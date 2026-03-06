#include "booth_multiplier.hpp"

static ap_uint<6> decode_width(ap_uint<32> mode) {
  switch ((int)(mode & 0x3)) {
    case 0:
      return 8;
    case 1:
      return 16;
    case 2:
      return 24;
    default:
      return 32;
  }
}

static ap_int<64> normalize_operand(ap_uint<32> raw, ap_uint<6> width, bool signed_mode) {
  ap_uint<64> mask = width == 32 ? 0xFFFFFFFFULL : (((ap_uint<64>)1 << width) - 1);
  ap_uint<64> masked = raw & mask;

  if (!signed_mode) {
    return (ap_int<64>)masked;
  }

  ap_uint<64> sign_bit = (ap_uint<64>)1 << (width - 1);
  if (masked & sign_bit) {
    ap_uint<64> extension = ~mask;
    return (ap_int<64>)(masked | extension);
  }
  return (ap_int<64>)masked;
}

static ap_int<65> booth_core(ap_int<64> multiplicand, ap_int<64> multiplier, ap_uint<6> width) {
  ap_int<65> accumulator = 0;
  ap_int<65> multiplicand_ext = multiplicand;
  ap_int<66> multiplier_bits = 0;
  const int max_groups = 16;
  int active_groups = (width + 1) >> 1;

  multiplier_bits[0] = 0;
  for (int bit = 0; bit < 32; ++bit) {
#pragma HLS UNROLL
    if (bit < width) {
      multiplier_bits[bit + 1] = multiplier[bit];
    } else {
      multiplier_bits[bit + 1] = multiplier[width - 1];
    }
  }

  for (int group = 0; group < max_groups; ++group) {
#pragma HLS PIPELINE II=1
    if (group >= active_groups) {
      continue;
    }

    ap_uint<3> code = multiplier_bits.range((group << 1) + 2, group << 1);
    ap_int<65> partial = 0;

    switch ((int)code) {
      case 0:
      case 7:
        partial = 0;
        break;
      case 1:
      case 2:
        partial = multiplicand_ext;
        break;
      case 3:
        partial = multiplicand_ext << 1;
        break;
      case 4:
        partial = -(multiplicand_ext << 1);
        break;
      case 5:
      case 6:
        partial = -multiplicand_ext;
        break;
    }

    accumulator += partial << (group << 1);
  }

  return accumulator;
}

void booth_multiplier(
    ap_uint<32> operand_a,
    ap_uint<32> operand_b,
    ap_uint<32> mode,
    ap_uint<32>* result_lo,
    ap_uint<32>* result_hi,
    ap_uint<32>* status) {
#pragma HLS INTERFACE s_axilite port=operand_a bundle=CTRL
#pragma HLS INTERFACE s_axilite port=operand_b bundle=CTRL
#pragma HLS INTERFACE s_axilite port=mode bundle=CTRL
#pragma HLS INTERFACE s_axilite port=result_lo bundle=CTRL
#pragma HLS INTERFACE s_axilite port=result_hi bundle=CTRL
#pragma HLS INTERFACE s_axilite port=status bundle=CTRL
#pragma HLS INTERFACE s_axilite port=return bundle=CTRL

  bool signed_mode = mode[8];
  ap_uint<6> width = decode_width(mode);
  ap_int<64> norm_a = normalize_operand(operand_a, width, signed_mode);
  ap_int<64> norm_b = normalize_operand(operand_b, width, signed_mode);
  ap_int<65> product = booth_core(norm_a, norm_b, width);
  ap_uint<64> raw_product = product.range(63, 0);

  *result_lo = raw_product.range(31, 0);
  *result_hi = raw_product.range(63, 32);
  *status = 0x1 | (((mode >> 8) & 0x1) << 1) | ((mode & 0x3) << 8);
}
