#!/usr/bin/env python3
"""Scan a LaTeX paper project before converting it to the Midori preprint template.

Usage: python3 scan_source.py <project_dir> [--entry main.tex]

Prints a Markdown report: entry file and \\input tree, document class and venue
style, packages (flagging ones that clash with preprint.sty or must be removed),
citation usage, bibliography setup, research-paper-style (\\rps...) usage,
negative spacing, wrap floats, two-column signs, macro definitions that wrap a
font switch in \\textbf, \\hypersetup, the raw author block, and checklist files.
Read-only: it never modifies the project.
"""
import argparse
import os
import re
import sys
from collections import Counter, OrderedDict

VENUE_PATTERNS = [
    (r"neurips_\d+|nips_\d+", "NeurIPS"),
    (r"iclr\d+_conference", "ICLR"),
    (r"colm\d+_conference", "COLM"),
    (r"icml\d+", "ICML"),
    (r"^acl$|acl_natbib|emnlp|naacl", "ACL/*CL"),
    (r"^cvpr|^iccv|^wacv", "CVPR/ICCV"),
    (r"aaai\d+", "AAAI"),
    (r"ijcai\d+", "IJCAI"),
]
# Packages preprint.sty already loads: re-loading with options causes clashes.
TEMPLATE_PKGS = {"fontenc", "tgpagella", "mathpazo", "inconsolata", "montserrat",
                 "graphicx", "xcolor", "array", "tabularx", "booktabs", "fancyhdr",
                 "natbib", "etoolbox", "caption"}
# Options identical to what preprint.sty passes are harmless.
TEMPLATE_SAME_OPTS = {("fontenc", "T1"), ("xcolor", "table")}
# Loaded immediately only without [nowritingstyle]; tcolorbox is otherwise
# loaded at the end of the preamble, after the paper's own \usepackage.
DEFAULT_MODE_PKGS = {"enumitem", "pifont", "tcolorbox"}
REMOVE_PKGS = {"times", "mathptmx", "newtxtext", "newtxmath", "newtx", "txfonts",
               "helvet", "courier", "lmodern", "geometry", "fullpage", "lineno",
               "titlesec", "palatino", "mathpazo", "fourier", "libertine", "nimbusserif"}
CHECKLIST_HINTS = ("checklist", "reproducibility_checklist", "responsible")
# Text width (inches) of common venue styles, and whether they are two-column.
VENUE_WIDTH = {"NeurIPS": (5.5, False), "ICLR": (5.5, False), "COLM": (5.5, False),
               "ICML": (6.75, True), "ACL/*CL": (6.3, True), "CVPR/ICCV": (6.875, True),
               "AAAI": (7.0, True), "IJCAI": (7.0, True)}
UNIT = {"in": 1.0, "cm": 1 / 2.54, "mm": 1 / 25.4, "pt": 1 / 72.27, "bp": 1 / 72.0}


def to_in(v):
    m = re.match(r"\s*([\d.]+)\s*(?:true\s*)?(in|cm|mm|pt|bp)", v)
    return float(m.group(1)) * UNIT[m.group(2)] if m else None


def estimate_width(code):
    """Text width from geometry options or \\textwidth settings, in inches."""
    paper = 8.27 if "a4paper" in code else 8.5
    for m in re.finditer(r"\\(?:usepackage|RequirePackage|geometry)(?:\[([^\]]*)\])?(?:\{geometry\})?\{?([^}]*)\}?", code):
        opts = (m.group(1) or "") + "," + (m.group(2) or "")
        if "geometry" not in m.group(0):
            continue
        kv = dict(re.findall(r"(\w+)\s*=\s*([\d.]+\s*(?:in|cm|mm|pt|bp))", opts))
        if "textwidth" in kv:
            return to_in(kv["textwidth"])
        left = to_in(kv.get("left", kv.get("lmargin", kv.get("hmargin", kv.get("margin", "")))) or "")
        right = to_in(kv.get("right", kv.get("rmargin", kv.get("hmargin", kv.get("margin", "")))) or "")
        if left and right:
            return paper - left - right
    m = re.search(r"\\(?:setlength\{\\textwidth\}\{|textwidth\s*=?\s*)([\d.]+\s*(?:true\s*)?(?:in|cm|mm|pt|bp))", code)
    return to_in(m.group(1)) if m else None


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[: m.start()] if m else line)
    return "\n".join(out)


def find_entry(root):
    cands = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".tex"):
                p = os.path.join(dirpath, f)
                try:
                    t = strip_comments(open(p, errors="ignore").read())
                except OSError:
                    continue
                if "\\documentclass" in t and "\\begin{document}" in t:
                    cands.append(p)
    cands.sort(key=lambda p: (os.path.basename(p) not in ("main.tex", "paper.tex"), len(p)))
    return cands


def resolve(root, base_dir, name):
    for cand in (name, name + ".tex"):
        for d in (base_dir, root):
            p = os.path.normpath(os.path.join(d, cand))
            if os.path.isfile(p):
                return p
    return None


def walk_inputs(root, entry, seen=None, depth=0, tree=None):
    seen = seen if seen is not None else OrderedDict()
    tree = tree if tree is not None else []
    if entry in seen:
        return seen, tree
    text = open(entry, errors="ignore").read()
    seen[entry] = text
    tree.append("  " * depth + os.path.relpath(entry, root))
    for m in re.finditer(r"\\(?:input|include|subfile)\{([^}]+)\}", strip_comments(text)):
        p = resolve(root, os.path.dirname(entry), m.group(1).strip())
        if p:
            walk_inputs(root, p, seen, depth + 1, tree)
        else:
            tree.append("  " * (depth + 1) + m.group(1) + "  (NOT FOUND)")
    return seen, tree


def lines_matching(files, root, pattern, flags=0):
    hits = []
    for path, text in files.items():
        for i, line in enumerate(text.split("\n"), 1):
            code = strip_comments(line)
            if re.search(pattern, code, flags):
                hits.append(f"{os.path.relpath(path, root)}:{i}: {line.strip()[:140]}")
    return hits


def balanced_arg(text, start):
    """Return the {...} group starting at text[start] == '{'."""
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{" and text[i - 1] != "\\":
            depth += 1
        elif c == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1: i]
    return text[start + 1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--entry")
    a = ap.parse_args()
    root = os.path.abspath(a.project)
    entries = [os.path.join(root, a.entry)] if a.entry else find_entry(root)
    if not entries:
        sys.exit("No .tex file with \\documentclass and \\begin{document} found.")
    entry = entries[0]
    files, tree = walk_inputs(root, entry)
    main_text = strip_comments(files[entry])
    pre = main_text.split("\\begin{document}")[0]
    all_code = {p: strip_comments(t) for p, t in files.items()}
    body_code = "\n".join(all_code.values())

    print(f"# Source scan: {os.path.relpath(entry, root)}\n")
    if len(entries) > 1:
        print("Other candidate entry files: " + ", ".join(os.path.relpath(e, root) for e in entries[1:]) + "\n")
    print("## \\input tree\n```\n" + "\n".join(tree) + "\n```\n")

    m = re.search(r"\\documentclass(\[[^\]]*\])?\{([^}]+)\}", pre)
    cls_opts, cls = (m.group(1) or "", m.group(2)) if m else ("", "?")
    local_cls = os.path.isfile(os.path.join(root, cls + ".cls"))
    print(f"## Document class\n- `\\documentclass{cls_opts}{{{cls}}}`" + (" (local .cls file: read it to map its commands)" if local_cls else ""))
    if "twocolumn" in cls_opts:
        print("- two-column class option")

    pkgs = re.findall(r"\\(?:usepackage|RequirePackage)(\[[^\]]*\])?\{([^}]+)\}", pre)
    venue = []
    print("\n## Packages")
    rows = []
    for opts, names in pkgs:
        for name in [n.strip() for n in names.split(",")]:
            note = ""
            for pat, label in VENUE_PATTERNS:
                if re.search(pat, name):
                    note = f"VENUE STYLE ({label}): remove"
                    venue.append(label)
            if not note and name in REMOVE_PKGS:
                note = "page/font package of the old template: remove"
            elif not note and name in TEMPLATE_PKGS and opts and \
                    (name, opts.strip("[] ")) in TEMPLATE_SAME_OPTS:
                note = "same option as preprint.sty: harmless, can stay"
            elif not note and name in TEMPLATE_PKGS and opts:
                note = "loaded by preprint.sty: move options to \\PassOptionsToPackage before it (see guide §3)"
            elif not note and name in DEFAULT_MODE_PKGS and opts:
                note = "fine with [nowritingstyle]; in default mode use \\PassOptionsToPackage / \\tcbuselibrary (guide §3)"
            elif not note and name == "biblatex":
                note = "use [nonatbib]"
            elif not note and name == "enumerate":
                note = "overrides enumitem in default mode"
            elif not note and name == "ulem":
                note = "add \\normalem"
            rows.append(f"- `{name}`{(' ' + opts) if opts else ''}" + (f" — **{note}**" if note else ""))
    print("\n".join(rows))
    if os.path.isfile(os.path.join(root, cls + ".cls")):
        pass
    if local_cls:
        cls_code = strip_comments(open(os.path.join(root, cls + ".cls"), errors="ignore").read())
        cls_pkgs = re.findall(r"\\(?:usepackage|RequirePackage)(\[[^\]]*\])?\{([^}]+)\}", cls_code)
        print("\nPackages loaded by the local class (they disappear when the class is replaced;"
              " keep the ones the body still needs, and their citation options):")
        for opts, names in cls_pkgs:
            print(f"- `{names}`{(' ' + opts) if opts else ''}")
        nat = [o for o, n in cls_pkgs if "natbib" in n and o]
        if nat:
            print(f"- class loads natbib with {nat[0]} → keep that citation mode")
    width_code = pre + ("\n" + strip_comments(open(os.path.join(root, cls + ".cls"), errors="ignore").read()) if local_cls else "")
    for _, names in pkgs:  # project-local style files (e.g. a renamed venue .sty)
        for name in names.split(","):
            sty = os.path.join(root, name.strip() + ".sty")
            if os.path.isfile(sty):
                width_code += "\n" + strip_comments(open(sty, errors="ignore").read())
    est = estimate_width(width_code)
    two_col = "twocolumn" in cls_opts
    for label in venue:
        if label in VENUE_WIDTH and est is None:
            est, two_col = VENUE_WIDTH[label][0], VENUE_WIDTH[label][1] or two_col
    print("\n## Text width")
    if est:
        print(f"- source text width ≈ {est:.2f}in ({'two-column' if two_col else 'single-column'}); template default 5.5in, [wide] 6.5in")
        full = len(re.findall(r"\\resizebox\{\\textwidth\}|width=\\textwidth|width=\\linewidth", body_code))
        if not two_col and est >= 6.2:
            print(f"- single-column source at ~6.5in → use [wide] so full-width figures/tables ({full} found) keep their size")
        elif two_col:
            print("- two-column source: keep the default width; see guide §7 for column-width figures")
        else:
            print("- matches the default 5.5in column")
    else:
        print("- could not estimate (no geometry/venue info): compare a rendered page of the original with the template")
    print("\nVenue detected: " + (", ".join(sorted(set(venue))) if venue else "none from packages (check the class)"))

    print("\n## Citations and bibliography")
    c = Counter()
    for k in ("cite", "citep", "citet", "citealp", "citeauthor", "citeyear", "parencite", "textcite", "autocite"):
        c[k] = len(re.findall(r"\\" + k + r"\*?(\[[^\]]*\])*\{", body_code))
    print("- usage: " + ", ".join(f"\\{k}: {v}" for k, v in c.items() if v))
    for pat in (r"\\PassOptionsToPackage\{[^}]*\}\{natbib\}", r"\\bibliographystyle\{[^}]+\}",
                r"\\bibliography\{[^}]+\}", r"\\addbibresource\{[^}]+\}", r"\\setcitestyle\{[^}]+\}"):
        for hit in re.findall(pat, body_code):
            print(f"- `{hit}`")
    if c["cite"] > 3 * (c["citep"] + c["citet"] + 1):
        print("- mostly bare \\cite: keep NUMERIC citations (author-year would print bare names)")

    rps = sorted(set(re.findall(r"\\rps[A-Z][A-Za-z]*", body_code)))
    print("\n## research-paper-style layer")
    if rps:
        print("- uses: " + ", ".join(rps) + " → load preprint WITHOUT nowritingstyle; copy researchpaperstyle.sty")
    else:
        print("- no \\rps... macros → use \\usepackage[nowritingstyle]{preprint}")

    print("\n## Layout hazards")
    neg = lines_matching(files, root, r"\\v(space|skip)\*?\s*\{?\s*-")
    print(f"- negative vertical spacing ({len(neg)}):")
    for h in neg:
        print("  - " + h)
    wraps = lines_matching(files, root, r"\\begin\{wrap(figure|table)\}")
    print(f"- wrap floats ({len(wraps)}):")
    for h in wraps:
        print("  - " + h)
    star = len(re.findall(r"\\begin\{(figure|table)\*\}", body_code))
    colw = len(re.findall(r"\\columnwidth", body_code))
    print(f"- figure*/table*: {star}; \\columnwidth uses: {colw}")
    resize = lines_matching(files, root, r"\\resizebox\{\\columnwidth\}")
    for h in resize:
        print("  - resizebox to columnwidth: " + h)

    print("\n## Macro definitions to check (\\textbf around a font switch)")
    found = False
    for path, code in all_code.items():
        for mm in re.finditer(r"\\(?:newcommand|renewcommand|def)\s*\{?\\([A-Za-z@]+)\}?[^\n]*", code):
            line = mm.group(0)
            if "\\textbf" in line and re.search(r"\\fontfamily|\\ttfamily|\\scshape|\\sffamily|\\texttt|\\textsc", line):
                print(f"- {os.path.relpath(path, root)}: `{line.strip()[:160]}` → use \\bfseries inside")
                found = True
    if not found:
        print("- none")

    print("\n## Other preamble items")
    for pat, label in ((r"\\hypersetup", "\\hypersetup (drop colour keys)"),
                       (r"\\(iclr|acl|cvpr|nips|icml)finalcopy|\\workshoptitle|\\cvprPaperID|\\confName|\\linenumbers|\\pdfinfo",
                        "venue switch/command (remove)"),
                       (r"\\icml(title|author|affiliation|correspondingauthor|keywords)|\\printAffiliationsAndNotice",
                        "ICML front-matter command (map to \\author/\\affiliation)"),
                       (r"\\twocolumn\[", "\\twocolumn[...] wrapper (remove)")):
        hits = lines_matching(files, root, pat)
        if hits:
            print(f"- {label}:")
            for h in hits[:12]:
                print("  - " + h)

    print("\n## Front matter (raw)")
    for cmd in ("title", "author"):
        idx = pre.find("\\" + cmd)
        while idx != -1 and pre[idx + len(cmd) + 1].isalpha():
            idx = pre.find("\\" + cmd, idx + 1)
        if idx != -1:
            j = idx + len(cmd) + 1
            while j < len(pre) and pre[j] in " \t\n[":
                if pre[j] == "[":
                    j = pre.find("]", j) + 1
                else:
                    j += 1
            if j < len(pre) and pre[j] == "{":
                print(f"### \\{cmd}\n```latex\n{balanced_arg(pre, j).strip()}\n```")
    multi = re.findall(r"\\author\[[^\]]*\]\{[^}]*\}", pre)
    if multi:
        print("- keyed \\author[...] commands already present: " + str(len(multi)))
    for kw in ("thanks", "footnotemark", "email", "affiliation", "institute", "And", "AND"):
        n = len(re.findall(r"\\" + kw + r"\b", pre))
        if n:
            print(f"- \\{kw}: {n}")
    abs_files = [os.path.relpath(p, root) for p, t in all_code.items() if "\\begin{abstract}" in t]
    abs_cmd = bool(re.search(r"\\abstract\{", pre))
    print(f"- abstract environment in: {', '.join(abs_files) or 'not found'}" + ("; \\abstract{...} command in preamble" if abs_cmd else ""))
    urls = re.findall(r"\\url\{(https?://[^}]*(?:github|gitlab|huggingface|anonymous)[^}]*)\}", body_code)
    if urls:
        print("- code/data links: " + ", ".join(sorted(set(urls))))

    own_app = lines_matching(files, root, r"\\section\*?\s*\{\s*Appendix|\\beginappendix|\\appendixpage")
    if own_app:
        print("\n## Own appendix title (the template adds \"Appendix\" automatically: comment these out)")
        for h in own_app:
            print("- " + h)
    toc = lines_matching(files, root, r"\\tableofcontents")
    if toc:
        print("\n## Table of contents in the source (keep it, or use the [toc] option)")
        for h in toc:
            print("- " + h)
    print("\n## Venue paperwork / special inputs")
    for p in files:
        rel = os.path.relpath(p, root)
        if any(h in rel.lower() for h in CHECKLIST_HINTS):
            print(f"- {rel} (venue checklist? do not \\input in the preprint)")
    if "\\appendix" in body_code:
        print("- has \\appendix")


if __name__ == "__main__":
    main()
