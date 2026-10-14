#!/usr/bin/env python3
"""Compile a converted project and summarise what needs attention.

Usage:
  python3 build_check.py <project_dir> [--entry main.tex] [--render 55]
                         [--zoom PAGE:DPI[:X,Y,W,H]] [--out DIR]

- Runs latexmk -pdf (pdfLaTeX) in the project directory, so main.bbl ends up
  there (arXiv needs it).
- Reports: errors (file:line), undefined references/citations, overfull boxes
  with the source file and lines, font-shape substitutions, page count.
- --render DPI renders every page to PNG (default output: a temp directory,
  printed at the end) for the page-by-page visual check.
- --zoom renders one page (optionally a crop in pixels at that DPI) for a
  close look at tables, equations or the title block. Repeatable.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter


def run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, errors="ignore")


def file_stack_events(log):
    """Yield (position, current_file) by tracking '(file' and ')' in the log."""
    # Every "(" is pushed (file names and ordinary parenthesised text such as
    # "(Font)" alike) so that the matching ")" pops the right entry.
    stack, events = [], []
    for m in re.finditer(r"\(([^\s()]*)|\)", log):
        if m.group(0) == ")":
            if stack:
                stack.pop()
        else:
            stack.append(m.group(1) or "")
        cur = next((f for f in reversed(stack) if f.endswith(".tex")), "?")
        events.append((m.start(), cur))
    return events


def file_at(events, pos):
    cur = "?"
    lo, hi = 0, len(events)
    while lo < hi:
        mid = (lo + hi) // 2
        if events[mid][0] <= pos:
            cur = events[mid][1]
            lo = mid + 1
        else:
            hi = mid
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--entry", default="main.tex")
    ap.add_argument("--render", type=int, default=0, help="DPI for rendering all pages (0 = off)")
    ap.add_argument("--zoom", action="append", default=[], help="PAGE:DPI[:X,Y,W,H]")
    ap.add_argument("--out", help="directory for PNG renders")
    ap.add_argument("--no-compile", action="store_true", help="only parse the existing log / render")
    ap.add_argument("--force", action="store_true",
                    help="latexmk -f: keep going past BibTeX errors that already exist in the original .bib")
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    base = os.path.splitext(a.entry)[0]
    env = dict(os.environ, max_print_line="10000", error_line="254", half_error_line="238")
    if not a.no_compile:
        cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-file-line-error"] + (["-f"] if a.force else [])
        r = run(cmd + [a.entry], proj, env)
        print(f"latexmk exit code: {r.returncode}")
        blg = os.path.join(proj, base + ".blg")
        if os.path.isfile(blg):
            nerr = re.search(r"\(There (?:were|was) (\d+) error", open(blg, errors="ignore").read())
            if nerr:
                print(f"BibTeX reported {nerr.group(1)} error(s) (see {base}.blg). If the original build has the same"
                      " errors, they come from the .bib: rerun with --force and list them in PREPRINT_NOTES.md.")
    log_path = os.path.join(proj, base + ".log")
    pdf_path = os.path.join(proj, base + ".pdf")
    if not os.path.isfile(log_path):
        sys.exit("No log file produced.")
    log = open(log_path, errors="ignore").read()
    events = file_stack_events(log)

    errors = re.findall(r"^(\S+\.tex:\d+: .*)$", log, re.M) + re.findall(r"^(! .*)$", log, re.M)
    print(f"\n## Errors ({len(errors)})")
    for e in dict.fromkeys(errors):
        print("- " + e[:200])

    undef = Counter(re.findall(r"(Reference|Citation) `([^']+)' on page \d+ undefined", log))
    print(f"\n## Undefined references/citations ({len(undef)})")
    for (kind, key), n in sorted(undef.items()):
        print(f"- {kind} `{key}` x{n}")

    print("\n## Overfull boxes")
    n_over = 0
    for m in re.finditer(r"Overfull \\([hv])box \(([\d.]+)pt too (?:wide|high)\) (?:in paragraph at lines (\d+)--(\d+)|detected at line (\d+)|has occurred while \\output is active)", log):
        n_over += 1
        lines = f"lines {m.group(3)}--{m.group(4)}" if m.group(3) else (f"line {m.group(5)}" if m.group(5) else "output routine")
        print(f"- {m.group(1)}box {m.group(2)}pt too wide/high — {file_at(events, m.start())} {lines}")
    if not n_over:
        print("- none")

    fonts = sorted(set(re.findall(r"Font shape `([^']+)' undefined\s*\(Font\)\s*using `([^']+)'", log)))
    print(f"\n## Font substitutions ({len(fonts)})")
    for f, g in fonts:
        print(f"- {f} -> {g}")

    other = Counter()
    for m in re.finditer(r"^((?:LaTeX|Package \w+|Class \w+) Warning: .*)$", log, re.M):
        w = re.sub(r" on input line \d+\.?", "", m.group(1))
        if "undefined" in w and ("Reference" in w or "Citation" in w):
            continue
        if "Font shape" in w:
            continue
        other[w[:150]] += 1
    print(f"\n## Other warnings ({sum(other.values())})")
    for w, n in other.most_common(25):
        print(f"- {w} x{n}")

    if os.path.isfile(pdf_path):
        info = run(["pdfinfo", pdf_path], proj).stdout
        pages = re.search(r"Pages:\s+(\d+)", info)
        print(f"\nPDF: {pdf_path} ({pages.group(1) if pages else '?'} pages)")
    else:
        print("\nNo PDF produced.")
        return

    if a.render or a.zoom:
        out = a.out or tempfile.mkdtemp(prefix="preprint_pages_")
        os.makedirs(out, exist_ok=True)
        if a.render:
            run(["pdftoppm", "-r", str(a.render), "-png", pdf_path, os.path.join(out, "page")], proj)
        for z in a.zoom:
            parts = z.split(":")
            page, dpi = parts[0], parts[1] if len(parts) > 1 else "160"
            cmd = ["pdftoppm", "-r", dpi, "-png", "-f", page, "-l", page]
            if len(parts) > 2:
                x, y, w, h = parts[2].split(",")
                cmd += ["-x", x, "-y", y, "-W", w, "-H", h]
            run(cmd + [pdf_path, os.path.join(out, f"zoom-p{page}-{dpi}")], proj)
        pngs = sorted(f for f in os.listdir(out) if f.endswith(".png"))
        print(f"\nRendered {len(pngs)} PNG(s) to {out}")
        for f in pngs:
            print("  " + os.path.join(out, f))


if __name__ == "__main__":
    main()
