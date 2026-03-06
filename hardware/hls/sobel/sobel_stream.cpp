#include "sobel_stream.hpp"

#include "conv3x3.hpp"
#include "kernel_modes.hpp"

void sobel_stream(
    hls::stream<axis_pixel_t>& s_axis,
    hls::stream<axis_pixel_t>& m_axis,
    ap_uint<16> width,
    ap_uint<16> height,
    ap_uint<16> stride) {
#pragma HLS INTERFACE axis port=s_axis
#pragma HLS INTERFACE axis port=m_axis
#pragma HLS INTERFACE s_axilite port=width bundle=CTRL
#pragma HLS INTERFACE s_axilite port=height bundle=CTRL
#pragma HLS INTERFACE s_axilite port=stride bundle=CTRL
#pragma HLS INTERFACE s_axilite port=return bundle=CTRL

  (void)stride;
  conv3x3_core(s_axis, m_axis, width, height, KERNEL_SOBEL_MAG, 0);
}
