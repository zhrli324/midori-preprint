# Midori preprint: LaTeX template + Claude skill
#
#   make preview   compile template/main.tex in all variants into template/preview/
#   make sync      copy template files into the skill's assets
#   make check     fail if the skill's assets differ from template/
#   make skill     package the skill as dist/midori-preprint.skill
#   make install   install the skill for Claude Code (~/.claude/skills/)
#   make clean     remove LaTeX build files

SKILL   := skill/midori-preprint
DIST    := dist/midori-preprint.skill
BUILD   := .build

.PHONY: preview sync check skill install clean

preview:
	rm -rf $(BUILD) && mkdir -p $(BUILD) && cp -R template/. $(BUILD)/
	cd $(BUILD) && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null
	cd $(BUILD) && for o in monochrome wide; do \
	  sed "s/\\\\usepackage{preprint}/\\\\usepackage[$$o]{preprint}/" main.tex > $$o.tex && \
	  latexmk -pdf -interaction=nonstopmode -halt-on-error $$o.tex >/dev/null; done
	cp $(BUILD)/main.pdf template/preview/preview.pdf
	cp $(BUILD)/monochrome.pdf template/preview/preview-monochrome.pdf
	cp $(BUILD)/wide.pdf template/preview/preview-wide.pdf
	rm -rf $(BUILD)

sync:
	sh tools/sync-skill-assets.sh

check:
	sh tools/sync-skill-assets.sh --check

skill: check
	mkdir -p dist && rm -f $(DIST)
	cd skill && zip -qr -X ../$(DIST) midori-preprint -x '*/__pycache__/*' '*.DS_Store'
	@echo "packaged $(DIST)"

install: check
	mkdir -p $(HOME)/.claude/skills
	rm -rf $(HOME)/.claude/skills/midori-preprint
	cp -R $(SKILL) $(HOME)/.claude/skills/midori-preprint
	@echo "installed to ~/.claude/skills/midori-preprint"

clean:
	rm -rf $(BUILD)
