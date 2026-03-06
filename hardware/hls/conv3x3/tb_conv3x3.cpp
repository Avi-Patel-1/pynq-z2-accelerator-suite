#include <cassert>

#include "conv3x3.hpp"

static void load_image(hls::stream<axis_pixel_t>& stream, const unsigned char* image, int width, int height) {
  for (int row = 0; row < height; ++row) {
    for (int col = 0; col < width; ++col) {
      axis_pixel_t pixel;
      pixel.data = image[row * width + col];
      pixel.keep = 1;
      pixel.strb = 1;
      pixel.user = row == 0 && col == 0 ? 1 : 0;
      pixel.last = row == height - 1 && col == width - 1 ? 1 : 0;
      pixel.id = 0;
      pixel.dest = 0;
      stream.write(pixel);
    }
  }
}

static void read_image(hls::stream<axis_pixel_t>& stream, unsigned char* image, int width, int height) {
  for (int row = 0; row < height; ++row) {
    for (int col = 0; col < width; ++col) {
      image[row * width + col] = stream.read().data;
    }
  }
}

int main() {
  const int width = 4;
  const int height = 4;
  const unsigned char image[width * height] = {
      0, 10, 20, 30,
      40, 50, 60, 70,
      80, 90, 100, 110,
      120, 130, 140, 150};
  const unsigned char expected_blur[width * height] = {
      11, 20, 26, 20,
      30, 50, 60, 43,
      56, 90, 100, 70,
      46, 73, 80, 55};

  hls::stream<axis_pixel_t> input_stream;
  hls::stream<axis_pixel_t> output_stream;
  unsigned char output[width * height];

  load_image(input_stream, image, width, height);
  conv3x3_stream(input_stream, output_stream, width, height, width, 1, 0, 0);
  read_image(output_stream, output, width, height);

  for (int index = 0; index < width * height; ++index) {
    assert(output[index] == expected_blur[index]);
  }

  return 0;
}
