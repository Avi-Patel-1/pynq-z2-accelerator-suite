# Project Summary

## Objective

The goal of this project is to build a small reusable accelerator platform on the PYNQ-Z2. The platform combines one register-mapped arithmetic block and one DMA-backed streaming image block so the software and hardware sides can be tested together instead of as separate demos.

## System architecture

The hardware side uses a Zynq processing system, AXI4-Lite for control, and AXI DMA for the streaming image path. The multiplier is controlled through MMIO registers. The 3x3 filter receives one grayscale pixel per AXI stream beat and writes one output pixel per beat back to memory through DMA.

## Arithmetic IP design

The arithmetic block is a radix-4 Booth multiplier written in HLS. It accepts two operands, a mode register, and returns a 64-bit product split across two 32-bit registers. The mode field selects 8, 16, 24, or 32-bit operation and also selects signed or unsigned arithmetic. The software driver writes the operands, sets the mode, starts the block, waits for the done bit, and reads the result.

## Streaming image IP design

The image block is a streaming 3x3 filter with zero-padded borders. A small set of runtime-selectable modes is included so the same block can be reused for pass-through, blur, sharpen, Sobel X, Sobel Y, and Sobel magnitude. The HLS core keeps two line buffers and one 3x3 window so the filter can run as a normal stream operator instead of a frame buffer kernel.

## AXI integration

Both accelerators use AXI4-Lite for configuration. The image path also uses AXI4-Stream and AXI DMA. The expected data path is PS DDR to DMA, DMA to filter IP, filter IP back to DMA, and DMA back to PS DDR. The Vivado scripts in `hardware/vivado/scripts/` set up the base project, the DMA block, the AXI control path, and the packaging step for the overlay files.

## Python control flow

The Python side is split into small driver modules. `ArithmeticOverlay` handles register writes and reads for the multiplier. `VisionOverlay` sets the image dimensions, writes the filter mode, allocates buffers, launches DMA transfers, and returns the processed frame. `AcceleratorOverlay` collects both blocks behind one object so the notebooks and tests can use a shared control style.

## Verification

The multiplier is checked with directed tests and random tests across several active widths. The vision block is checked against a NumPy reference model for pass-through, blur, sharpen, and Sobel modes. A mock MMIO and DMA backend is included so the whole Python path can run on a host machine without a board.

## Benchmark results

The sample benchmark JSON in `data/benchmark_results/sample_results.json` is generated with the mock backend. It is only meant to check the control flow and report formatting. On real hardware the multiplier should be measured against the ARM software path and the filter should be measured in frame time and FPS with DMA included in the timing.

## Limitations

- The repo does not include a checked-in bitstream because that is a build output.
- The current image path uses grayscale frames to keep the stream kernel and tests simple.
- Real board-side benchmark numbers still need to be collected after Vivado and HLS builds are complete.

## Future work

- add a MAC or FIR block to the arithmetic side
- add tiled image support for larger frames
- add a live HDMI or camera demo path
- compare HLS pragmas and resource use after synthesis
