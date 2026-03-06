#ifndef STREAM_UTILS_HPP
#define STREAM_UTILS_HPP

#include <ap_axi_sdata.h>
#include <ap_int.h>

#include "kernel_modes.hpp"

typedef ap_axiu<8, 1, 1, 1> axis_pixel_t;

static const int MAX_IMAGE_WIDTH = 1280;

inline int abs_i32(int value) {
  return value < 0 ? -value : value;
}

inline ap_uint<8> clamp_u8(int value) {
  if (value < 0) {
    return 0;
  }
  if (value > 255) {
    return 255;
  }
  return (ap_uint<8>)value;
}

inline ap_uint<8> apply_kernel_mode(ap_uint<8> window[3][3], ap_uint<32> mode, ap_uint<8> threshold) {
#pragma HLS INLINE
#pragma HLS ARRAY_PARTITION variable=window complete dim=0
  int center = window[1][1];
  int blur_sum = 0;

  for (int row = 0; row < 3; ++row) {
#pragma HLS UNROLL
    for (int col = 0; col < 3; ++col) {
#pragma HLS UNROLL
      blur_sum += window[row][col];
    }
  }

  int sobel_x =
      -window[0][0] + window[0][2] -
      (window[1][0] << 1) + (window[1][2] << 1) -
      window[2][0] + window[2][2];

  int sobel_y =
      -window[0][0] - (window[0][1] << 1) - window[0][2] +
      window[2][0] + (window[2][1] << 1) + window[2][2];

  switch ((int)mode) {
    case KERNEL_PASS:
      return (ap_uint<8>)center;
    case KERNEL_BLUR:
      return clamp_u8(blur_sum / 9);
    case KERNEL_SHARPEN:
      return clamp_u8(5 * center - window[0][1] - window[1][0] - window[1][2] - window[2][1]);
    case KERNEL_SOBEL_X:
      return clamp_u8(abs_i32(sobel_x));
    case KERNEL_SOBEL_Y:
      return clamp_u8(abs_i32(sobel_y));
    case KERNEL_SOBEL_MAG:
      return clamp_u8(abs_i32(sobel_x) + abs_i32(sobel_y));
    case KERNEL_THRESHOLD:
      return center >= threshold ? (ap_uint<8>)255 : (ap_uint<8>)0;
    default:
      return (ap_uint<8>)center;
  }
}

#endif
