#!/usr/bin/env python3
"""
extract_figures.py — Extract figures from academic PDF papers.

Uses PyMuPDF (fitz) to locate figure captions, determine figure bounding
regions, and render them as high-resolution PNG images.

Works with both raster and vector figures (renders the page region).

Output includes figure number, page, caption text, and image path.
The LLM reviews captions and paper content to decide which figures
to include in the source page and how to describe them.

Requirements:
    pip install PyMuPDF Pillow

Usage:
    # Single PDF
    python extract_figures.py paper.pdf

    # Scan a directory of PDFs
    python extract_figures.py ./papers/

    # Custom output root and DPI
    python extract_figures.py ./papers/ -o ./all_figures -d 300 -n 5
"""

import argparse
import json
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Caption detection
# ---------------------------------------------------------------------------

CAPTION_RE = re.compile(r"^(?:Figure|Fig\.?)\s*(\d+)")


def find_captions(doc: fitz.Document, max_pages: int) -> list[dict]:
    """Return a list of figure caption metadata from the first *max_pages* pages."""
    captions: list[dict] = []
    pages_to_scan = min(doc.page_count, max_pages)

    for pi in range(pages_to_scan):
        page = doc[pi]
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            text = "".join(
                span["text"] for line in block["lines"] for span in line["spans"]
            ).strip()
            m = CAPTION_RE.match(text)
            if m:
                captions.append(
                    {
                        "num": int(m.group(1)),
                        "page": pi,
                        "y0": block["bbox"][1],
                        "y1": block["bbox"][3],
                        "text": text[:300],
                    }
                )
    return captions



# ---------------------------------------------------------------------------
# Figure region detection
# ---------------------------------------------------------------------------


def _find_figure_top(
    doc: fitz.Document, caption: dict, all_captions: list[dict]
) -> float:
    """Heuristic: walk upward from caption, skip narrow figure-internal labels,
    stop at the first wide body-text block."""
    page = doc[caption["page"]]
    pw = page.rect.width
    body_width_threshold = pw * 0.55

    blocks_above: list[dict] = []
    for b in page.get_text("dict")["blocks"]:
        if b["bbox"][1] >= caption["y0"] - 2:
            continue
        text = ""
        if b["type"] == 0:
            text = "".join(
                s["text"] for ln in b["lines"] for s in ln["spans"]
            ).strip()
        blocks_above.append(
            {
                "y0": b["bbox"][1],
                "y1": b["bbox"][3],
                "w": b["bbox"][2] - b["bbox"][0],
                "text": text,
                "type": b["type"],
            }
        )
    blocks_above.sort(key=lambda b: b["y0"])

    prev_cap_bottom = 0.0
    for c in all_captions:
        if c["page"] == caption["page"] and c["y1"] < caption["y0"] - 5:
            prev_cap_bottom = max(prev_cap_bottom, c["y1"])

    figure_top = prev_cap_bottom
    for b in reversed(blocks_above):
        if b["y1"] <= prev_cap_bottom:
            break
        is_body = (
            b["w"] > body_width_threshold
            and b["type"] == 0
            and len(b["text"]) > 40
        )
        if is_body:
            figure_top = b["y1"]
            break

    return max(figure_top, 0.0)


# ---------------------------------------------------------------------------
# Single-PDF extraction
# ---------------------------------------------------------------------------


def extract_figures(
    pdf_path: str,
    output_dir: str,
    max_pages: int = 10,
    dpi: int = 200,
) -> list[dict]:
    """Extract all figures from *pdf_path* and save as PNGs.

    Returns a list of dicts: {fig_num, page, caption, image_path}
    """
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    captions = find_captions(doc, max_pages)
    if not captions:
        doc.close()
        return []

    results: list[dict] = []
    margin = 5

    for cap in captions:
        top = _find_figure_top(doc, cap, captions)
        page = doc[cap["page"]]

        clip = fitz.Rect(
            page.rect.x0 + margin,
            max(page.rect.y0, top),
            page.rect.x1 - margin,
            min(page.rect.y1, cap["y1"] + margin),
        )

        # Skip degenerate regions (zero or negative dimensions)
        if clip.width <= 0 or clip.height <= 0:
            print(
                f"  SKIP Fig {cap['num']} (page {cap['page'] + 1}): "
                f"degenerate clip region {clip.width:.0f}×{clip.height:.0f}",
                file=sys.stderr,
            )
            continue

        mat = fitz.Matrix(dpi / 72, dpi / 72)
        try:
            pix = page.get_pixmap(matrix=mat, clip=clip)
            out_path = os.path.join(output_dir, f"figure_{cap['num']}.png")
            pix.save(out_path)
        except Exception as exc:
            print(
                f"  SKIP Fig {cap['num']} (page {cap['page'] + 1}): {exc}",
                file=sys.stderr,
            )
            continue

        results.append(
            {
                "fig_num": cap["num"],
                "page": cap["page"] + 1,
                "caption": cap["text"],
                "image_path": os.path.abspath(out_path),
            }
        )

    doc.close()
    return results


# ---------------------------------------------------------------------------
# Directory scan
# ---------------------------------------------------------------------------


def scan_directory(
    input_dir: str,
    output_root: str,
    max_pages: int = 10,
    dpi: int = 200,
) -> list[dict]:
    """Scan all PDFs in *input_dir*, extract figures, return manifest entries."""
    pdf_files = sorted(
        f
        for f in os.listdir(input_dir)
        if f.lower().endswith(".pdf")
    )
    if not pdf_files:
        print(f"No PDF files found in {input_dir}", file=sys.stderr)
        return []

    manifest: list[dict] = []

    for pdf_name in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_name)
        stem = os.path.splitext(pdf_name)[0]
        fig_dir = os.path.join(output_root, stem)

        results = extract_figures(pdf_path, fig_dir, max_pages, dpi)
        for r in results:
            r["pdf"] = pdf_name
        manifest.extend(results)

    return manifest


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def print_manifest(manifest: list[dict], fmt: str = "text") -> None:
    """Print the extraction manifest in the requested format."""
    if fmt == "json":
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return

    # Grouped text output — easy for LLMs to scan
    current_pdf = None
    for entry in manifest:
        if entry.get("pdf") != current_pdf:
            current_pdf = entry.get("pdf")
            if current_pdf:
                print(f"\n## {current_pdf}")
                print("-" * 60)

        print(f"  Fig {entry['fig_num']:<3d} | page {entry['page']:<3d} | {entry['image_path']}")
        print(f"          {entry['caption']}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract figures from academic PDFs. Accepts a single PDF or a directory."
    )
    parser.add_argument(
        "input",
        help="Path to a PDF file or a directory containing PDFs",
    )
    parser.add_argument(
        "--output-dir", "-o", default=None,
        help="Output root directory (default: <input>_figures/ or <dir>/figures/)",
    )
    parser.add_argument(
        "--max-pages", "-n", type=int, default=10,
        help="Scan first N pages per PDF (default: 10)",
    )
    parser.add_argument(
        "--dpi", "-d", type=int, default=200,
        help="Render DPI (default: 200)",
    )
    parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text",
        help="Output format: 'text' (human/LLM readable) or 'json' (default: text)",
    )
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)
    is_file = os.path.isfile(args.input) and args.input.lower().endswith(".pdf")

    if not is_dir and not is_file:
        print(f"ERROR: {args.input} is not a PDF file or directory", file=sys.stderr)
        sys.exit(1)

    # Resolve output directory
    if args.output_dir is None:
        if is_dir:
            args.output_dir = os.path.join(args.input, "figures")
        else:
            stem = os.path.splitext(os.path.basename(args.input))[0]
            args.output_dir = os.path.join(
                os.path.dirname(args.input) or ".", f"{stem}_figures"
            )

    # Extract
    if is_dir:
        manifest = scan_directory(
            args.input, args.output_dir, args.max_pages, args.dpi
        )
    else:
        manifest = extract_figures(
            args.input, args.output_dir, args.max_pages, args.dpi
        )
        pdf_name = os.path.basename(args.input)
        for entry in manifest:
            entry["pdf"] = pdf_name

    # Output
    print_manifest(manifest, args.format)

    total = len(manifest)
    pdfs = len({e.get("pdf") for e in manifest})
    print(f"\n--- {total} figure(s) from {pdfs} PDF(s) ---", file=sys.stderr)


if __name__ == "__main__":
    main()
