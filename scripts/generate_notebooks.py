from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def markdown_cell(lines: list[str]) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": [line if line.endswith("\n") else line + "\n" for line in lines]}


def code_cell(lines: list[str]) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line if line.endswith("\n") else line + "\n" for line in lines],
    }


def write_notebook(path: Path, cells: list[dict[str, object]]) -> None:
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")


def build_arithmetic_notebook() -> list[dict[str, object]]:
    return [
        markdown_cell(
            [
                "# Tutorial: Arithmetic IP Demo",
                "",
                "Audience:",
                "- Students testing the Booth multiplier before or after loading the overlay on the board.",
                "",
                "Prerequisites:",
                "- Python 3 with NumPy.",
                "- This repo on the board or on a host machine.",
                "",
                "Learning goals:",
                "- Load the overlay helper.",
                "- Run a few multiplier transactions.",
                "- Check a small benchmark table.",
            ]
        ),
        markdown_cell(
            [
                "## Setup",
                "",
                "Use the mock backend first. Change `use_mock=True` to a real bitstream path after the Vivado build is done.",
            ]
        ),
        code_cell(
            [
                "from pathlib import Path",
                "import sys",
                "",
                "repo_root = Path.cwd()",
                "if not (repo_root / 'software').exists():",
                "    repo_root = repo_root.parent",
                "if str(repo_root) not in sys.path:",
                "    sys.path.insert(0, str(repo_root))",
                "",
                "from software.pynq.overlay import AcceleratorOverlay",
                "from software.pynq.arithmetic import run_multiplier_test",
                "from software.pynq.benchmarks import benchmark_multiplier",
            ]
        ),
        markdown_cell(["## Run a few transactions"]),
        code_cell(
            [
                "suite = AcceleratorOverlay(use_mock=True)",
                "vectors = [(7, 9, 8, False), (-5, 12, 8, True), (-12345, 23456, 32, True)]",
                "results = []",
                "for a, b, width, signed_mode in vectors:",
                "    product = suite.arithmetic.multiply(a, b, width=width, signed_mode=signed_mode)",
                "    results.append((a, b, width, signed_mode, product))",
                "results",
            ]
        ),
        markdown_cell(["## Run the directed test set"]),
        code_cell(
            [
                "run_multiplier_test(overlay=suite.arithmetic)",
            ]
        ),
        markdown_cell(["## Benchmark the call path"]),
        code_cell(
            [
                "benchmark_multiplier(suite, repeat=50)",
            ]
        ),
        markdown_cell(
            [
                "## Move to the board",
                "",
                "After the overlay files are copied into `hardware/export/`, change the setup cell to:",
                "",
                "`suite = AcceleratorOverlay(bitstream_path='hardware/export/pynq_z2_accel.bit', use_mock=False)`",
            ]
        ),
    ]


def build_vision_notebook() -> list[dict[str, object]]:
    return [
        markdown_cell(
            [
                "# Tutorial: Vision IP Demo",
                "",
                "Audience:",
                "- Students testing the 3x3 filter path before switching to the board.",
                "",
                "Prerequisites:",
                "- Python 3 with NumPy.",
                "- Sample PGM images in `data/input_images/`.",
                "",
                "Learning goals:",
                "- Load a sample frame.",
                "- Push it through the filter helper.",
                "- Compare the hardware path against the software reference.",
            ]
        ),
        markdown_cell(["## Setup"]),
        code_cell(
            [
                "from pathlib import Path",
                "import sys",
                "",
                "repo_root = Path.cwd()",
                "if not (repo_root / 'software').exists():",
                "    repo_root = repo_root.parent",
                "if str(repo_root) not in sys.path:",
                "    sys.path.insert(0, str(repo_root))",
                "",
                "from software.pynq.overlay import AcceleratorOverlay",
                "from software.pynq.benchmarks import benchmark_filter",
                "from software.pynq.reference import load_pgm, process_frame_reference",
                "from software.pynq.registers import KernelMode",
            ]
        ),
        markdown_cell(["## Load a test image and run the Sobel mode"]),
        code_cell(
            [
                "suite = AcceleratorOverlay(use_mock=True)",
                "image_path = repo_root / 'data' / 'input_images' / 'checkerboard_64.pgm'",
                "frame = load_pgm(image_path)",
                "hw_edges = suite.vision.process_image_hw(frame, mode=KernelMode.SOBEL_MAG)",
                "sw_edges = process_frame_reference(frame, KernelMode.SOBEL_MAG)",
                "hw_edges.shape, int(hw_edges.max())",
            ]
        ),
        markdown_cell(["## Check that the mock hardware path matches the software reference"]),
        code_cell(
            [
                "bool((hw_edges == sw_edges).all())",
            ]
        ),
        markdown_cell(["## Save one output image"]),
        code_cell(
            [
                "out_path = repo_root / 'data' / 'output_images' / 'notebook_sobel_output.pgm'",
                "suite.vision.save_gray_image(out_path, hw_edges)",
                "out_path",
            ]
        ),
        markdown_cell(["## Benchmark the filter path"]),
        code_cell(
            [
                "benchmark_filter(frame, suite, repeat=8)",
            ]
        ),
    ]


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    write_notebook(NOTEBOOK_DIR / "arithmetic_demo.ipynb", build_arithmetic_notebook())
    write_notebook(NOTEBOOK_DIR / "vision_demo.ipynb", build_vision_notebook())


if __name__ == "__main__":
    main()
