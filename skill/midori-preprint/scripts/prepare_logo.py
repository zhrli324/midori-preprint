#!/usr/bin/env python3
"""Prepare a logo for the template's logo row (only needed for new logos;
NTU and Midori Lab logos are already in assets/template/logos/).

Usage:
  python3 prepare_logo.py logo.svg out_dir            # vector PDF, cropped
  python3 prepare_logo.py logo.png out_dir            # trimmed, transparent PNG
  python3 prepare_logo.py logo.png out_dir --split    # stacked logo -> icon + wordmark

Requirements: Pillow; for SVG also cairosvg (+ the cairo library) and pdfcrop
(TeX Live). On macOS with Homebrew cairo, run with
  DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
Install them in a scratch virtual environment rather than the system Python:
  python3 -m venv /tmp/logo-venv && /tmp/logo-venv/bin/pip install pillow cairosvg

Then use the pieces with \\logoimage[height]{file}; keep every piece at the
same visual height as the other logo (about 0.42in) and size a separate
wordmark so its letters weigh about the same as the other logo's text.
"""
import argparse
import os
import subprocess
import sys


def svg_to_pdf(svg, out_dir):
    import cairosvg
    stem = os.path.splitext(os.path.basename(svg))[0]
    raw = os.path.join(out_dir, stem + "-raw.pdf")
    final = os.path.join(out_dir, stem + ".pdf")
    cairosvg.svg2pdf(url=svg, write_to=raw)
    subprocess.run(["pdfcrop", "--margins", "0", raw, final], check=True, capture_output=True)
    os.remove(raw)
    print("wrote", final)


def trim_png(png, out_dir, split, threshold=225):
    from PIL import Image
    im = Image.open(png).convert("RGBA")
    w, h = im.size
    px = im.load()

    def ink(p):
        r, g, b, a = p
        return a > 20 and min(r, g, b) < threshold

    rows = [any(ink(px[x, y]) for x in range(0, w, 2)) for y in range(h)]
    bands, y = [], 0
    while y < h:
        if rows[y]:
            s = y
            while y < h and rows[y]:
                y += 1
            bands.append([s, y])
        else:
            y += 1
    merged = []
    for b in bands:  # join bands split only by anti-aliasing
        if merged and b[0] - merged[-1][1] < max(4, h // 100):
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    if not merged:
        sys.exit("no ink found")

    def crop(y0, y1, name, pad=6):
        cols = [x for x in range(w) if any(ink(px[x, yy]) for yy in range(y0, y1, 2))]
        box = (max(cols[0] - pad, 0), max(y0 - pad, 0), min(cols[-1] + 1 + pad, w), min(y1 + pad, h))
        c = im.crop(box)
        data = []
        for r, g, b, a in c.getdata():  # white -> transparent with a soft edge
            m = min(r, g, b)
            alpha = 0 if m >= 250 else (255 if m <= 200 else int(255 * (250 - m) / 50))
            data.append((r, g, b, min(a, alpha)))
        c.putdata(data)
        path = os.path.join(out_dir, name)
        c.save(path, dpi=(600, 600))
        print("wrote", path, c.size)

    stem = os.path.splitext(os.path.basename(png))[0]
    crop(merged[0][0], merged[-1][1], stem + "-logo.png")
    if split:
        if len(merged) < 2:
            sys.exit("--split: could not find a separate wordmark band below the icon")
        crop(merged[0][0], merged[-2][1], stem + "-icon.png")
        crop(merged[-1][0], merged[-1][1], stem + "-wordmark.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logo")
    ap.add_argument("out_dir")
    ap.add_argument("--split", action="store_true", help="split a stacked PNG logo into icon + wordmark")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    if a.logo.lower().endswith(".svg"):
        svg_to_pdf(a.logo, a.out_dir)
    else:
        trim_png(a.logo, a.out_dir, a.split)


if __name__ == "__main__":
    main()
