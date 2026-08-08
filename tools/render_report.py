"""Render a Markdown work product to a self-contained, print-ready HTML file.

Used to produce the audit handoff report for PDF conversion. Kept in the repo so
the output is reproducible rather than a one-off artifact.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import markdown

# A4 print stylesheet. Deliberately conservative: system fonts only, no external
# requests, so the HTML renders identically offline and inside a PDF engine.
STYLE = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.55; color: #1a1a1a;
  max-width: 178mm; margin: 0 auto; padding: 0;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
h1 { font-size: 20pt; margin: 0 0 4mm; padding-bottom: 3mm;
     border-bottom: 2px solid #2a2a2a; line-height: 1.25; }
h2 { font-size: 14pt; margin: 9mm 0 3mm; padding-bottom: 1.5mm;
     border-bottom: 1px solid #c8c8c8; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 6mm 0 2mm; page-break-after: avoid; }
h2 + p, h3 + p, h2 + table, h3 + table { page-break-before: avoid; }
p, ul, ol { margin: 0 0 3mm; }
li { margin-bottom: 1.2mm; }
blockquote {
  margin: 0 0 5mm; padding: 3mm 4mm; background: #f5f6f8;
  border-left: 3px solid #6a7180; font-size: 9.8pt;
}
blockquote p { margin: 0 0 1.5mm; }
blockquote p:last-child { margin: 0; }
table {
  border-collapse: collapse; width: 100%; margin: 0 0 5mm;
  font-size: 9pt; page-break-inside: avoid;
}
th, td { border: 1px solid #ccd0d6; padding: 1.8mm 2.4mm;
         text-align: left; vertical-align: top; }
th { background: #eef0f3; font-weight: 600; }
tr:nth-child(even) td { background: #fafbfc; }
code {
  font-family: Consolas, "SF Mono", monospace; font-size: 8.8pt;
  background: #f0f1f4; padding: 0.4mm 1.2mm; border-radius: 2px;
  word-break: break-word;
}
pre {
  background: #f7f8fa; border: 1px solid #dfe2e7; border-radius: 3px;
  padding: 3mm; overflow-x: auto; page-break-inside: avoid; margin: 0 0 4mm;
}
pre code { background: none; padding: 0; font-size: 8.6pt; }
hr { border: none; border-top: 1px solid #d5d8dd; margin: 7mm 0; }
strong { font-weight: 600; }
a { color: #1a4d8f; text-decoration: none; }
.footer {
  margin-top: 9mm; padding-top: 3mm; border-top: 1px solid #d5d8dd;
  font-size: 8.5pt; color: #666;
}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{style}</style>
</head>
<body>
{body}
<div class="footer">{footer}</div>
</body>
</html>
"""


def render(source: Path, destination: Path, footer: str) -> None:
    text = source.read_text(encoding="utf-8")

    heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = heading.group(1).strip() if heading else source.stem

    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        output_format="html5",
    )

    destination.write_text(
        TEMPLATE.format(
            title=html.escape(title),
            style=STYLE,
            body=body,
            footer=html.escape(footer),
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--footer",
        default="ClutchG PC Optimizer — ISO/IEC 29110 work product",
        help="Footer line rendered at the end of the document",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f"Source not found: {args.source}")

    render(args.source, args.destination, args.footer)
    print(f"Wrote {args.destination} ({args.destination.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
