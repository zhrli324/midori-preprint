#!/usr/bin/env python3
"""Check that a template conversion left the paper's text untouched.

Usage: python3 text_diff.py <original_project> <converted_project> [--entry main.tex]

For every .tex file present in both projects (same relative path), and for the
body (\\begin{document}..\\end{document}) of the entry file, compare the
sequence of words and numbers after removing comments, \\begin/\\end
environment names and command names. Layout-only edits (commented-out spacing,
wrapfigure -> figure, `aligned` around an equation) leave this sequence
unchanged or nearly so; reworded sentences, moved links, changed numbers or
renamed colours show up as differences.

Exit code 0 = identical, 1 = differences found (each printed with context).
"""
import argparse
import difflib
import os
import re
import sys

TOKEN = re.compile(r"[A-Za-z]{2,}|\d+(?:\.\d+)?")


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[: m.start()] if m else line)
    return "\n".join(out)


# Pure layout arguments: spacing, float placement/size, graphics/box scaling.
LAYOUT = [
    r"\\[vh](?:space|skip)\*?\s*\{[^}]*\}",
    r"\\vskip\s*-?[\d.]+\s*[a-z]{2}",
    r"\\begin\{wrap(?:figure|table)\}(?:\[[^\]]*\])?\{[^}]*\}\{[^}]*\}",
    r"\\begin\{(?:figure|table)\*?\}\s*\[[^\]]*\]",
    r"\\includegraphics\s*\[[^\]]*\]",
    r"\\resizebox\s*\{[^}]*\}\s*\{[^}]*\}",
    # template-domain commands in the document body
    r"\\bibliographystyle\s*\{[^}]*\}",
    r"\\(?:this)?pagestyle\s*\{[^}]*\}",
]


def tokens(text):
    t = strip_comments(text)
    for pat in LAYOUT:
        t = re.sub(pat, " ", t)
    t = re.sub(r"\\(begin|end)\s*\{[^}]*\}", " ", t)
    t = re.sub(r"\\[A-Za-z@]+\*?", " ", t)
    return TOKEN.findall(t)


def body(text):
    t = strip_comments(text)  # a commented-out \begin{document} must not count
    if "\\begin{document}" in t:
        t = t.split("\\begin{document}", 1)[1]
    if "\\end{document}" in t:
        t = t.split("\\end{document}", 1)[0]
    return t


def compare(name, a, b, ctx=6):
    ta, tb = tokens(a), tokens(b)
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    diffs = [op for op in sm.get_opcodes() if op[0] != "equal"]
    if not diffs:
        return 0
    print(f"\n### {name}: {len(diffs)} difference(s)")
    for tag, i1, i2, j1, j2 in diffs:
        before = " ".join(ta[max(0, i1 - ctx): i1])
        print(f"- {tag}: …{before} [[ {' '.join(ta[i1:i2]) or '∅'} → {' '.join(tb[j1:j2]) or '∅'} ]] …")
    return len(diffs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("converted")
    ap.add_argument("--entry", default="main.tex")
    ap.add_argument("--converted-entry", help="entry file name in the converted project (default: same)")
    a = ap.parse_args()
    orig, conv = os.path.abspath(a.original), os.path.abspath(a.converted)
    total = 0

    oe, ce = os.path.join(orig, a.entry), os.path.join(conv, a.converted_entry or a.entry)
    if os.path.isfile(oe) and os.path.isfile(ce):
        total += compare(f"{a.entry} (document body)", body(open(oe, errors="ignore").read()),
                         body(open(ce, errors="ignore").read()))

    skip_dirs = {os.path.relpath(conv, orig)} if conv.startswith(orig + os.sep) else set()
    compared = 0
    for dirpath, dirnames, files in os.walk(orig):
        rel_dir = os.path.relpath(dirpath, orig)
        dirnames[:] = [d for d in dirnames if os.path.normpath(os.path.join(rel_dir, d)) not in skip_dirs]
        for f in files:
            if not f.endswith(".tex"):
                continue
            rel = os.path.normpath(os.path.join(rel_dir, f))
            if rel == os.path.normpath(a.entry):
                continue
            cp = os.path.join(conv, rel)
            if not os.path.isfile(cp):
                print(f"- not in converted project: {rel}")
                continue
            compared += 1
            total += compare(rel, open(os.path.join(dirpath, f), errors="ignore").read(),
                             open(cp, errors="ignore").read())
    print(f"\nCompared the entry body and {compared} other .tex file(s): "
          + ("no text differences." if total == 0 else f"{total} difference(s) — each must be a layout-only edit or be reverted."))
    sys.exit(0 if total == 0 else 1)


if __name__ == "__main__":
    main()
