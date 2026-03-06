# PYNQ-Z2 Accelerator Suite

This project builds two hardware accelerators on the PYNQ-Z2 and drives them from Python on the ARM side. The first block is a register-controlled radix-4 Booth multiplier. The second block is a streaming 3x3 filter used for Sobel edge detection and a few other kernels.

The repo is split into hardware source, Python drivers, tests, notebooks, and small demo assets. The Python code can run against a mock backend on a normal computer, so the control path and verification flow can be tested before moving to the board.

![System overview](docs/figures/ab.png)

## Hardware and software

- Board: PYNQ-Z2 (Zynq-7020)
- Tools: Vivado, Vitis HLS, PYNQ Python
- Control path: AXI4-Lite
- Streaming path: AXI4-Stream with AXI DMA
- Host-side packages: Python 3, NumPy

## Folder layout

- `hardware/` HLS source, Vivado scripts, block design notes, and constraints
- `software/` Python drivers, mock runtime, references, and benchmarks
- `tests/` unit tests for arithmetic and image processing
- `notebooks/` short demo notebooks for the multiplier and the vision path
- `data/` sample images, saved outputs, and benchmark JSON
- `docs/` project notes, figures, and the short report
- `scripts/` helper scripts for demo runs, assets, and the PDF report

## Accelerator blocks

- `booth_multiplier`: AXI4-Lite peripheral with operand, mode, and result registers
- `conv3x3_stream`: AXI4-Stream filter with pass-through, blur, sharpen, Sobel X, Sobel Y, and Sobel magnitude modes
- `sobel_stream`: fixed-mode wrapper around the 3x3 engine for a simple dedicated Sobel IP option

## Build and run

1. Build the HLS IP with `hardware/vivado/scripts/build_hls_ip.tcl`.
2. Create the block design with `hardware/vivado/scripts/create_block_design.tcl`.
3. Generate the bitstream and copy the `.bit` and `.hwh` files into `hardware/export/`.
4. On the board, copy this repo and run the Python drivers or notebooks.
5. On a host machine without the board, use the mock backend to run tests and sample benchmarks.

For a quick software-only check:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
./scripts/run_demo.sh
```

## Results

Sample mock-backend outputs are saved in `data/output_images/` and a sample benchmark report is in `data/benchmark_results/sample_results.json`.

From the sample mock run:

- arithmetic call overhead is larger than direct CPU multiplication for small scalar cases
- the image path timing is close to the software reference because the mock backend still runs the software kernel
- real board-side numbers still need to be collected after the overlay is built

The short writeup is in `docs/project_summary.md`, and a generated PDF copy is in `docs/project_summary.pdf`.

## Notes

- Border handling for the 3x3 filter uses zero padding.
- The image path in this repo uses 8-bit grayscale frames to keep the HLS core and tests easy to follow.
- The notebook demos are short on purpose. The main control code lives in `software/pynq/`, not only in the notebooks.
