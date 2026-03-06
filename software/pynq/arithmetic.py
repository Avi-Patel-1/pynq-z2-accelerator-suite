from __future__ import annotations

import time
from time import perf_counter_ns

from .mock_runtime import MockArithmeticIP
from .reference import (
    build_multiplier_mode,
    pack_operand,
    reference_multiplier,
    signed_from_mode,
    unpack_result_words,
)
from .registers import (
    ARITH_CONTROL,
    ARITH_MODE,
    ARITH_OPERAND_A,
    ARITH_OPERAND_B,
    ARITH_RESULT_HI,
    ARITH_RESULT_LO,
    ARITH_STATUS,
)


class ArithmeticOverlay:
    def __init__(self, ip: object, poll_interval_s: float = 1e-6) -> None:
        self.ip = ip
        self.poll_interval_s = poll_interval_s

    def write_operands(self, operand_a: int, operand_b: int, width: int = 32, signed_mode: bool = True) -> int:
        mode = build_multiplier_mode(width, signed_mode)
        self.ip.write(ARITH_OPERAND_A, pack_operand(operand_a, width))
        self.ip.write(ARITH_OPERAND_B, pack_operand(operand_b, width))
        self.ip.write(ARITH_MODE, mode)
        return mode

    def start(self) -> None:
        self.ip.write(ARITH_CONTROL, 0x1)

    def wait_done(self, timeout_s: float = 0.1) -> int:
        deadline = time.perf_counter() + timeout_s
        while time.perf_counter() < deadline:
            status = self.ip.read(ARITH_STATUS)
            control = self.ip.read(ARITH_CONTROL)
            if (status & 0x1) or (control & 0x2):
                return status
            time.sleep(self.poll_interval_s)
        raise TimeoutError("Timed out waiting for the multiplier IP")

    def read_result(self, signed_mode: bool = True) -> int:
        result_lo = self.ip.read(ARITH_RESULT_LO)
        result_hi = self.ip.read(ARITH_RESULT_HI)
        return unpack_result_words(result_lo, result_hi, signed_mode)

    def multiply(
        self,
        operand_a: int,
        operand_b: int,
        width: int = 32,
        signed_mode: bool = True,
        timeout_s: float = 0.1,
        return_timing: bool = False,
    ) -> int | tuple[int, int]:
        self.write_operands(operand_a, operand_b, width=width, signed_mode=signed_mode)
        start_ns = perf_counter_ns()
        self.start()
        self.wait_done(timeout_s=timeout_s)
        latency_ns = perf_counter_ns() - start_ns
        result = self.read_result(signed_mode=signed_mode)
        if return_timing:
            return result, latency_ns
        return result


def run_multiplier_test(vectors: list[dict[str, int]] | None = None, overlay: ArithmeticOverlay | None = None) -> dict[str, object]:
    test_vectors = vectors or [
        {"a": 0, "b": 0, "width": 8, "signed": False},
        {"a": 7, "b": 9, "width": 8, "signed": False},
        {"a": -5, "b": 12, "width": 8, "signed": True},
        {"a": -33, "b": -17, "width": 16, "signed": True},
        {"a": 0x00FFFF, "b": 0x000011, "width": 24, "signed": False},
        {"a": -12345, "b": 23456, "width": 32, "signed": True},
    ]
    dut = overlay or ArithmeticOverlay(MockArithmeticIP())
    failures: list[dict[str, int]] = []

    for vector in test_vectors:
        result = dut.multiply(vector["a"], vector["b"], vector["width"], bool(vector["signed"]))
        expected = reference_multiplier(vector["a"], vector["b"], vector["width"], bool(vector["signed"]))
        if result != expected:
            failures.append({**vector, "expected": expected, "actual": result})

    return {
        "total": len(test_vectors),
        "passed": len(test_vectors) - len(failures),
        "failed": len(failures),
        "failures": failures,
    }
