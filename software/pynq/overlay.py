from __future__ import annotations

from pathlib import Path

from .arithmetic import ArithmeticOverlay
from .mock_runtime import MockOverlay
from .vision import VisionOverlay

try:
    from pynq import Overlay as PynqOverlay
except ImportError:  # pragma: no cover - only used on the board
    PynqOverlay = None


class AcceleratorOverlay:
    def __init__(
        self,
        bitstream_path: str | None = None,
        use_mock: bool = False,
        download: bool = True,
        arithmetic_name: str = "booth_multiplier_0",
        vision_name: str = "conv3x3_0",
        dma_name: str = "axi_dma_0",
    ) -> None:
        if use_mock or PynqOverlay is None:
            self.backend = "mock"
            self.overlay = MockOverlay()
        else:
            if bitstream_path is None:
                raise ValueError("A bitstream path is required when use_mock is False")
            self.backend = "board"
            self.overlay = PynqOverlay(str(Path(bitstream_path)), download=download)

        self.arithmetic = ArithmeticOverlay(getattr(self.overlay, arithmetic_name))
        self.vision = VisionOverlay(getattr(self.overlay, vision_name), getattr(self.overlay, dma_name))

    def describe(self) -> dict[str, str]:
        return {
            "backend": self.backend,
            "arithmetic_ip": type(self.arithmetic.ip).__name__,
            "vision_ip": type(self.vision.ip).__name__,
            "dma": type(self.vision.dma).__name__,
        }


def load_overlay(bitstream_path: str | None = None, use_mock: bool = False) -> AcceleratorOverlay:
    return AcceleratorOverlay(bitstream_path=bitstream_path, use_mock=use_mock)
