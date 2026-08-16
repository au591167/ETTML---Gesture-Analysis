"""Render the Markdown exam notes as a tablet-friendly A4 PDF.

Usage from the repository root:
    python Presentation/render_exam_notes.py

Requires the Python package ``markdown`` and a local Chrome/Chromium install.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    import markdown
    from markdown.extensions.toc import slugify_unicode
except ImportError as error:  # pragma: no cover - user-facing dependency check
    raise SystemExit("Missing dependency. Run: python -m pip install markdown") from error


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "Presentation" / "ETTML-eksamensnoter.md"
DEFAULT_OUTPUT = REPO_ROOT / "Presentation" / "ETTML-eksamensnoter-tablet.pdf"


def find_browser(explicit: str | None) -> Path:
    """Return a Chrome/Chromium executable that can print HTML to PDF."""
    candidates = [
        Path(explicit) if explicit else None,
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for command in ("chrome", "chromium", "chromium-browser"):
        resolved = shutil.which(command)
        if resolved:
            candidates.append(Path(resolved))
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise SystemExit("Chrome/Chromium was not found. Pass its path with --browser.")


def build_html(markdown_text: str) -> str:
    """Convert the notes while keeping headings and code easy to scan."""
    lines = markdown_text.splitlines()
    title = "ETTML – fagligt opslagsværk til eksamen"
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]

    body = markdown.markdown(
        "\n".join(lines),
        extensions=["fenced_code", "tables", "sane_lists", "toc"],
        # Keep Danish letters in anchors so the PDF links match the links used
        # by the Markdown notes and GitHub's heading anchors.
        extension_configs={"toc": {"permalink": False, "slugify": slugify_unicode}},
        output_format="html5",
    )

    css = r"""
@page {
  size: A4;
  margin: 15mm 14mm 18mm 16mm;
  @bottom-left {
    content: "ETTML · Eksamensnoter";
    color: #64748b;
    font: 8.5pt "Segoe UI", Arial, sans-serif;
  }
  @bottom-right {
    content: "Side " counter(page) " af " counter(pages);
    color: #64748b;
    font: 8.5pt "Segoe UI", Arial, sans-serif;
  }
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: #182235;
  background: white;
  font-family: "Segoe UI", Aptos, Arial, sans-serif;
  font-size: 10.8pt;
  line-height: 1.48;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.cover {
  min-height: 255mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 18mm 12mm;
  color: white;
  background: linear-gradient(145deg, #11294a 0%, #164e63 62%, #0f766e 100%);
  break-after: page;
}
.cover .eyebrow {
  color: #99f6e4;
  font-size: 12pt;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.cover h1 {
  margin: 8mm 0 5mm;
  color: white;
  font-size: 31pt;
  line-height: 1.08;
  border: 0;
}
.cover p { max-width: 135mm; font-size: 14pt; color: #dbeafe; }
.cover .meta { margin-top: 20mm; font-size: 10.5pt; color: #ccfbf1; }
h2, h3, h4 { break-after: avoid; page-break-after: avoid; }
h2 {
  margin: 8mm 0 3mm;
  padding: 2.5mm 0 2mm;
  color: #123b5d;
  font-size: 20pt;
  line-height: 1.16;
  border-bottom: 1.2pt solid #5eead4;
}
h2[id^="slide-"] {
  break-before: page;
  margin-top: 0;
  padding: 5mm 5mm 4mm;
  color: white;
  background: linear-gradient(120deg, #123b5d, #0f766e);
  border: 0;
  border-radius: 5px;
}
h2[id^="slide-"]::before {
  content: "TALEKORT · POWERPOINT 1:1";
  display: block;
  margin-bottom: 1.5mm;
  color: #99f6e4;
  font-size: 8.5pt;
  font-weight: 700;
  letter-spacing: .1em;
}
h2#del-b-fagligt-opslagsværk {
  break-before: page;
  padding-top: 5mm;
}
h3 { margin: 6mm 0 2mm; color: #0f5f66; font-size: 15pt; line-height: 1.2; }
h4 { margin: 4mm 0 1.5mm; color: #334155; font-size: 12pt; }
p { margin: 0 0 2.6mm; orphans: 3; widows: 3; }
ul, ol { margin: 1.5mm 0 3mm 6mm; padding-left: 5mm; }
li { margin: 0 0 1.3mm; }
li::marker { color: #0f766e; }
strong { color: #102a43; }
a { color: #086788; text-decoration: none; }
hr { border: 0; border-top: 1pt solid #cbd5e1; margin: 6mm 0; }
blockquote {
  margin: 3mm 0 4mm;
  padding: 3mm 4mm;
  color: #24445c;
  background: #ecfeff;
  border-left: 3pt solid #14b8a6;
  break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }
code {
  padding: .2mm 1mm;
  border-radius: 2px;
  color: #713f12;
  background: #fef3c7;
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: .91em;
}
pre {
  margin: 3mm 0 4mm;
  padding: 3.2mm 3.6mm;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  color: #e2e8f0;
  background: #111827;
  border-left: 3pt solid #2dd4bf;
  border-radius: 4px;
  break-inside: avoid;
}
pre code { padding: 0; color: inherit; background: transparent; font-size: 8.4pt; line-height: 1.38; }
table { width: 100%; margin: 3mm 0 5mm; border-collapse: collapse; font-size: 9.5pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { padding: 2mm; color: white; background: #155e75; text-align: left; }
td { padding: 2mm; border: .5pt solid #cbd5e1; vertical-align: top; }
tbody tr:nth-child(even) { background: #f8fafc; }
body > h2:first-of-type { margin-top: 0; }
@media screen {
  body { max-width: 210mm; margin: 0 auto; padding: 12mm; box-shadow: 0 0 20px #94a3b8; }
  .cover { margin: -12mm -12mm 12mm; }
}
"""

    return f"""<!doctype html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <section class="cover">
    <div class="eyebrow">Tiny Machine Learning · ETTML</div>
    <h1>{title}</h1>
    <p>Præsentationsflow, kerneteori, projektresultater og dokumenteret kodekort.</p>
    <div class="meta">Tabletudgave · brug dokumentets globale begrebsindeks til hurtigt opslag</div>
  </section>
  {body}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render ETTML exam notes to PDF.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--browser", help="Explicit path to Chrome/Chromium")
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    browser = find_browser(args.browser)
    if not source.is_file():
        raise SystemExit(f"Notes file was not found: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(source.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="ettml-notes-") as temp_name:
        temp_dir = Path(temp_name)
        html_path = temp_dir / "notes.html"
        profile_dir = temp_dir / "chrome-profile"
        html_path.write_text(html, encoding="utf-8")
        command = [
            str(browser),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            "--run-all-compositor-stages-before-draw",
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={output}",
            html_path.as_uri(),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if completed.returncode != 0 or not output.is_file():
            details = completed.stderr.strip() or completed.stdout.strip()
            raise SystemExit(f"PDF rendering failed: {details}")

    print(f"[OK] Wrote {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
