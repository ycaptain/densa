#!/usr/bin/env bash
set -euo pipefail
# Idempotent helper to set up git-crypt for one or more sensitive
# `raw/` trees. List the L2s you want encrypted in ENCRYPT_PATHS below
# (one git-attributes glob per line). The script is safe to re-run.
#
# Usage: bash _system/scripts/setup_encryption.sh
# Prereq: brew install git-crypt gnupg; you have a GPG key.

# Edit this list to fit your vault. Each line is a git-attributes glob.
ENCRYPT_PATHS=(
  # "domains/psychology/raw/**"
  # "domains/<your-sensitive-domain>/raw/**"
)

if [ "${#ENCRYPT_PATHS[@]}" -eq 0 ]; then
  echo "No paths configured. Edit ENCRYPT_PATHS in this script first."
  exit 1
fi

if ! command -v git-crypt >/dev/null; then
  echo "git-crypt not found. Install with: brew install git-crypt"
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

GA=.gitattributes
touch "$GA"
for path in "${ENCRYPT_PATHS[@]}"; do
  LINE="$path filter=git-crypt diff=git-crypt"
  if ! grep -qF "$LINE" "$GA"; then
    echo "$LINE" >> "$GA"
    echo "Added .gitattributes pattern: $path"
  else
    echo ".gitattributes pattern already present: $path"
  fi
done

# 2. init guard
if [ ! -f .git-crypt/keys/default ]; then
  echo
  echo "Run next:  git-crypt init"
  echo "Then add your GPG identity:"
  echo "  git-crypt add-gpg-user <your@email>"
  echo "Then verify:  git-crypt status -e"
else
  echo "git-crypt already initialised (.git-crypt/keys/default exists)."
fi
