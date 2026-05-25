---
type: analysis
domain: psychology
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: ["[[<raw-psychiatry-session-wikilink>]]"]
aliases: []
session_kind: psychiatry
participants: [self, <psychiatrist-slug>]
analysis_lens: [biopsychosocial-4P, diagnostic-differential]
diagnostic_signals: []
tags: [psychiatry, medication]
status: active
compiled_against: 1
---

# <% tp.file.title %>

<!-- Single-file v3 analysis of ONE psychiatry session.
The clinical lens is DSM-5 + pharmacology, NOT psychodynamic process.
If process material surfaces during a psychiatry session, defer it to the
next therapy analysis (with [[<therapist-slug>]]) — DO NOT process it here.
This boundary keeps the medication arc clean and prevents cross-clinical leak.
See domains/psychology/AGENTS.md §"Biopsychosocial 4P framing" + §7 risks. -->

## TL;DR

1-3 sentences. Symptom snapshot + any medication change + key clinical observation.

## Key moments

<!-- 2-4 bullets. Psychiatry sessions are usually shorter and more structured than therapy. -->

- [HH:MM] short description — touches [[<concept>]] / [[medication-arc]]

## Narrative reconstruction (~300-500 字)

<!-- Briefer than therapy. Focus on observation and dialogue, not interpretation. -->

…

## 症状评估

### 主诉

<!-- Each symptom anchored to a raw timestamp; do NOT add symptoms not stated. -->

- <symptom> — raw [HH:MM]

### 量表（如本次跑了；空表也保留以示未跑）

| Scale | This session | Last session | Δ | Clinically significant (≥5)? |
| --- | --- | --- | --- | --- |
| PHQ-9 | … | … | … | … |
| GAD-7 | … | … | … | … |
| ASRS | … | … | … | … |

### biopsychosocial 4P (only fill cells with new material)

- **Predisposing**：<long-standing factors — ADHD, ASD evaluation, schema legacies>
- **Precipitating**：<proximal trigger this week>
- **Perpetuating**：<what keeps the loop going>
- **Protective**：<what's working — supports, prior interventions, current routines>

## 用药记录

### 当前方案

<!-- List every active medication with dose + start date + change this session. -->

- <drug>: <dose>, started <YYYY-MM-DD>, **this session**: <new dose | unchanged | discontinued>

### 副作用 / 主观体验

<!-- Each observation tagged whether attributed to medication, situation, or unclear. -->

- <observation> — attribution: <medication | situational | unclear>

### 医生 plan

- <next f/u date, dose targets, scale assignments, lab orders, referrals>

## Wiki side-effects

- Concept: [[depression]] / [[anxiety]] / [[adhd]] / [[possible-asd-features]] +1 instance (only those that surfaced this session)
- Protocol: [[medication-arc]] timeline **+1 entry** (always — even when no medication change, log "no change" for continuity)
- Entity: [[<psychiatrist-slug>]] Appearances +1
- (No pattern/theme updates expected. If pattern material surfaced, log it in "Open threads" for next therapy session, NOT here.)

## Open threads

<!-- Material to bring to therapy or follow up at next psychiatry session. -->

- 带到下次精神科：<follow-up data>
- 带到下次治疗（[[<therapist-slug>]]）：<process material that surfaced but wasn't worked through here>

## Pages NOT touched but should be (carry-over)

- …
