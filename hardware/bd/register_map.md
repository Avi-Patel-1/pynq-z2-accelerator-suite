# Register Map

## Booth multiplier

Base name in the block design: `booth_multiplier_0`

| Offset | Register | Description |
| --- | --- | --- |
| `0x00` | `CTRL` | HLS control register. Bit `0` start, bit `1` done, bit `2` idle, bit `3` ready. |
| `0x10` | `OPERAND_A` | Operand A, low 32 bits. |
| `0x18` | `OPERAND_B` | Operand B, low 32 bits. |
| `0x20` | `MODE` | Width code in bits `[1:0]`, signed mode in bit `8`. |
| `0x28` | `RESULT_LO` | Product bits `[31:0]`. |
| `0x30` | `RESULT_HI` | Product bits `[63:32]`. |
| `0x38` | `STATUS` | Bit `0` valid, bit `1` signed, bits `[9:8]` width code. |

Mode field details:

- width code `0`: 8-bit
- width code `1`: 16-bit
- width code `2`: 24-bit
- width code `3`: 32-bit
- signed mode bit `8`: `0` unsigned, `1` signed

## Streaming 3x3 filter

Base name in the block design: `conv3x3_0`

| Offset | Register | Description |
| --- | --- | --- |
| `0x00` | `CTRL` | HLS control register. Bit `0` start, bit `1` done, bit `2` idle, bit `3` ready. |
| `0x10` | `WIDTH` | Frame width in pixels. |
| `0x18` | `HEIGHT` | Frame height in pixels. |
| `0x20` | `STRIDE` | Bytes per row. Use width for grayscale frames. |
| `0x28` | `MODE` | Filter mode select. |
| `0x30` | `THRESHOLD` | Threshold value for mode `6`. |
| `0x38` | `BORDER` | Border mode. `0` means zero padding. |

Mode values:

- `0` pass-through
- `1` blur
- `2` sharpen
- `3` Sobel X
- `4` Sobel Y
- `5` Sobel magnitude
- `6` threshold

## DMA path

The frame path in the block design is:

`PS DDR -> AXI DMA MM2S -> conv3x3_0 -> AXI DMA S2MM -> PS DDR`

Software writes the control registers first, starts the IP, then launches the DMA transfers.
