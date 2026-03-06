from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "project_summary.md"
TARGET = ROOT / "docs" / "project_summary.pdf"

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT_MARGIN = 54
TOP_MARGIN = 738
LINE_HEIGHT = 14
WRAP_WIDTH = 88
LINES_PER_PAGE = 48


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def markdown_to_lines(markdown: str) -> list[str]:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            lines.append("")
            continue
        if raw_line.startswith("## "):
            lines.append(stripped[3:].upper())
            lines.append("")
            continue
        if raw_line.startswith("# "):
            lines.append(stripped[2:].upper())
            lines.append("")
            continue
        if raw_line.startswith("- "):
            wrapped = textwrap.wrap("  - " + stripped[2:], width=WRAP_WIDTH) or [""]
        else:
            wrapped = textwrap.wrap(stripped, width=WRAP_WIDTH) or [""]
        lines.extend(wrapped)
    return lines


def split_pages(lines: list[str]) -> list[list[str]]:
    return [lines[index : index + LINES_PER_PAGE] for index in range(0, len(lines), LINES_PER_PAGE)]


def build_pdf(pages: list[list[str]]) -> bytes:
    objects: list[str] = []

    def add_object(payload: str) -> int:
        objects.append(payload)
        return len(objects)

    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    pages_id = add_object("")
    page_ids: list[int] = []

    for page_lines in pages:
        content_stream = ["BT", "/F1 11 Tf", f"{LINE_HEIGHT} TL", f"{LEFT_MARGIN} {TOP_MARGIN} Td"]
        first_line = True
        for line in page_lines:
            if not first_line:
                content_stream.append("T*")
            content_stream.append(f"({escape_pdf_text(line)}) Tj")
            first_line = False
        content_stream.append("ET")
        content_payload = "\n".join(content_stream) + "\n"
        content_id = add_object(f"<< /Length {len(content_payload.encode('latin-1'))} >>\nstream\n{content_payload}endstream")
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>"
    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

    output = ["%PDF-1.4\n"]
    offsets = [0]

    for index, payload in enumerate(objects, start=1):
        offsets.append(sum(len(chunk.encode("latin-1")) for chunk in output))
        output.append(f"{index} 0 obj\n{payload}\nendobj\n")

    xref_offset = sum(len(chunk.encode("latin-1")) for chunk in output)
    output.append(f"xref\n0 {len(objects) + 1}\n")
    output.append("0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.append(f"{offset:010d} 00000 n \n")
    output.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    )

    return "".join(output).encode("latin-1")


def main() -> None:
    lines = markdown_to_lines(SOURCE.read_text(encoding="utf-8"))
    pdf_bytes = build_pdf(split_pages(lines))
    TARGET.write_bytes(pdf_bytes)


if __name__ == "__main__":
    main()
