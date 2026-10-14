#!/bin/sh
# Copy the template (template/) into the skill's bundled assets
# (skill/midori-preprint/assets/), so both always ship the same files.
#
#   tools/sync-skill-assets.sh          copy template -> skill assets
#   tools/sync-skill-assets.sh --check  only report differences (exit 1 if any)
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
T="$ROOT/template"
A="$ROOT/skill/midori-preprint/assets"
CHECK=${1:-}
STATUS=0

# source (in template/) : destination (in skill assets/)
for pair in \
  preprint.sty:template/preprint.sty \
  preprint.bst:template/preprint.bst \
  researchpaperstyle.sty:template/researchpaperstyle.sty \
  figures/ntu-logo.pdf:template/logos/ntu-logo.pdf \
  figures/midori-icon.png:template/logos/midori-icon.png \
  figures/midori-wordmark.png:template/logos/midori-wordmark.png \
  figures/midori-logo.png:template/logos/midori-logo.png \
  references.bib:example/references.bib \
  math_commands.tex:example/math_commands.tex
do
  src="$T/${pair%%:*}"; dst="$A/${pair#*:}"
  if [ "$CHECK" = "--check" ]; then
    cmp -s "$src" "$dst" || { echo "differs: template/${pair%%:*} vs skill assets/${pair#*:}"; STATUS=1; }
  else
    mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"
  fi
done

# The example main.tex refers to logos/ inside the skill instead of figures/.
tmp=$(mktemp)
sed -e 's#{figures/ntu-logo}#{logos/ntu-logo}#g' -e 's#{figures/midori-#{logos/midori-#g' "$T/main.tex" > "$tmp"
if [ "$CHECK" = "--check" ]; then
  cmp -s "$tmp" "$A/example/main.tex" || { echo "differs: template/main.tex vs skill assets/example/main.tex"; STATUS=1; }
else
  cp "$tmp" "$A/example/main.tex"
fi
rm -f "$tmp"

if [ "$CHECK" = "--check" ] && [ $STATUS -eq 0 ]; then
  echo "skill assets are in sync with template/"
fi
exit $STATUS
