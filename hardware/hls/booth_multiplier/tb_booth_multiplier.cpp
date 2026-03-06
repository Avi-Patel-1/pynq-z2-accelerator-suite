#include <cassert>

#include "booth_multiplier.hpp"

static int64_t decode_result(uint32_t lo, uint32_t hi, bool signed_mode) {
  uint64_t raw = ((uint64_t)hi << 32) | lo;
  if (signed_mode && (raw & (1ULL << 63))) {
    return (int64_t)(raw - (1ULL << 64));
  }
  return (int64_t)raw;
}

static int64_t normalize_operand(uint32_t raw, int width, bool signed_mode) {
  uint64_t mask = width == 32 ? 0xFFFFFFFFULL : ((1ULL << width) - 1);
  uint64_t value = raw & mask;
  if (signed_mode && (value & (1ULL << (width - 1)))) {
    return (int64_t)(value - (1ULL << width));
  }
  return (int64_t)value;
}

static void run_case(int32_t a, int32_t b, int width_code, bool signed_mode) {
  uint32_t result_lo = 0;
  uint32_t result_hi = 0;
  uint32_t status = 0;
  uint32_t mode = width_code | (signed_mode ? (1U << 8) : 0U);
  int width = width_code == 0 ? 8 : (width_code == 1 ? 16 : (width_code == 2 ? 24 : 32));
  int64_t expected = normalize_operand((uint32_t)a, width, signed_mode) * normalize_operand((uint32_t)b, width, signed_mode);

  booth_multiplier((uint32_t)a, (uint32_t)b, mode, &result_lo, &result_hi, &status);
  assert((status & 0x1) == 0x1);
  assert(decode_result(result_lo, result_hi, signed_mode) == expected);
}

int main() {
  run_case(7, 9, 0, false);
  run_case(-5, 12, 0, true);
  run_case(-321, -17, 1, true);
  run_case(0x00FFFF, 321, 2, false);
  run_case(-12345, 23456, 3, true);
  run_case((int32_t)0xFFFFFFFFU, (int32_t)0xFFFFFFFFU, 3, false);
  return 0;
}
