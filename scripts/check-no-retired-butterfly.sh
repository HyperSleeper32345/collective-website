#!/usr/bin/env bash
# Fails if the retired previous mark (the "butterfly") is present in the served
# site. Retired marks are removed everywhere with a build guard.
#
# The discriminators come from brand system section 10.6, which tells the two
# marks apart by measurement. The retired mark's six wing paths all open and
# close at the single point 200,200 on a 400-unit viewBox; the paths below are
# byte-identical across Collective-Dragonfly-Icon-Source.svg and both
# Collective_Logo_Icon_Transparent*_v1.svg files.
#
# The v1.4 dragonfly (collective-website-icon.svg, the SSOT mark) has four wings
# attached along x=470 and x=530, e.g. "M 470 348 C 410 340 ...". That is the
# CORRECT geometry and the homepage hero draws it, so it must never be used as a
# discriminator here. An earlier version of this script did exactly that and had
# to exclude index.html to pass; there are no exclusions now.
set -euo pipefail

cd "$(dirname "$0")/.."

DISCRIMINATORS=(
  'M200 200 C180 160,120 100,90 80'
  'M200 200 C185 175,140 130,110 115'
  'M200 200 C220 160,280 100,310 80'
)

hits=""
while IFS= read -r -d '' f; do
  for d in "${DISCRIMINATORS[@]}"; do
    if grep -qF "$d" "$f"; then
      hits="$hits$f"$'\n'
      break
    fi
  done
done < <(find . \( -path ./.git -o -path ./node_modules -o -path ./.worktrees -o -path ./.claude -o -path ./scripts -o -path ./.github \) -prune -o \
  \( -name '*.html' -o -name '*.svg' -o -name '*.css' -o -name '*.js' -o -name '*.webmanifest' \) -type f -print0)

if [ -n "$hits" ]; then
  echo "Retired butterfly mark path data found in:" >&2
  echo "$hits" >&2
  exit 1
fi

echo "No retired butterfly path data found."
