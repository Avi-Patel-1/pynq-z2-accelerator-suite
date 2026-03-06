from __future__ import annotations

from pathlib import Path

import numpy as np

from .registers import CODE_TO_WIDTH, KernelMode, SIGNED_MODE_BIT, WIDTH_TO_CODE


def build_multiplier_mode(width: int = 32, signed_mode: bool = True) -> int:
    if width not in WIDTH_TO_CODE:
        raise ValueError(f"Unsupported width: {width}")
    return WIDTH_TO_CODE[width] | (SIGNED_MODE_BIT if signed_mode else 0)


def width_from_mode(mode: int) -> int:
    return CODE_TO_WIDTH[mode & 0x3]


def signed_from_mode(mode: int) -> bool:
    return bool(mode & SIGNED_MODE_BIT)


def pack_operand(value: int, width: int) -> int:
    return value & ((1 << width) - 1)


def unpack_operand(raw_value: int, width: int, signed_mode: bool) -> int:
    masked = pack_operand(raw_value, width)
    if signed_mode and masked & (1 << (width - 1)):
        return masked - (1 << width)
    return masked


def reference_multiplier(value_a: int, value_b: int, width: int, signed_mode: bool) -> int:
    norm_a = unpack_operand(value_a, width, signed_mode)
    norm_b = unpack_operand(value_b, width, signed_mode)
    return norm_a * norm_b


def reference_multiplier_from_mode(raw_a: int, raw_b: int, mode: int) -> int:
    width = width_from_mode(mode)
    signed_mode = signed_from_mode(mode)
    return reference_multiplier(raw_a, raw_b, width, signed_mode)


def pack_result_words(value: int) -> tuple[int, int]:
    raw = value & ((1 << 64) - 1)
    return raw & 0xFFFFFFFF, (raw >> 32) & 0xFFFFFFFF


def unpack_result_words(result_lo: int, result_hi: int, signed_mode: bool) -> int:
    raw = (result_hi << 32) | result_lo
    if signed_mode and raw & (1 << 63):
        return raw - (1 << 64)
    return raw


def ensure_grayscale_frame(frame: np.ndarray) -> np.ndarray:
    array = np.asarray(frame, dtype=np.uint8)
    if array.ndim != 2:
        raise ValueError("Expected a 2D grayscale frame")
    return array


def _apply_kernel(image: np.ndarray, kernel: np.ndarray, divisor: int = 1, absolute_value: bool = False) -> np.ndarray:
    frame = ensure_grayscale_frame(image)
    padded = np.pad(frame.astype(np.int16), ((1, 1), (1, 1)), mode="constant")
    output = np.zeros_like(frame, dtype=np.uint8)

    for row in range(frame.shape[0]):
        for col in range(frame.shape[1]):
            window = padded[row : row + 3, col : col + 3]
            value = int(np.sum(window * kernel))
            if divisor > 1:
                value //= divisor
            if absolute_value:
                value = abs(value)
            output[row, col] = np.uint8(max(0, min(255, value)))

    return output


def process_frame_reference(image: np.ndarray, mode: int | KernelMode, threshold: int = 128) -> np.ndarray:
    frame = ensure_grayscale_frame(image)
    kernel_mode = KernelMode(int(mode))

    if kernel_mode == KernelMode.PASS_THROUGH:
        return frame.copy()
    if kernel_mode == KernelMode.BLUR:
        kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.int16)
        return _apply_kernel(frame, kernel, divisor=9)
    if kernel_mode == KernelMode.SHARPEN:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.int16)
        return _apply_kernel(frame, kernel)
    if kernel_mode == KernelMode.SOBEL_X:
        kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.int16)
        return _apply_kernel(frame, kernel, absolute_value=True)
    if kernel_mode == KernelMode.SOBEL_Y:
        kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.int16)
        return _apply_kernel(frame, kernel, absolute_value=True)
    if kernel_mode == KernelMode.SOBEL_MAG:
        sobel_x = process_frame_reference(frame, KernelMode.SOBEL_X, threshold)
        sobel_y = process_frame_reference(frame, KernelMode.SOBEL_Y, threshold)
        magnitude = sobel_x.astype(np.uint16) + sobel_y.astype(np.uint16)
        return np.clip(magnitude, 0, 255).astype(np.uint8)
    if kernel_mode == KernelMode.THRESHOLD:
        return np.where(frame >= threshold, 255, 0).astype(np.uint8)
    raise ValueError(f"Unsupported mode: {kernel_mode}")


def build_checkerboard(size: int = 64, tile: int = 8) -> np.ndarray:
    rows = np.arange(size) // tile
    cols = np.arange(size) // tile
    pattern = (rows[:, None] + cols[None, :]) % 2
    return np.where(pattern == 0, 48, 216).astype(np.uint8)


def build_diagonal(size: int = 64) -> np.ndarray:
    frame = np.zeros((size, size), dtype=np.uint8)
    for row in range(size):
        for col in range(size):
            if abs(row - col) <= 2:
                frame[row, col] = 255
            else:
                frame[row, col] = (row * 3 + col * 2) % 160
    return frame


def save_pgm(path: str | Path, frame: np.ndarray) -> None:
    image = ensure_grayscale_frame(frame)
    target = Path(path)
    header = f"P5\n{image.shape[1]} {image.shape[0]}\n255\n".encode("ascii")
    target.write_bytes(header + image.tobytes())


def load_pgm(path: str | Path) -> np.ndarray:
    payload = Path(path).read_bytes()
    if not payload.startswith(b"P5"):
        raise ValueError("Only binary PGM (P5) files are supported")

    body = payload[2:].lstrip()
    tokens: list[bytes] = []
    index = 0
    while len(tokens) < 3:
        if body[index : index + 1] == b"#":
            while body[index : index + 1] not in {b"\n", b""}:
                index += 1
        elif body[index : index + 1].isspace():
            index += 1
        else:
            start = index
            while body[index : index + 1] and not body[index : index + 1].isspace():
                index += 1
            tokens.append(body[start:index])
    width = int(tokens[0])
    height = int(tokens[1])
    max_value = int(tokens[2])
    if max_value != 255:
        raise ValueError("Expected an 8-bit PGM with max value 255")
    pixel_data = body[index:].lstrip()
    return np.frombuffer(pixel_data[: width * height], dtype=np.uint8).reshape((height, width)).copy()
