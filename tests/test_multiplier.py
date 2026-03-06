from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from software.pynq.arithmetic import run_multiplier_test
from software.pynq.overlay import AcceleratorOverlay
from software.pynq.reference import reference_multiplier


class MultiplierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.overlay = AcceleratorOverlay(use_mock=True)

    def test_directed_vectors(self) -> None:
        report = run_multiplier_test(overlay=self.overlay.arithmetic)
        self.assertEqual(report["failed"], 0)

    def test_random_signed_and_unsigned_cases(self) -> None:
        rng = random.Random(21)
        widths = [8, 16, 24, 32]

        for width in widths:
            max_unsigned = (1 << width) - 1
            min_signed = -(1 << (width - 1))
            max_signed = (1 << (width - 1)) - 1

            for signed_mode in (False, True):
                for _ in range(40):
                    if signed_mode:
                        operand_a = rng.randint(min_signed, max_signed)
                        operand_b = rng.randint(min_signed, max_signed)
                    else:
                        operand_a = rng.randint(0, max_unsigned)
                        operand_b = rng.randint(0, max_unsigned)

                    actual = self.overlay.arithmetic.multiply(operand_a, operand_b, width=width, signed_mode=signed_mode)
                    expected = reference_multiplier(operand_a, operand_b, width, signed_mode)
                    self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
