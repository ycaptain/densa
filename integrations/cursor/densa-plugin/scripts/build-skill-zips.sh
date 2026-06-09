#!/usr/bin/env bash
# Build per-operation zip bundles of the five SKILL.md files,
# ready to upload to skills.sh / agentskills.io / Claude Code's
# Settings > Capabilities > Skills.
#
# Usage:
#   bash integrations/cursor/densa-plugin/scripts/build-skill-zips.sh [output-dir]
#
# Default output-dir is outputs/skill-bundles/.  Each zip contains
# one skill directory rooted at the skill name (so it unpacks as
# `~/.cursor/skills/densa-<op>/SKILL.md` or equivalent in Claude
# Code).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$PLUGIN_DIR/skills"
REPO_ROOT="$(cd "$PLUGIN_DIR/../../.." && pwd)"

OUTPUT_DIR="${1:-$REPO_ROOT/outputs/skill-bundles}"
mkdir -p "$OUTPUT_DIR"

OPS=(ingest query lint process-inbox promote)

echo "Building skill bundles -> $OUTPUT_DIR"

for op in "${OPS[@]}"; do
    src="$SKILLS_DIR/$op"
    if [[ ! -d "$src" ]]; then
        echo "  skip: $src not found" >&2
        continue
    fi

    bundle_name="densa-$op"
    work_dir="$(mktemp -d)"
    cp -R "$src" "$work_dir/$bundle_name"

    zip_path="$OUTPUT_DIR/$bundle_name.zip"
    rm -f "$zip_path"
    (cd "$work_dir" && zip -rq "$zip_path" "$bundle_name")
    rm -rf "$work_dir"

    size_kb=$(du -k "$zip_path" | awk '{print $1}')
    echo "  built: $bundle_name.zip (${size_kb} KB)"
done

echo
echo "Done. Next steps:"
echo "  1. Verify each zip: unzip -l $OUTPUT_DIR/densa-<op>.zip"
echo "  2. Submit per the maintainers' submission checklist"
echo "     (skills.sh / agentskills.io / Cursor marketplace / Claude Code Skills)"
