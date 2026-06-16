"""Pure rendering for ``densa tui``.

Everything here is a pure function of the view-model plus the terminal
dimensions: ``render`` turns an :class:`densa.tui.model.AppState` into
exactly ``height`` strings, each at most ``width`` columns wide. No
``curses`` import, no I/O, no clock — which is what lets the
render-shape contract be proven by property tests
(``_system/tests/test_tui_view.py``) without a terminal.

Two deliberate boundaries keep purity intact:

* **Excerpt file reads happen in the driver, not here.** ``render``
  accepts already-read ``excerpt_lines``; the disk read is the
  driver's job.
* **Only single-column characters are emitted.** The display-width
  contract (``len(row) <= width``) is only honest if one code point
  paints one column, so the renderer avoids emoji / wide glyphs and
  uses ASCII markers (``E``/``W``/``>``/``[RO]``). Truncation is by
  ``len()``, which bounds the *buffer* but not painted columns: a wide
  glyph (CJK / emoji) in a message would over-paint and could wrap or
  overflow the line visually even while ``len(row) <= width`` holds.
  Validator messages are effectively ASCII, so this is a documented
  limitation, not a live failure mode.
"""

from __future__ import annotations

from densa.report import Diagnostic, Severity
from densa.tui.model import AppState
from densa.tui.noise import is_known_noise

MIN_WIDTH = 20
MIN_HEIGHT = 5


def too_small(width: int, height: int) -> bool:
    """True when the terminal cannot host the viewer chrome."""
    return width < MIN_WIDTH or height < MIN_HEIGHT


def scroll_window(cursor: int, total: int, rows: int) -> tuple[int, int]:
    """Return the ``[start, end)`` slice of a ``total``-long list to show
    in ``rows`` lines, keeping ``cursor`` visible.

    Contract
    --------
    pre  : ``rows >= 1``; ``total >= 0``; ``0 <= cursor < total`` when
           ``total > 0`` (``cursor`` ignored when ``total == 0``).
    post : ``0 <= start <= end <= total``; ``end - start <= rows``; and
           when ``total > 0`` the window contains the cursor
           (``start <= cursor < end``).
    """
    if total <= rows:
        return (0, total)
    half = rows // 2
    start = max(0, min(cursor - half, total - rows))
    return (start, start + rows)


def _fit(text: str, width: int) -> str:
    """Truncate (with an ellipsis) or left-pad *text* to exactly *width*.

    Defensive at ``width <= 0`` (returns ``""``) so the row buffer can
    never exceed the requested width even for out-of-contract dims.
    """
    if width <= 0:
        return ""
    if len(text) > width:
        if width == 1:
            return text[:1]
        return text[: width - 1] + "…"  # … is single-column
    return text.ljust(width)


def _sev_marker(severity: Severity) -> str:
    return "E" if severity is Severity.ERROR else "W"


def _finding_row(diag: Diagnostic, selected: bool, width: int) -> str:
    cursor = ">" if selected else " "
    loc = f"{diag.path}:{diag.line}" if diag.line > 0 else diag.path
    noise = " [RO]" if is_known_noise(diag.path) else ""
    body = f"{cursor}{_sev_marker(diag.severity)} {diag.rule_id} {loc}{noise}  {diag.message}"
    return _fit(body, width)


def _header(state: AppState, width: int) -> str:
    vis = state.visible()
    pos = f"{state.cursor + 1}/{len(vis)}" if vis else "0/0"
    flt = state.severity_filter.value
    rule = state.rule_filter or "all-rules"
    muted = f"{state.muted_count} muted" if state.mute_noise else "noise shown"
    return _fit(f" DENSA diagnostics  {pos}  [{flt}|{rule}]  {muted}", width)


def _status(width: int) -> str:
    return _fit(
        " j/k move  s sev  f rule  m mute  enter excerpt  r rerun  q quit",
        width,
    )


def render_excerpt_pane(
    diag: Diagnostic | None,
    excerpt_lines: list[str] | None,
    rows: int,
    width: int,
) -> list[str]:
    """Render the excerpt pane body (``rows`` lines). Pure.

    *excerpt_lines* is the file's lines as already read by the driver
    (``None`` when unread/unreadable). The selected ``diag`` supplies
    the focus line.
    """
    if rows <= 0:
        return []
    out: list[str] = []
    if diag is None:
        out.append(_fit(" (no selection)", width))
    elif diag.line <= 0:
        out.append(_fit(f" {diag.path}: (whole-file finding — no line)", width))
    elif excerpt_lines is None:
        out.append(_fit(f" {diag.path}: (unreadable)", width))
    else:
        body_rows = rows - 1
        win_start, win_end = scroll_window(
            diag.line - 1, len(excerpt_lines), max(1, body_rows)
        )
        out.append(_fit(f" {diag.path}:{diag.line}", width))
        for i in range(win_start, win_end):
            marker = ">" if (i + 1) == diag.line else " "
            out.append(_fit(f"{marker}{i + 1:>5} {excerpt_lines[i]}", width))
    return (out + [_fit("", width)] * rows)[:rows]


def render(
    state: AppState,
    width: int,
    height: int,
    excerpt_lines: list[str] | None = None,
) -> list[str]:
    """Render the whole screen to exactly *height* rows of <= *width*.

    Contract
    --------
    pre  : (none — degrades gracefully on any positive dims).
    post : ``len(result) == height``; ``all(len(r) <= width)``; pure;
           never raises.
    """
    if too_small(width, height):
        msg = _fit("terminal too small (need >=20x5)", width)
        return ([msg] + [_fit("", width)] * height)[:height]

    vis = state.visible()
    body_rows = height - 2  # header + status

    # Split the body when an excerpt is open.
    if state.excerpt_open and vis:
        excerpt_rows = min(body_rows // 2, max(1, body_rows - 1))
        list_rows = body_rows - excerpt_rows - 1  # 1 separator row
    else:
        excerpt_rows = 0
        list_rows = body_rows

    rows: list[str] = [_header(state, width)]

    if not vis:
        note = (
            "No findings"
            if not state.all
            else f"0 of {len(state.all)} shown (filtered/muted)"
        )
        blanks = body_rows
        mid = blanks // 2
        for r in range(blanks):
            rows.append(_fit(f"  {note}" if r == mid else "", width))
    else:
        start, end = scroll_window(state.cursor, len(vis), max(1, list_rows))
        shown = 0
        for i in range(start, end):
            rows.append(_finding_row(vis[i], i == state.cursor, width))
            shown += 1
        while shown < list_rows:
            rows.append(_fit("", width))
            shown += 1
        if excerpt_rows > 0:
            rows.append(_fit("-" * width, width))
            rows.extend(
                render_excerpt_pane(
                    state.selected(), excerpt_lines, excerpt_rows, width
                )
            )

    rows.append(_status(width))
    # Defensive: pin to exactly height (should already hold by construction).
    return (rows + [_fit("", width)] * height)[:height]
