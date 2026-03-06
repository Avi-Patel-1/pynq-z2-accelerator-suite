#include "conv3x3.hpp"

void conv3x3_core(
    hls::stream<axis_pixel_t>& s_axis,
    hls::stream<axis_pixel_t>& m_axis,
    ap_uint<16> width,
    ap_uint<16> height,
    ap_uint<32> mode,
    ap_uint<8> threshold) {
  ap_uint<8> line_buffer0[MAX_IMAGE_WIDTH + 2];
  ap_uint<8> line_buffer1[MAX_IMAGE_WIDTH + 2];
  ap_uint<8> window[3][3];
#pragma HLS ARRAY_PARTITION variable=window complete dim=0
#pragma HLS BIND_STORAGE variable=line_buffer0 type=ram_2p impl=bram
#pragma HLS BIND_STORAGE variable=line_buffer1 type=ram_2p impl=bram

  for (int col = 0; col < MAX_IMAGE_WIDTH + 2; ++col) {
#pragma HLS PIPELINE II=1
    line_buffer0[col] = 0;
    line_buffer1[col] = 0;
  }

  for (int row = 0; row < 3; ++row) {
#pragma HLS UNROLL
    for (int col = 0; col < 3; ++col) {
#pragma HLS UNROLL
      window[row][col] = 0;
    }
  }

  int output_index = 0;
  int total_pixels = width * height;

  for (int padded_row = 0; padded_row < height + 2; ++padded_row) {
    for (int padded_col = 0; padded_col < width + 2; ++padded_col) {
#pragma HLS PIPELINE II=1
      ap_uint<8> incoming = 0;
      bool in_frame = padded_row > 0 && padded_row <= height && padded_col > 0 && padded_col <= width;

      if (in_frame) {
        axis_pixel_t pixel_in = s_axis.read();
        incoming = pixel_in.data;
      }

      for (int row = 0; row < 3; ++row) {
#pragma HLS UNROLL
        window[row][0] = window[row][1];
        window[row][1] = window[row][2];
      }

      window[0][2] = line_buffer0[padded_col];
      window[1][2] = line_buffer1[padded_col];
      window[2][2] = incoming;

      line_buffer0[padded_col] = line_buffer1[padded_col];
      line_buffer1[padded_col] = incoming;

      if (padded_row >= 2 && padded_col >= 2) {
        axis_pixel_t pixel_out;
        pixel_out.data = apply_kernel_mode(window, mode, threshold);
        pixel_out.keep = 0x1;
        pixel_out.strb = 0x1;
        pixel_out.user = output_index == 0 ? 1 : 0;
        pixel_out.last = output_index == total_pixels - 1 ? 1 : 0;
        pixel_out.id = 0;
        pixel_out.dest = 0;
        m_axis.write(pixel_out);
        ++output_index;
      }
    }
  }
}

void conv3x3_stream(
    hls::stream<axis_pixel_t>& s_axis,
    hls::stream<axis_pixel_t>& m_axis,
    ap_uint<16> width,
    ap_uint<16> height,
    ap_uint<16> stride,
    ap_uint<32> mode,
    ap_uint<32> threshold,
    ap_uint<32> border) {
#pragma HLS INTERFACE axis port=s_axis
#pragma HLS INTERFACE axis port=m_axis
#pragma HLS INTERFACE s_axilite port=width bundle=CTRL
#pragma HLS INTERFACE s_axilite port=height bundle=CTRL
#pragma HLS INTERFACE s_axilite port=stride bundle=CTRL
#pragma HLS INTERFACE s_axilite port=mode bundle=CTRL
#pragma HLS INTERFACE s_axilite port=threshold bundle=CTRL
#pragma HLS INTERFACE s_axilite port=border bundle=CTRL
#pragma HLS INTERFACE s_axilite port=return bundle=CTRL

  (void)stride;
  (void)border;

  if (width == 0 || height == 0 || width > MAX_IMAGE_WIDTH) {
    return;
  }

  conv3x3_core(s_axis, m_axis, width, height, mode, threshold.range(7, 0));
}
