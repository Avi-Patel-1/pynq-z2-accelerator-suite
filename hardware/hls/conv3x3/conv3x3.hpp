#ifndef CONV3X3_HPP
#define CONV3X3_HPP

#include <ap_int.h>
#include <hls_stream.h>

#include "stream_utils.hpp"

void conv3x3_core(
    hls::stream<axis_pixel_t>& s_axis,
    hls::stream<axis_pixel_t>& m_axis,
    ap_uint<16> width,
    ap_uint<16> height,
    ap_uint<32> mode,
    ap_uint<8> threshold);

void conv3x3_stream(
    hls::stream<axis_pixel_t>& s_axis,
    hls::stream<axis_pixel_t>& m_axis,
    ap_uint<16> width,
    ap_uint<16> height,
    ap_uint<16> stride,
    ap_uint<32> mode,
    ap_uint<32> threshold,
    ap_uint<32> border);

#endif
