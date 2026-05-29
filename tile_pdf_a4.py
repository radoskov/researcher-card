#!/usr/bin/env python3
"""
Tile the first page of a PDF repeatedly onto an A4 page.

Default settings are suitable for printing multiple small cards/labels:
- A4 portrait
- no scaling
- 5 mm outer margins
- 3 mm gaps between copies
- crop marks enabled
"""
examples = """
Examples:
  python tile_pdf_a4.py main.pdf tiled_a4.pdf
  python tile_pdf_a4.py main.pdf tiled_a4.pdf --margin-mm 7 --gap-mm 4
  python tile_pdf_a4.py main.pdf tiled_a4.pdf --scale 0.95 --no-crop-marks
  python tile_pdf_a4.py main.pdf tiled_a4.pdf --landscape
  python tile_pdf_a4.py main.pdf tiled_a4.pdf --cols 2 --rows 5
"""

import sys
import argparse
import math
from pathlib import Path

import fitz  # PyMuPDF

PT_PER_MM = 72.0 / 25.4
A4_PORTRAIT = (210 * PT_PER_MM, 297 * PT_PER_MM)


def mm(value: float) -> float:
    return value * PT_PER_MM


def draw_crop_marks(page, rect, mark_len=mm(4), offset=mm(1), width=0.3):
    """Draw small crop marks just outside each tile rectangle."""
    x0, y0, x1, y1 = rect.x0, rect.y0, rect.x1, rect.y1
    segments = [
        # top-left
        ((x0 - offset - mark_len, y0), (x0 - offset, y0)),
        ((x0, y0 - offset - mark_len), (x0, y0 - offset)),
        # top-right
        ((x1 + offset, y0), (x1 + offset + mark_len, y0)),
        ((x1, y0 - offset - mark_len), (x1, y0 - offset)),
        # bottom-left
        ((x0 - offset - mark_len, y1), (x0 - offset, y1)),
        ((x0, y1 + offset), (x0, y1 + offset + mark_len)),
        # bottom-right
        ((x1 + offset, y1), (x1 + offset + mark_len, y1)),
        ((x1, y1 + offset), (x1, y1 + offset + mark_len)),
    ]
    for start, end in segments:
        page.draw_line(start, end, color=(0, 0, 0), width=width)

class HelpOnErrorParser(argparse.ArgumentParser):

    def error(self, message):
        self.print_help(sys.stderr)
        sys.stderr.write(examples)
        self.exit(2)

def main():
    parser = HelpOnErrorParser(description="Tile a PDF page onto A4.")
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--page", type=int, default=1, help="1-based source page number to tile")
    parser.add_argument("--margin-mm", type=float, default=5.0)
    parser.add_argument("--gap-mm", type=float, default=3.0)
    parser.add_argument("--scale", type=float, default=1.0, help="Scale each copy, e.g. 0.95")
    parser.add_argument("--cols", type=int, default=None, help="Override automatic column count")
    parser.add_argument("--rows", type=int, default=None, help="Override automatic row count")
    parser.add_argument("--landscape", action="store_true", help="Use A4 landscape")
    parser.add_argument("--no-crop-marks", action="store_true")
    args = parser.parse_args()

    src = fitz.open(args.input_pdf)
    page_index = args.page - 1
    if page_index < 0 or page_index >= src.page_count:
        raise SystemExit(f"Source page {args.page} is out of range; PDF has {src.page_count} pages.")

    source_page = src[page_index]
    source_rect = source_page.rect
    tile_w = source_rect.width * args.scale
    tile_h = source_rect.height * args.scale

    a4_w, a4_h = A4_PORTRAIT
    if args.landscape:
        a4_w, a4_h = a4_h, a4_w

    margin = mm(args.margin_mm)
    gap = mm(args.gap_mm)
    usable_w = a4_w - 2 * margin
    usable_h = a4_h - 2 * margin

    cols = args.cols or max(1, math.floor(((usable_w + gap) / (tile_w + gap)) + 1e-9))
    rows = args.rows or max(1, math.floor(((usable_h + gap) / (tile_h + gap)) + 1e-9))

    grid_w = cols * tile_w + (cols - 1) * gap
    grid_h = rows * tile_h + (rows - 1) * gap
    if grid_w > usable_w + 0.01 or grid_h > usable_h + 0.01:
        raise SystemExit(
            f"Grid does not fit A4: {cols} x {rows} needs "
            f"{grid_w / PT_PER_MM:.1f} x {grid_h / PT_PER_MM:.1f} mm inside "
            f"{usable_w / PT_PER_MM:.1f} x {usable_h / PT_PER_MM:.1f} mm. "
            "Reduce scale, margins, gaps, cols, or rows."
        )

    out = fitz.open()
    out_page = out.new_page(width=a4_w, height=a4_h)

    # Center the grid on the page.
    start_x = (a4_w - grid_w) / 2
    start_y = (a4_h - grid_h) / 2

    for r in range(rows):
        for c in range(cols):
            x0 = start_x + c * (tile_w + gap)
            y0 = start_y + r * (tile_h + gap)
            dest = fitz.Rect(x0, y0, x0 + tile_w, y0 + tile_h)
            out_page.show_pdf_page(dest, src, page_index)
            if not args.no_crop_marks:
                draw_crop_marks(out_page, dest)

    out.save(args.output_pdf, garbage=4, deflate=True)
    print(f"Wrote {args.output_pdf}")
    print(f"A4 size: {a4_w / PT_PER_MM:.1f} x {a4_h / PT_PER_MM:.1f} mm")
    print(f"Tile size: {tile_w / PT_PER_MM:.1f} x {tile_h / PT_PER_MM:.1f} mm")
    print(f"Grid: {cols} columns x {rows} rows = {cols * rows} copies")


if __name__ == "__main__":
    main()
