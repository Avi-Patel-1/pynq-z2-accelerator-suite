#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
export PYTHONPATH="$ROOT_DIR"

python3 -m software.pynq.benchmarks \
  --mock \
  --image "$ROOT_DIR/data/input_images/checkerboard_64.pgm" \
  --out "$ROOT_DIR/data/benchmark_results/sample_results.json"
