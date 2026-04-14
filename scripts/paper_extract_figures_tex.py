#!/usr/bin/env python3
"""Extract figures and captions from arXiv TeX source.

Downloads the e-print tar from arXiv, parses \\begin{figure}...\\end{figure}
environments to extract \\includegraphics paths and \\caption text, then copies
the original image files. Falls back to PDF extraction if TeX source is
unavailable.

Usage:
    # From arXiv ID (downloads e-print automatically):
    python scripts/paper_extract_figures_tex.py --arxiv 2603.03329 -o output_dir

    # From local tar.gz:
    python scripts/paper_extract_figures_tex.py --tar path/to/eprint.tar.gz -o output_dir

Output (same format as paper_extract_figures.py):
    <output_dir>/
        figure_<N>.png          # Original image (converted to PNG if needed)
        figures_manifest.json   # {figure, caption, page, image_path} entries

Requires: PyMuPDF (fitz) — only for PDF→PNG conversion of vector figures
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request


# ---------------------------------------------------------------------------
# TeX parsing
# ---------------------------------------------------------------------------

def strip_tex_commands(text):
    """Strip common LaTeX formatting commands, keeping content."""
    # \textbf{content} → content, \textit{content} → content, etc.
    text = re.sub(r"\\(?:textbf|textit|textrm|texttt|textsf|textsc|emph|underline)\{([^}]*)\}", r"\1", text)
    # \textbf{\textit{nested}} — run again for nesting
    text = re.sub(r"\\(?:textbf|textit|textrm|texttt|textsf|textsc|emph|underline)\{([^}]*)\}", r"\1", text)
    # \label{...} → remove
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    # \ref{...} → (ref)
    text = re.sub(r"\\ref\{[^}]*\}", "(ref)", text)
    # \cite{...} → [cite]
    text = re.sub(r"\\cite[a-z]*\{[^}]*\}", "[cite]", text)
    # \footnote{...} → remove
    text = re.sub(r"\\footnote\{[^}]*\}", "", text)
    # ~ → space
    text = text.replace("~", " ")
    # remaining simple commands like \%, \&, etc.
    text = re.sub(r"\\([%&$#_{}])", r"\1", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_main_tex(tex_dir):
    """Find the main .tex file (the one with \\documentclass)."""
    for f in glob.glob(os.path.join(tex_dir, "**/*.tex"), recursive=True):
        try:
            with open(f, "r", errors="replace") as fh:
                content = fh.read(5000)  # Check first 5KB
                if r"\documentclass" in content:
                    return f
        except Exception:
            continue
    # Fallback: just return the largest .tex file
    tex_files = glob.glob(os.path.join(tex_dir, "**/*.tex"), recursive=True)
    if tex_files:
        return max(tex_files, key=os.path.getsize)
    return None


def resolve_inputs(main_tex_path, tex_dir, _depth=0):
    """Resolve \\input{} and \\include{} to get full document content.

    Returns concatenated TeX source with all includes recursively expanded.
    """
    if _depth > 10:  # Guard against infinite recursion
        return ""

    content = _read_tex(main_tex_path)

    def expand_include(match):
        filename = match.group(1)
        if not filename.endswith(".tex"):
            filename += ".tex"
        # Search relative to main tex file, then tex_dir
        candidates = [
            os.path.join(os.path.dirname(main_tex_path), filename),
            os.path.join(tex_dir, filename),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return resolve_inputs(c, tex_dir, _depth + 1)
        return ""  # File not found, skip

    # Expand \input{} and \include{}
    content = re.sub(r"\\(?:input|include)\{([^}]+)\}", expand_include, content)
    return content


def _read_tex(path):
    """Read a TeX file, handling encoding gracefully."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def _extract_caption_from_block(block):
    """Extract caption text from a figure environment block.

    Handles multiline captions and nested braces.
    """
    # Find \caption{ and then match balanced braces
    idx = block.find(r"\caption")
    if idx == -1:
        return ""

    # Skip \caption and optional [...] (short caption)
    rest = block[idx + len(r"\caption"):]
    rest = rest.lstrip()
    if rest.startswith("["):
        # Skip short caption [...]
        depth = 0
        i = 0
        for i, ch in enumerate(rest):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    break
        rest = rest[i + 1:].lstrip()

    if not rest.startswith("{"):
        return ""

    # Match balanced braces
    depth = 0
    end = 0
    for i, ch in enumerate(rest):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    caption = rest[1:end]  # Content inside outer braces
    return strip_tex_commands(caption)


def parse_figure_environments(tex_content, tex_dir):
    """Parse \\begin{figure}...\\end{figure} environments.

    Returns list of dicts:
        {fig_num, caption, image_paths, label}
    """
    # Match figure and figure* environments
    pattern = r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}"
    blocks = re.findall(pattern, tex_content, re.DOTALL)

    figures = []
    fig_counter = 0

    for block in blocks:
        fig_counter += 1

        # Extract \includegraphics paths
        img_matches = re.findall(
            r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",
            block,
        )

        # Resolve image paths — try with and without common extensions
        resolved_paths = []
        for img_path in img_matches:
            resolved = _resolve_image_path(img_path, tex_dir)
            if resolved:
                resolved_paths.append(resolved)

        # Extract caption
        caption = _extract_caption_from_block(block)

        # Extract label
        label_match = re.search(r"\\label\{([^}]+)\}", block)
        label = label_match.group(1) if label_match else None

        if resolved_paths or caption:  # Keep even if no images (caption-only)
            figures.append({
                "fig_num": fig_counter,
                "caption": caption[:600],
                "image_paths": resolved_paths,
                "label": label,
            })

    return figures


def _resolve_image_path(img_ref, tex_dir):
    """Resolve an \\includegraphics reference to an actual file path.

    LaTeX allows omitting extensions; try common ones.
    """
    # Try the path as-is first, then with common extensions
    extensions = ["", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg"]

    # img_ref might be relative to tex_dir
    for ext in extensions:
        candidate = os.path.join(tex_dir, img_ref + ext)
        if os.path.isfile(candidate):
            return candidate

    # Also try without any directory prefix in img_ref (flat layout)
    basename = os.path.basename(img_ref)
    for ext in extensions:
        candidate = os.path.join(tex_dir, basename + ext)
        if os.path.isfile(candidate):
            return candidate

    return None


# ---------------------------------------------------------------------------
# Image conversion
# ---------------------------------------------------------------------------

def convert_to_png(src_path, dst_path, dpi=200):
    """Convert an image file to PNG. Handles PDF, EPS, PNG, JPG, SVG."""
    ext = os.path.splitext(src_path)[1].lower()

    if ext in (".png",):
        shutil.copy2(src_path, dst_path)
        return True

    if ext in (".jpg", ".jpeg"):
        # Just copy — PNG conversion not essential for JPEGs
        shutil.copy2(src_path, dst_path.replace(".png", ".jpg"))
        # Actually, let's keep consistent .png output
        try:
            import fitz
            doc = fitz.open(src_path)
            # For single-page image
            page = doc[0]
            pix = page.get_pixmap(dpi=dpi)
            pix.save(dst_path)
            doc.close()
            return True
        except Exception:
            # Fallback: just copy as jpg
            jpg_path = dst_path.replace(".png", ".jpg")
            shutil.copy2(src_path, jpg_path)
            # Update dst to jpg
            os.rename(jpg_path, dst_path)
            return True

    if ext in (".pdf", ".eps"):
        try:
            import fitz
            doc = fitz.open(src_path)
            if len(doc) > 0:
                page = doc[0]
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                pix.save(dst_path)
                doc.close()
                return True
            doc.close()
        except Exception as e:
            print(f"  Warning: Could not convert {src_path}: {e}", file=sys.stderr)
            return False

    if ext == ".svg":
        # SVG conversion is complex; skip or try cairosvg if available
        try:
            import cairosvg
            cairosvg.svg2png(url=src_path, write_to=dst_path, dpi=dpi)
            return True
        except ImportError:
            print(f"  Warning: SVG conversion requires cairosvg: {src_path}", file=sys.stderr)
            return False

    print(f"  Warning: Unknown image format: {src_path}", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# arXiv download
# ---------------------------------------------------------------------------

def download_eprint(arxiv_id, dest_path):
    """Download arXiv e-print tar.gz."""
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    print(f"  Downloading e-print: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AutoWiki/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ERROR: Download failed: {e}", file=sys.stderr)
        return False


def extract_tar(tar_path, dest_dir):
    """Extract a tar.gz (or plain gzipped file) to dest_dir."""
    os.makedirs(dest_dir, exist_ok=True)
    try:
        with tarfile.open(tar_path, "r:gz") as tf:
            tf.extractall(dest_dir)
        return True
    except tarfile.TarError:
        # Might be a single gzipped file (rare, but arXiv does this for single-file submissions)
        import gzip
        try:
            with gzip.open(tar_path, "rb") as gz:
                content = gz.read()
            out_path = os.path.join(dest_dir, "main.tex")
            with open(out_path, "wb") as f:
                f.write(content)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def extract_figures_from_tex(tex_dir, output_dir, dpi=200):
    """Extract figures from a TeX source directory.

    Returns manifest in the same format as paper_extract_figures.py.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Find main TeX file
    main_tex = find_main_tex(tex_dir)
    if not main_tex:
        print("  ERROR: No .tex file found", file=sys.stderr)
        return []

    print(f"  Main TeX: {os.path.basename(main_tex)}")

    # Expand \input/\include
    full_content = resolve_inputs(main_tex, tex_dir)

    # Parse figure environments
    figures = parse_figure_environments(full_content, tex_dir)
    print(f"  Figure environments found: {len(figures)}")

    # Process each figure
    manifest = []
    for fig in figures:
        caption_preview = fig["caption"][:80] + ("..." if len(fig["caption"]) > 80 else "")
        print(f"    Fig {fig['fig_num']}: {caption_preview}")
        print(f"      Images: {[os.path.basename(p) for p in fig['image_paths']]}")

        if not fig["image_paths"]:
            # Caption-only figure (no image found)
            manifest.append({
                "figure": f"Figure {fig['fig_num']}",
                "caption": fig["caption"],
                "page": None,
                "image_path": None,
                "source": "tex",
                "label": fig["label"],
                "note": "no image file found",
            })
            continue

        # For figures with multiple images (subfigures), combine or take first
        if len(fig["image_paths"]) == 1:
            src = fig["image_paths"][0]
            filename = f"figure_{fig['fig_num']}.png"
            dst = os.path.join(output_dir, filename)
            ok = convert_to_png(src, dst, dpi)
            if ok:
                manifest.append({
                    "figure": f"Figure {fig['fig_num']}",
                    "caption": fig["caption"],
                    "page": None,
                    "image_path": filename,
                    "source": "tex",
                    "label": fig["label"],
                    "original_format": os.path.splitext(src)[1],
                })
                print(f"      → {filename} (from {os.path.basename(src)})")
        else:
            # Multiple images in one figure environment (subfigures)
            for j, src in enumerate(fig["image_paths"]):
                suffix = chr(ord("a") + j)
                filename = f"figure_{fig['fig_num']}{suffix}.png"
                dst = os.path.join(output_dir, filename)
                ok = convert_to_png(src, dst, dpi)
                if ok:
                    manifest.append({
                        "figure": f"Figure {fig['fig_num']}{suffix}",
                        "caption": fig["caption"],
                        "page": None,
                        "image_path": filename,
                        "source": "tex",
                        "label": fig["label"],
                        "original_format": os.path.splitext(src)[1],
                    })
                    print(f"      → {filename} (from {os.path.basename(src)})")

    # Write manifest
    manifest_path = os.path.join(output_dir, "figures_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n  Manifest: {manifest_path}")

    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract figures from arXiv TeX source"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--arxiv", help="arXiv paper ID (e.g., 2603.03329)")
    group.add_argument("--tar", help="Path to local e-print tar.gz")
    parser.add_argument("-o", "--output", required=True,
                        help="Output directory for figures and manifest")
    parser.add_argument("--dpi", type=int, default=200,
                        help="Rendering DPI for PDF/EPS conversion (default: 200)")
    args = parser.parse_args()

    if args.arxiv:
        # Download and extract
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "eprint.tar.gz")
            if not download_eprint(args.arxiv, tar_path):
                sys.exit(1)
            tex_dir = os.path.join(tmpdir, "tex")
            if not extract_tar(tar_path, tex_dir):
                print("ERROR: Failed to extract tar", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting figures from TeX source: {args.arxiv}")
            manifest = extract_figures_from_tex(tex_dir, args.output, args.dpi)
    else:
        # Local tar
        if not os.path.isfile(args.tar):
            print(f"ERROR: File not found: {args.tar}", file=sys.stderr)
            sys.exit(1)
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_dir = os.path.join(tmpdir, "tex")
            if not extract_tar(args.tar, tex_dir):
                print("ERROR: Failed to extract tar", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting figures from TeX source: {args.tar}")
            manifest = extract_figures_from_tex(tex_dir, args.output, args.dpi)

    print(f"\nDone. Extracted {len(manifest)} figure(s) to {args.output}")


if __name__ == "__main__":
    main()
