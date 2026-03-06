from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter_ns

import numpy as np

from .overlay import AcceleratorOverlay
from .reference import build_multiplier_mode, load_pgm, process_frame_reference, reference_multiplier, signed_from_mode, width_from_mode
from .registers import KernelMode


def _average(values: list[int]) -> int:
    return int(sum(values) / max(1, len(values)))


def benchmark_multiplier(
    overlay: AcceleratorOverlay | None = None,
    repeat: int = 200,
    use_mock: bool = True,
) -> dict[str, object]:
    suite = overlay or AcceleratorOverlay(use_mock=use_mock)
    test_cases = [
        {"a": 13, "b": 7, "mode": build_multiplier_mode(8, False)},
        {"a": -19, "b": 25, "mode": build_multiplier_mode(8, True)},
        {"a": 511, "b": 127, "mode": build_multiplier_mode(16, False)},
        {"a": -321, "b": -17, "mode": build_multiplier_mode(16, True)},
        {"a": 0x00FFFF, "b": 321, "mode": build_multiplier_mode(24, False)},
        {"a": -12345, "b": 23456, "mode": build_multiplier_mode(32, True)},
    ]
    rows: list[dict[str, int | bool]] = []

    for case in test_cases:
        cpu_samples: list[int] = []
        hw_samples: list[int] = []
        width = width_from_mode(case["mode"])
        signed_mode = signed_from_mode(case["mode"])

        for _ in range(repeat):
            start_ns = perf_counter_ns()
            reference_multiplier(case["a"], case["b"], width, signed_mode)
            cpu_samples.append(perf_counter_ns() - start_ns)

        for _ in range(repeat):
            _, latency_ns = suite.arithmetic.multiply(
                case["a"],
                case["b"],
                width=width,
                signed_mode=signed_mode,
                return_timing=True,
            )
            hw_samples.append(latency_ns)

        rows.append(
            {
                "width": width,
                "signed": signed_mode,
                "cpu_avg_ns": _average(cpu_samples),
                "hw_avg_ns": _average(hw_samples),
                "speedup_vs_call_path": round(_average(cpu_samples) / max(1, _average(hw_samples)), 4),
            }
        )

    return {"backend": suite.backend, "repeat": repeat, "rows": rows}


def benchmark_filter(
    frame: np.ndarray,
    overlay: AcceleratorOverlay | None = None,
    repeat: int = 20,
    use_mock: bool = True,
) -> dict[str, object]:
    suite = overlay or AcceleratorOverlay(use_mock=use_mock)
    rows: list[dict[str, int | float | str]] = []
    modes = [KernelMode.PASS_THROUGH, KernelMode.BLUR, KernelMode.SHARPEN, KernelMode.SOBEL_MAG]

    for mode in modes:
        cpu_samples: list[int] = []
        hw_total_samples: list[int] = []
        hw_device_samples: list[int] = []

        for _ in range(repeat):
            start_ns = perf_counter_ns()
            process_frame_reference(frame, mode)
            cpu_samples.append(perf_counter_ns() - start_ns)

        for _ in range(repeat):
            _, timing = suite.vision.process_image_hw(frame, mode=mode, return_timing=True)
            hw_total_samples.append(timing["total_ns"])
            hw_device_samples.append(timing["device_ns"])

        avg_total = _average(hw_total_samples)
        rows.append(
            {
                "mode": mode.name.lower(),
                "cpu_avg_ns": _average(cpu_samples),
                "hw_total_avg_ns": avg_total,
                "hw_device_avg_ns": _average(hw_device_samples),
                "fps_from_total": round(1_000_000_000 / max(1, avg_total), 2),
            }
        )

    return {
        "backend": suite.backend,
        "shape": list(frame.shape),
        "repeat": repeat,
        "rows": rows,
    }


def _print_multiplier_summary(result: dict[str, object]) -> None:
    print("Multiplier benchmark")
    for row in result["rows"]:
        print(
            "  width={width:>2} signed={signed:<5} cpu={cpu_avg_ns:>8} ns hw_call={hw_avg_ns:>8} ns".format(
                **row
            )
        )


def _print_filter_summary(result: dict[str, object]) -> None:
    print("Filter benchmark")
    for row in result["rows"]:
        print(
            "  mode={mode:<12} cpu={cpu_avg_ns:>8} ns hw_total={hw_total_avg_ns:>8} ns fps={fps_from_total:>7}".format(
                **row
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run sample benchmarks for the PYNQ-Z2 accelerator suite.")
    parser.add_argument("--bitstream", default=None, help="Path to the PYNQ overlay bitstream.")
    parser.add_argument("--image", default=None, help="Path to a grayscale PGM image.")
    parser.add_argument("--out", default=None, help="Optional path to save benchmark JSON.")
    parser.add_argument("--mock", action="store_true", help="Use the mock backend.")
    parser.add_argument("--repeat-mul", type=int, default=200, help="Repeat count for multiplier timing.")
    parser.add_argument("--repeat-vision", type=int, default=20, help="Repeat count for filter timing.")
    args = parser.parse_args()

    suite = AcceleratorOverlay(bitstream_path=args.bitstream, use_mock=args.mock or args.bitstream is None)
    image_path = Path(args.image) if args.image else None
    if image_path is None:
        raise SystemExit("Please pass --image with a grayscale PGM file")

    frame = load_pgm(image_path)
    multiplier_result = benchmark_multiplier(suite, repeat=args.repeat_mul, use_mock=suite.backend == "mock")
    filter_result = benchmark_filter(frame, suite, repeat=args.repeat_vision, use_mock=suite.backend == "mock")

    _print_multiplier_summary(multiplier_result)
    _print_filter_summary(filter_result)

    if args.out:
        payload = {
            "multiplier": multiplier_result,
            "vision": filter_result,
        }
        Path(args.out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
