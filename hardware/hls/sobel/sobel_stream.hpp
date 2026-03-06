#ifndef SOBEL_STREAM_HPP
#define SOBEL_STREAM_HPP

#include <ap_int.h>
#include <hls_stream.h>

#include "stream_utils.hpp"

void sobel_stream(
    hls::stream<axis_pixel_t>& s_axis,
    hls::stream<axis_pixel_t>& m_axis,
    ap_uint<16> width,
    ap_uint<16> height,
    ap_uint<16> stride);

#endif
