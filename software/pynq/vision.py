from __future__ import annotations

from time import perf_counter_ns

import numpy as np

from .dma_utils import allocate_buffer, copy_frame, to_numpy
from .reference import ensure_grayscale_frame, load_pgm, process_frame_reference, save_pgm
from .registers import (
    BorderMode,
    KernelMode,
    VISION_BORDER,
    VISION_CONTROL,
    VISION_HEIGHT,
    VISION_MODE,
    VISION_STRIDE,
    VISION_THRESHOLD,
    VISION_WIDTH,
)


class VisionOverlay:
    def __init__(self, ip: object, dma: object, allocator: object | None = None) -> None:
        self.ip = ip
        self.dma = dma
        self.allocator = allocator

    def configure(
        self,
        width: int,
        height: int,
        mode: int | KernelMode,
        threshold: int = 128,
        border: int | BorderMode = BorderMode.ZERO,
    ) -> None:
        self.ip.write(VISION_WIDTH, int(width))
        self.ip.write(VISION_HEIGHT, int(height))
        self.ip.write(VISION_STRIDE, int(width))
        self.ip.write(VISION_MODE, int(mode))
        self.ip.write(VISION_THRESHOLD, int(threshold) & 0xFF)
        self.ip.write(VISION_BORDER, int(border))

    def process_image_hw(
        self,
        frame: np.ndarray,
        mode: int | KernelMode = KernelMode.SOBEL_MAG,
        threshold: int = 128,
        return_timing: bool = False,
    ) -> np.ndarray | tuple[np.ndarray, dict[str, int]]:
        image = ensure_grayscale_frame(frame)
        height, width = image.shape
        self.configure(width=width, height=height, mode=mode, threshold=threshold)

        input_buffer = allocate_buffer(image.shape, np.uint8, allocator=self.allocator)
        output_buffer = allocate_buffer(image.shape, np.uint8, allocator=self.allocator)

        prep_start_ns = perf_counter_ns()
        copy_frame(input_buffer, image)
        if hasattr(input_buffer, "flush"):
            input_buffer.flush()
        prep_done_ns = perf_counter_ns()

        self.dma.recvchannel.transfer(output_buffer)
        self.dma.sendchannel.transfer(input_buffer)
        self.ip.write(VISION_CONTROL, 0x1)
        self.dma.sendchannel.wait()
        self.dma.recvchannel.wait()
        if hasattr(output_buffer, "invalidate"):
            output_buffer.invalidate()
        device_done_ns = perf_counter_ns()

        result = to_numpy(output_buffer)
        copy_done_ns = perf_counter_ns()
        timings = {
            "buffer_prep_ns": prep_done_ns - prep_start_ns,
            "device_ns": device_done_ns - prep_done_ns,
            "copy_out_ns": copy_done_ns - device_done_ns,
            "total_ns": copy_done_ns - prep_start_ns,
        }

        if return_timing:
            return result, timings
        return result

    def process_image_sw(self, frame: np.ndarray, mode: int | KernelMode, threshold: int = 128) -> np.ndarray:
        return process_frame_reference(frame, mode, threshold)

    @staticmethod
    def load_gray_image(path: str) -> np.ndarray:
        return load_pgm(path)

    @staticmethod
    def save_gray_image(path: str, frame: np.ndarray) -> None:
        save_pgm(path, frame)


def process_image_hw(
    overlay: VisionOverlay,
    frame: np.ndarray,
    mode: int | KernelMode = KernelMode.SOBEL_MAG,
    threshold: int = 128,
) -> np.ndarray:
    return overlay.process_image_hw(frame, mode=mode, threshold=threshold)
