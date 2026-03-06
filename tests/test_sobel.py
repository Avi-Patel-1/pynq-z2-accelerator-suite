from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from software.pynq.overlay import AcceleratorOverlay
from software.pynq.reference import build_diagonal, process_frame_reference
from software.pynq.registers import KernelMode


class SobelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.overlay = AcceleratorOverlay(use_mock=True)

    def test_sobel_x_matches_reference(self) -> None:
        frame = build_diagonal(20)
        actual = self.overlay.vision.process_image_hw(frame, mode=KernelMode.SOBEL_X)
        expected = process_frame_reference(frame, KernelMode.SOBEL_X)
        np.testing.assert_array_equal(actual, expected)

    def test_sobel_y_matches_reference(self) -> None:
        frame = build_diagonal(20)
        actual = self.overlay.vision.process_image_hw(frame, mode=KernelMode.SOBEL_Y)
        expected = process_frame_reference(frame, KernelMode.SOBEL_Y)
        np.testing.assert_array_equal(actual, expected)

    def test_sobel_magnitude_border_stays_nonnegative(self) -> None:
        frame = build_diagonal(20)
        actual = self.overlay.vision.process_image_hw(frame, mode=KernelMode.SOBEL_MAG)
        expected = process_frame_reference(frame, KernelMode.SOBEL_MAG)
        np.testing.assert_array_equal(actual, expected)
        self.assertTrue(np.all(actual[0, :] >= 0))
        self.assertTrue(np.all(actual[:, 0] >= 0))


if __name__ == "__main__":
    unittest.main()
