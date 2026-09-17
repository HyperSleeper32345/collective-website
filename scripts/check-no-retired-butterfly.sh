#!/usr/bin/env bash
# Fails if the retired butterfly mark's path data (brand system section 10.6,
# byte-identical across the three files it was found shipping in) is present
# in the served site. Retired marks are removed everywhere with a build guard.
set -euo pipefail

cd "$(dirname "$0")/.."

DISCRIMINATOR='M 470 348 C 410 340, 350 330, 255 345 C 280 380, 380 388, 470 365 Z'

# index.html's hero emblem draws the same retired geometry inside a bespoke,
# hand-tuned wing/venation/scan animation (styles.css .fw-l/.fw-r/.hw-l/.hw-r
# etc). Replacing it means redesigning that animation against the correct
# mark, which is a brand-sign-off decision, not a file swap, so it is tracked
# on its own row rather than silently allowed here.
hits=""
while IFS= read -r -d '' f; do
  case "$f" in
    ./index.html) continue ;;
  esac
  if grep -qF "$DISCRIMINATOR" "$f"; then
    hits="$hits$f"$'\n'
  fi
done < <(find . \( -path ./.git -o -path ./node_modules -o -path ./.worktrees -o -path ./scripts -o -path ./.github \) -prune -o \
  \( -name '*.html' -o -name '*.svg' -o -name '*.css' -o -name '*.js' -o -name '*.webmanifest' \) -type f -print0)

if [ -n "$hits" ]; then
  echo "Retired butterfly mark path data found in:" >&2
  echo "$hits" >&2
  exit 1
fi

echo "No retired butterfly path data found."
