from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from software.pynq.overlay import AcceleratorOverlay
from software.pynq.reference import build_checkerboard, process_frame_reference
from software.pynq.registers import KernelMode


class ConvolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.overlay = AcceleratorOverlay(use_mock=True)

    def test_pass_through_matches_input(self) -> None:
        frame = build_checkerboard(16, 4)
        actual = self.overlay.vision.process_image_hw(frame, mode=KernelMode.PASS_THROUGH)
        np.testing.assert_array_equal(actual, frame)

    def test_blur_matches_reference(self) -> None:
        frame = build_checkerboard(16, 4)
        actual = self.overlay.vision.process_image_hw(frame, mode=KernelMode.BLUR)
        expected = process_frame_reference(frame, KernelMode.BLUR)
        np.testing.assert_array_equal(actual, expected)

    def test_sharpen_matches_reference(self) -> None:
        frame = build_checkerboard(16, 4)
        actual = self.overlay.vision.process_image_hw(frame, mode=KernelMode.SHARPEN)
        expected = process_frame_reference(frame, KernelMode.SHARPEN)
        np.testing.assert_array_equal(actual, expected)


if __name__ == "__main__":
    unittest.main()
