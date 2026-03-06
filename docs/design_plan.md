# Design Plan

## Refined plan

### Phase 1 - Setup

- create the repo layout
- define register maps for the arithmetic and vision IP blocks
- keep one Python control style across both accelerators
- add sample images and a mock backend so tests can run off-board

### Phase 2 - Arithmetic path

- implement a radix-4 Booth multiplier in HLS
- expose operands, mode, result, and status through AXI4-Lite
- add a Python MMIO driver
- verify signed and unsigned operation across several widths
- compare hardware call time against a CPU baseline

### Phase 3 - Vision path

- implement a streaming 3x3 filter in HLS
- support pass-through, blur, sharpen, Sobel X, Sobel Y, and Sobel magnitude
- connect the block through AXI DMA
- verify zero-padded border handling against a NumPy reference
- measure frame time and rough FPS

### Phase 4 - Platform cleanup

- wrap both accelerators in one overlay helper
- keep register offsets in one file
- add simple benchmark functions and demo notebooks
- save a few sample outputs for the repo

### Phase 5 - Documentation

- write a short README
- write a short project summary
- keep build notes for Vivado and HLS
- include a few small figures showing the system layout and the control flow

## Repo structure

```text
pynq-z2-accelerator-suite/
  README.md
  hardware/
    hls/
      booth_multiplier/
      conv3x3/
      sobel/
      common/
    vivado/
      scripts/
    bd/
    constraints/
    export/
  software/
    pynq/
  notebooks/
  tests/
  data/
    input_images/
    output_images/
    benchmark_results/
  docs/
    figures/
  scripts/
```

## Arithmetic IP spec

Block name: `booth_multiplier`

Purpose:
- multiply two 32-bit register inputs
- support 8, 16, 24, and 32-bit active widths
- support signed or unsigned mode
- return the product in two 32-bit result registers

Register map:

| Offset | Name | Notes |
| --- | --- | --- |
| `0x00` | control | HLS `ap_ctrl_hs`, start/done/idle/ready |
| `0x10` | operand_a | low 32 bits used |
| `0x18` | operand_b | low 32 bits used |
| `0x20` | mode | width select in bits `[1:0]`, signed in bit `8` |
| `0x28` | result_lo | low 32 bits of product |
| `0x30` | result_hi | high 32 bits of product |
| `0x38` | status | bit `0` valid, bit `1` signed mode, bits `[9:8]` width code |

Mode encoding:

| Width code | Active width |
| --- | --- |
| `0` | 8-bit |
| `1` | 16-bit |
| `2` | 24-bit |
| `3` | 32-bit |

## Vision IP spec

Block name: `conv3x3_stream`

Purpose:
- process one grayscale video stream using AXI4-Stream
- accept runtime kernel selection over AXI4-Lite
- stay DMA-friendly by preserving frame order and asserting `TLAST` on the last pixel

Streaming assumptions:
- one 8-bit pixel per beat
- frame size is provided by software
- border handling uses zero padding

Register map:

| Offset | Name | Notes |
| --- | --- | --- |
| `0x00` | control | HLS `ap_ctrl_hs`, start/done/idle/ready |
| `0x10` | width | active frame width |
| `0x18` | height | active frame height |
| `0x20` | stride | bytes per row, usually same as width |
| `0x28` | mode | kernel mode select |
| `0x30` | threshold | used only in threshold mode |
| `0x38` | border | `0` for zero padding |

Kernel modes:

| Value | Mode |
| --- | --- |
| `0` | pass-through |
| `1` | blur |
| `2` | sharpen |
| `3` | Sobel X |
| `4` | Sobel Y |
| `5` | Sobel magnitude |
| `6` | threshold |

## Python driver skeleton

Main classes:

- `ArithmeticOverlay`
  - write operands
  - start the IP
  - poll the done bit
  - read back the 64-bit result
- `VisionOverlay`
  - configure width, height, and kernel mode
  - allocate DMA buffers
  - push a frame through AXI DMA
  - collect the processed frame
- `AcceleratorOverlay`
  - load the overlay
  - expose `arithmetic` and `vision` helper objects
  - fall back to a mock runtime when PYNQ is not available

Driver helper functions:

- `run_multiplier_test()`
- `process_image_hw()`
- `benchmark_multiplier()`
- `benchmark_filter()`

## Test plan

### Multiplier

- directed cases: zero, one, max positive, min negative, sign mix
- random vectors for 8, 16, 24, and 32-bit widths
- signed and unsigned coverage
- exact comparison against a software reference
- register-level flow checked through the mock MMIO backend

### Convolution and Sobel

- known small images first
- compare pass-through, blur, sharpen, and Sobel modes to a NumPy reference
- verify border pixels stay zero with zero padding
- save a few output images for the repo
- test through the mock DMA path so the software stack can be checked off-board

## Benchmark plan

### Arithmetic

- time CPU multiplication in a loop
- time the IP call path including register writes and polling
- sweep widths and signed/unsigned mode
- report average latency and note when call overhead dominates

### Vision

- time CPU filtering on one frame
- time DMA send, IP run, and DMA receive as one transaction
- save total frame time and a rough FPS number
- compare small and medium image sizes
- call out that transfer overhead matters for small frames
