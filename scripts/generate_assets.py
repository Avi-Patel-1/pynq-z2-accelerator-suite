from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from software.pynq.benchmarks import benchmark_filter, benchmark_multiplier
from software.pynq.overlay import AcceleratorOverlay
from software.pynq.reference import build_checkerboard, build_diagonal, save_pgm
from software.pynq.registers import KernelMode


def main() -> None:
    input_dir = ROOT / "data" / "input_images"
    output_dir = ROOT / "data" / "output_images"
    benchmark_dir = ROOT / "data" / "benchmark_results"

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark_dir.mkdir(parents=True, exist_ok=True)

    checkerboard = build_checkerboard(64, 8)
    diagonal = build_diagonal(64)
    save_pgm(input_dir / "checkerboard_64.pgm", checkerboard)
    save_pgm(input_dir / "diagonal_64.pgm", diagonal)

    suite = AcceleratorOverlay(use_mock=True)
    sobel = suite.vision.process_image_hw(checkerboard, mode=KernelMode.SOBEL_MAG)
    blur = suite.vision.process_image_hw(diagonal, mode=KernelMode.BLUR)

    save_pgm(output_dir / "checkerboard_sobel_mock.pgm", sobel)
    save_pgm(output_dir / "diagonal_blur_mock.pgm", blur)

    results = {
        "multiplier": benchmark_multiplier(suite, repeat=120),
        "vision": benchmark_filter(checkerboard, suite, repeat=12),
    }
    (benchmark_dir / "sample_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
