# Researcher Business Card

A LaTeX template for a compact academic/researcher business card (85 × 55 mm) featuring a QR code with embedded contact information in MECARD format. Includes a Python utility to tile the card onto an A4 sheet for printing.

## Contents

| File | Purpose |
|---|---|
| `main.tex` | Business card template (XeLaTeX) — layout only, no personal data |
| `personal.tex` | Your personal details and research topics (gitignored) |
| `tile_pdf_a4.py` | Python script to tile the card PDF onto A4 for printing |
| `Garamond12-*.ttf` | Bundled Garamond 12 font files |

## Requirements

**Card compilation:**
- XeLaTeX (e.g. from TeX Live or MiKTeX)
- LaTeX packages: `memoir`, `xcolor`, `fontspec`, `pstricks`, `auto-pst-pdf`, `pst-barcode`

**Tiling script:**
- Python 3
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`pip install pymupdf`)

## Usage

### 1. Customize the card

Copy `personal.tex` and fill in your details — this is the only file you need to edit:

```latex
\newcommand{\FirstName}{Jane}
\newcommand{\LastName}{Doe}
\newcommand{\TitleBefore}{Dr.}
\newcommand{\TitleAfter}{PhD}
\newcommand{\RoleTitle}{Researcher}
\newcommand{\Group}{Awesome Research Group}
\newcommand{\Department}{Department of Computer Science}
\newcommand{\Institute}{My University}
\newcommand{\MyURL}{https://university.edu/~jdoe/}
\newcommand{\MyEmail}{jane.doe@university.edu}
\newcommand{\Phone}{+1 234 567 8900}
\newcommand{\GroupShort}{ARG}
\newcommand{\GroupContact}{https://arg.university.edu}

\newcommand{\ResearchTopics}{%
    \topic{Machine Learning}%
    \topic{Computer Vision}%
    \topic{Robotics}%
}
```

Add or remove `\topic{}` lines to match your research fields. `main.tex` handles all layout.

### 2. Compile the card

```bash
xelatex -shell-escape main.tex
```

This produces `main.pdf` — a single business card at 85 × 55 mm.

### 3. Tile onto A4 for printing

```bash
python tile_pdf_a4.py main.pdf tiled_a4.pdf
```

The script auto-fits as many copies as possible on an A4 page (portrait by default) with 5 mm outer margins, 3 mm gaps, and crop marks.

**Common options:**

```bash
# Custom margins and gaps
python tile_pdf_a4.py main.pdf tiled_a4.pdf --margin-mm 7 --gap-mm 4

# Scale cards slightly smaller
python tile_pdf_a4.py main.pdf tiled_a4.pdf --scale 0.95

# Landscape A4
python tile_pdf_a4.py main.pdf tiled_a4.pdf --landscape

# Fixed grid size
python tile_pdf_a4.py main.pdf tiled_a4.pdf --cols 2 --rows 5

# No crop marks
python tile_pdf_a4.py main.pdf tiled_a4.pdf --no-crop-marks
```

## License

[GNU Affero General Public License v3.0](LICENSE)
