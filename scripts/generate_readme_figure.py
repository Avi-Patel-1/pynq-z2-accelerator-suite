from __future__ import annotations

import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "docs" / "figures" / "system_overview.png"
WIDTH = 920
HEIGHT = 320


def rgb(r: int, g: int, b: int) -> tuple[int, int, int]:
    return r, g, b


def make_canvas(width: int, height: int, color: tuple[int, int, int]) -> list[list[list[int]]]:
    row = [[color[0], color[1], color[2]] for _ in range(width)]
    return [[pixel[:] for pixel in row] for _ in range(height)]


def fill_rect(canvas: list[list[list[int]]], x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    for y in range(max(0, y0), min(len(canvas), y1)):
        row = canvas[y]
        for x in range(max(0, x0), min(len(row), x1)):
            row[x][0], row[x][1], row[x][2] = color


def draw_border(canvas: list[list[list[int]]], x0: int, y0: int, x1: int, y1: int, thickness: int, color: tuple[int, int, int]) -> None:
    fill_rect(canvas, x0, y0, x1, y0 + thickness, color)
    fill_rect(canvas, x0, y1 - thickness, x1, y1, color)
    fill_rect(canvas, x0, y0, x0 + thickness, y1, color)
    fill_rect(canvas, x1 - thickness, y0, x1, y1, color)


def draw_line(canvas: list[list[list[int]]], x0: int, y0: int, x1: int, y1: int, thickness: int, color: tuple[int, int, int]) -> None:
    if x0 == x1:
        fill_rect(canvas, x0 - thickness // 2, min(y0, y1), x1 + thickness // 2 + 1, max(y0, y1) + 1, color)
        return
    if y0 == y1:
        fill_rect(canvas, min(x0, x1), y0 - thickness // 2, max(x0, x1) + 1, y1 + thickness // 2 + 1, color)
        return


def draw_text_block(canvas: list[list[list[int]]], x: int, y: int, text: str, color: tuple[int, int, int], scale: int = 2) -> None:
    font = {
        "A": ["0110", "1001", "1111", "1001", "1001"],
        "B": ["1110", "1001", "1110", "1001", "1110"],
        "C": ["0111", "1000", "1000", "1000", "0111"],
        "D": ["1110", "1001", "1001", "1001", "1110"],
        "E": ["1111", "1000", "1110", "1000", "1111"],
        "G": ["0111", "1000", "1011", "1001", "0111"],
        "H": ["1001", "1001", "1111", "1001", "1001"],
        "I": ["111", "010", "010", "010", "111"],
        "L": ["1000", "1000", "1000", "1000", "1111"],
        "M": ["10001", "11011", "10101", "10001", "10001"],
        "O": ["0110", "1001", "1001", "1001", "0110"],
        "P": ["1110", "1001", "1110", "1000", "1000"],
        "R": ["1110", "1001", "1110", "1010", "1001"],
        "S": ["0111", "1000", "0110", "0001", "1110"],
        "T": ["11111", "00100", "00100", "00100", "00100"],
        "V": ["10001", "10001", "10001", "01010", "00100"],
        "X": ["1001", "1001", "0110", "1001", "1001"],
        "Y": ["10001", "01010", "00100", "00100", "00100"],
        "3": ["111", "001", "111", "001", "111"],
        " ": ["0", "0", "0", "0", "0"],
        "-": ["000", "000", "111", "000", "000"],
    }
    cursor_x = x
    for char in text.upper():
        glyph = font.get(char, font[" "])
        glyph_width = len(glyph[0])
        for row_index, row_bits in enumerate(glyph):
            for col_index, bit in enumerate(row_bits):
                if bit == "1":
                    fill_rect(
                        canvas,
                        cursor_x + col_index * scale,
                        y + row_index * scale,
                        cursor_x + (col_index + 1) * scale,
                        y + (row_index + 1) * scale,
                        color,
                    )
        cursor_x += (glyph_width + 1) * scale


def write_png(path: Path, canvas: list[list[list[int]]]) -> None:
    raw_rows = []
    for row in canvas:
        raw_rows.append(b"\x00" + bytes(channel for pixel in row for channel in pixel))
    raw = b"".join(raw_rows)
    compressed = zlib.compress(raw, level=9)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> None:
    bg = rgb(244, 241, 234)
    dark = rgb(40, 44, 52)
    blue = rgb(217, 231, 255)
    tan = rgb(255, 240, 204)
    green = rgb(223, 247, 226)
    orange = rgb(252, 224, 213)
    purple = rgb(239, 225, 255)

    canvas = make_canvas(WIDTH, HEIGHT, bg)

    fill_rect(canvas, 40, 40, 220, 150, blue)
    draw_border(canvas, 40, 40, 220, 150, 3, dark)
    fill_rect(canvas, 300, 40, 520, 150, tan)
    draw_border(canvas, 300, 40, 520, 150, 3, dark)
    fill_rect(canvas, 600, 40, 860, 150, green)
    draw_border(canvas, 600, 40, 860, 150, 3, dark)
    fill_rect(canvas, 300, 200, 520, 290, orange)
    draw_border(canvas, 300, 200, 520, 290, 3, dark)
    fill_rect(canvas, 600, 190, 860, 300, purple)
    draw_border(canvas, 600, 190, 860, 300, 3, dark)

    draw_line(canvas, 220, 95, 300, 95, 4, dark)
    draw_line(canvas, 520, 95, 600, 95, 4, dark)
    draw_line(canvas, 130, 150, 130, 245, 4, dark)
    draw_line(canvas, 220, 245, 300, 245, 4, dark)
    draw_line(canvas, 520, 245, 600, 245, 4, dark)

    draw_text_block(canvas, 103, 74, "PS", dark, scale=5)
    draw_text_block(canvas, 62, 112, "ARM DDR", dark, scale=3)
    draw_text_block(canvas, 318, 76, "AXI4-LITE", dark, scale=4)
    draw_text_block(canvas, 332, 114, "CONTROL", dark, scale=3)
    draw_text_block(canvas, 635, 74, "BOOTH", dark, scale=4)
    draw_text_block(canvas, 625, 112, "MULTIPLIER", dark, scale=3)
    draw_text_block(canvas, 374, 228, "AXI DMA", dark, scale=4)
    draw_text_block(canvas, 638, 220, "3X3", dark, scale=5)
    draw_text_block(canvas, 655, 258, "FILTER", dark, scale=4)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_png(OUT_PATH, canvas)


if __name__ == "__main__":
    main()
