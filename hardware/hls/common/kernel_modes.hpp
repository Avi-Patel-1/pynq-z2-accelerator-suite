#ifndef KERNEL_MODES_HPP
#define KERNEL_MODES_HPP

enum kernel_mode_t {
  KERNEL_PASS = 0,
  KERNEL_BLUR = 1,
  KERNEL_SHARPEN = 2,
  KERNEL_SOBEL_X = 3,
  KERNEL_SOBEL_Y = 4,
  KERNEL_SOBEL_MAG = 5,
  KERNEL_THRESHOLD = 6
};

static const int BORDER_ZERO = 0;

#endif
