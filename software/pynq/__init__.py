__all__ = [
    "AcceleratorOverlay",
    "ArithmeticOverlay",
    "VisionOverlay",
    "benchmark_filter",
    "benchmark_multiplier",
    "load_overlay",
    "process_image_hw",
    "run_multiplier_test",
]


def __getattr__(name: str):
    if name in {"AcceleratorOverlay", "load_overlay"}:
        from .overlay import AcceleratorOverlay, load_overlay

        mapping = {
            "AcceleratorOverlay": AcceleratorOverlay,
            "load_overlay": load_overlay,
        }
        return mapping[name]
    if name in {"ArithmeticOverlay", "run_multiplier_test"}:
        from .arithmetic import ArithmeticOverlay, run_multiplier_test

        mapping = {
            "ArithmeticOverlay": ArithmeticOverlay,
            "run_multiplier_test": run_multiplier_test,
        }
        return mapping[name]
    if name in {"VisionOverlay", "process_image_hw"}:
        from .vision import VisionOverlay, process_image_hw

        mapping = {
            "VisionOverlay": VisionOverlay,
            "process_image_hw": process_image_hw,
        }
        return mapping[name]
    if name in {"benchmark_filter", "benchmark_multiplier"}:
        from .benchmarks import benchmark_filter, benchmark_multiplier

        mapping = {
            "benchmark_filter": benchmark_filter,
            "benchmark_multiplier": benchmark_multiplier,
        }
        return mapping[name]
    raise AttributeError(name)
