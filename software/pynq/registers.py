from __future__ import annotations

from enum import IntEnum


ARITH_CONTROL = 0x00
ARITH_OPERAND_A = 0x10
ARITH_OPERAND_B = 0x18
ARITH_MODE = 0x20
ARITH_RESULT_LO = 0x28
ARITH_RESULT_HI = 0x30
ARITH_STATUS = 0x38

VISION_CONTROL = 0x00
VISION_WIDTH = 0x10
VISION_HEIGHT = 0x18
VISION_STRIDE = 0x20
VISION_MODE = 0x28
VISION_THRESHOLD = 0x30
VISION_BORDER = 0x38

SIGNED_MODE_BIT = 1 << 8
WIDTH_TO_CODE = {8: 0, 16: 1, 24: 2, 32: 3}
CODE_TO_WIDTH = {value: key for key, value in WIDTH_TO_CODE.items()}


class KernelMode(IntEnum):
    PASS_THROUGH = 0
    BLUR = 1
    SHARPEN = 2
    SOBEL_X = 3
    SOBEL_Y = 4
    SOBEL_MAG = 5
    THRESHOLD = 6


class BorderMode(IntEnum):
    ZERO = 0
