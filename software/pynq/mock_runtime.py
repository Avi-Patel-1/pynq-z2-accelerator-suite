from __future__ import annotations

import numpy as np

from .reference import pack_result_words, process_frame_reference, reference_multiplier_from_mode
from .registers import (
    ARITH_CONTROL,
    ARITH_MODE,
    ARITH_OPERAND_A,
    ARITH_OPERAND_B,
    ARITH_RESULT_HI,
    ARITH_RESULT_LO,
    ARITH_STATUS,
    VISION_CONTROL,
    VISION_HEIGHT,
    VISION_MODE,
    VISION_THRESHOLD,
    VISION_WIDTH,
)


class MockMMIO:
    def __init__(self) -> None:
        self.registers: dict[int, int] = {}

    def write(self, offset: int, value: int) -> None:
        self.registers[offset] = int(value) & 0xFFFFFFFF

    def read(self, offset: int) -> int:
        return self.registers.get(offset, 0)


class MockArithmeticIP(MockMMIO):
    def __init__(self) -> None:
        super().__init__()
        self.registers[ARITH_CONTROL] = 0x4

    def write(self, offset: int, value: int) -> None:
        super().write(offset, value)
        if offset == ARITH_CONTROL and value & 0x1:
            product = reference_multiplier_from_mode(
                self.read(ARITH_OPERAND_A),
                self.read(ARITH_OPERAND_B),
                self.read(ARITH_MODE),
            )
            result_lo, result_hi = pack_result_words(product)
            self.registers[ARITH_RESULT_LO] = result_lo
            self.registers[ARITH_RESULT_HI] = result_hi
            self.registers[ARITH_STATUS] = 0x1 | (self.read(ARITH_MODE) << 1)
            self.registers[ARITH_CONTROL] = 0xE


class MockVisionIP(MockMMIO):
    def __init__(self) -> None:
        super().__init__()
        self.registers[VISION_CONTROL] = 0x4

    def mark_done(self) -> None:
        self.registers[VISION_CONTROL] = 0xE


class MockDMAChannel:
    def __init__(self, parent: "MockDMA", direction: str) -> None:
        self.parent = parent
        self.direction = direction

    def transfer(self, buffer: np.ndarray) -> None:
        if self.direction == "send":
            self.parent.send_buffer = np.array(buffer, copy=True)
        else:
            self.parent.recv_buffer = buffer

    def wait(self) -> None:
        self.parent.complete()


class MockDMA:
    def __init__(self, ip: MockVisionIP) -> None:
        self.ip = ip
        self.send_buffer: np.ndarray | None = None
        self.recv_buffer: np.ndarray | None = None
        self.sendchannel = MockDMAChannel(self, "send")
        self.recvchannel = MockDMAChannel(self, "recv")

    def complete(self) -> None:
        if self.send_buffer is None or self.recv_buffer is None:
            return

        width = self.ip.read(VISION_WIDTH)
        height = self.ip.read(VISION_HEIGHT)
        mode = self.ip.read(VISION_MODE)
        threshold = self.ip.read(VISION_THRESHOLD) & 0xFF

        frame = np.asarray(self.send_buffer, dtype=np.uint8)
        if frame.ndim == 1:
            frame = frame.reshape((height, width))
        result = process_frame_reference(frame, mode, threshold)
        self.recv_buffer[...] = result.reshape(self.recv_buffer.shape)
        self.ip.mark_done()
        self.send_buffer = None
        self.recv_buffer = None


class MockOverlay:
    def __init__(self) -> None:
        self.booth_multiplier_0 = MockArithmeticIP()
        self.conv3x3_0 = MockVisionIP()
        self.axi_dma_0 = MockDMA(self.conv3x3_0)
