#!/usr/bin/env python3
"""Extract figures and captions from a PDF research paper.

Pipeline:
1. Parse text blocks to find figure captions (Figure N / Fig. N patterns)
2. Render page regions around each figure at high DPI (captures vector graphics)
3. Output figures_manifest.json — agent reads captions (text) to decide which
   figures to include, without needing to view every image

Usage:
    python scripts/paper_extract_figures.py <pdf_path> -o <output_dir>

Output:
    <output_dir>/
        figure_<N>.png          # Rendered image for each detected figure
        figures_manifest.json   # {figure, caption, page, image_path} entries

Requires: PyMuPDF (fitz)
"""

import argparse
import json
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Caption extraction
# ---------------------------------------------------------------------------

def extract_captions(doc):
    """Find figure captions by scanning text blocks for 'Figure N' / 'Fig. N'.

    Only blocks whose text *starts* with a figure label are treated as captions,
    filtering out in-text references like "as shown in Figure 3".

    Returns list of dicts sorted by fig_num:
        {fig_num, caption, page, y_top, y_bottom}
    """
    captions = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, type)

        for block in blocks:
            if block[6] != 0:  # skip image blocks
                continue
            text = block[4].strip()
            m = re.match(
                r"(?:Figure|Fig\.?)\s*(\d+)\s*[.:)\s]\s*(.*)",
                text,
                re.IGNORECASE | re.DOTALL,
            )
            if not m:
                continue

            fig_num = int(m.group(1))
            caption_text = re.sub(r"\s+", " ", m.group(2)).strip()
            captions.append({
                "fig_num": fig_num,
                "caption": caption_text[:600],
                "page": page_num,
                "y_top": block[1],     # y0 of caption block
                "y_bottom": block[3],  # y1 of caption block
            })

    # Deduplicate — keep first occurrence of each fig_num
    seen = set()
    unique = []
    for c in captions:
        if c["fig_num"] not in seen:
            seen.add(c["fig_num"])
            unique.append(c)

    return sorted(unique, key=lambda x: x["fig_num"])


# ---------------------------------------------------------------------------
# Figure region estimation & rendering
# ---------------------------------------------------------------------------

def _is_body_text(block, page_width):
    """Heuristic: is this block body text (not a diagram label)?

    Diagram labels tend to be short, narrow fragments scattered across the
    figure area.  Body text (paragraphs, headings, captions) is typically
    wider than 40% of the page and contains ≥30 characters.
    """
    x0, _, x1, _, text, _, btype = block
    if btype != 0:
        return False
    width = x1 - x0
    char_count = len(text.strip())
    return width > page_width * 0.40 and char_count >= 30


def estimate_figure_clip(page, caption_y_top, caption_y_bottom):
    """Estimate a clip rect that contains the figure + its caption.

    Heuristic:
    - Bottom = caption block bottom + small padding
    - Top = bottom of the nearest *body-text* block above the figure,
      ignoring short diagram labels embedded inside the figure area.
    """
    page_rect = page.rect
    page_width = page_rect.width

    # Collect y-bottoms of body-text blocks clearly above the caption
    blocks = page.get_text("blocks")
    body_bottoms_above = []
    for b in blocks:
        if not _is_body_text(b, page_width):
            continue
        block_bottom = b[3]
        if block_bottom < caption_y_top - 10:
            body_bottoms_above.append(block_bottom)

    # Figure top: just below the nearest body text above, or page top margin
    if body_bottoms_above:
        figure_top = max(body_bottoms_above) + 2
    else:
        figure_top = max(page_rect.y0, 30)  # small top margin

    # Figure bottom: end of caption block + padding
    figure_bottom = min(caption_y_bottom + 8, page_rect.y1)

    # Minimum height guard — if region is too small, extend upward
    min_height = 150  # ~2 inches at 72 dpi
    if figure_bottom - figure_top < min_height:
        figure_top = max(page_rect.y0, caption_y_top - page_rect.height * 0.45)

    return fitz.Rect(page_rect.x0, figure_top, page_rect.x1, figure_bottom)


def render_region(page, clip_rect, dpi=200):
    """Render a page region to PNG bytes."""
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)
    return pix.tobytes("png")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def extract_figures(pdf_path, output_dir, dpi=200):
    """Extract figures: detect captions, render regions, write manifest."""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    # Step 1: Find captions
    captions = extract_captions(doc)
    print(f"  Captions found: {len(captions)}")
    for c in captions:
        preview = c["caption"][:80] + ("..." if len(c["caption"]) > 80 else "")
        print(f"    Fig {c['fig_num']} (p.{c['page'] + 1}): {preview}")

    # Step 2: Render figure regions
    manifest = []
    for cap in captions:
        page = doc[cap["page"]]
        clip = estimate_figure_clip(page, cap["y_top"], cap["y_bottom"])
        png_bytes = render_region(page, clip, dpi)

        filename = f"figure_{cap['fig_num']}.png"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "wb") as f:
            f.write(png_bytes)

        manifest.append({
            "figure": f"Figure {cap['fig_num']}",
            "caption": cap["caption"],
            "page": cap["page"] + 1,  # 1-indexed for humans
            "image_path": filename,
        })
        print(f"  → {filename} ({len(png_bytes)} bytes, p.{cap['page'] + 1})")

    # Step 3: Write manifest
    manifest_path = os.path.join(output_dir, "figures_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n  Manifest: {manifest_path}")

    doc.close()
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract figures and captions from a research paper PDF"
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", required=True,
                        help="Output directory for figures and manifest")
    parser.add_argument("--dpi", type=int, default=200,
                        help="Rendering DPI (default: 200)")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"ERROR: File not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting figures from: {args.pdf}")
    manifest = extract_figures(args.pdf, args.output, args.dpi)
    print(f"\nDone. Extracted {len(manifest)} figure(s) to {args.output}")


if __name__ == "__main__":
    main()
