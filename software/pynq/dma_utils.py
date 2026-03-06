from __future__ import annotations

from typing import Callable

import numpy as np

try:
    from pynq import allocate as pynq_allocate
except ImportError:  # pragma: no cover - only used on the board
    pynq_allocate = None


Allocator = Callable[..., np.ndarray]


def allocate_buffer(shape: tuple[int, ...], dtype: np.dtype = np.uint8, allocator: Allocator | None = None) -> np.ndarray:
    if allocator is not None:
        return allocator(shape=shape, dtype=dtype)
    if pynq_allocate is not None:
        return pynq_allocate(shape=shape, dtype=dtype)
    return np.zeros(shape, dtype=dtype)


def copy_frame(target: np.ndarray, source: np.ndarray) -> None:
    target[...] = np.asarray(source, dtype=target.dtype)


def to_numpy(buffer: np.ndarray) -> np.ndarray:
    return np.array(buffer, copy=True)
