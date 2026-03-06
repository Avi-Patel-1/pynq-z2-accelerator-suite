#ifndef BOOTH_MULTIPLIER_HPP
#define BOOTH_MULTIPLIER_HPP

#include <ap_int.h>

void booth_multiplier(
    ap_uint<32> operand_a,
    ap_uint<32> operand_b,
    ap_uint<32> mode,
    ap_uint<32>* result_lo,
    ap_uint<32>* result_hi,
    ap_uint<32>* status);

#endif
