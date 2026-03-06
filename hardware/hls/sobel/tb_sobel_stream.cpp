#include <cassert>

#include "sobel_stream.hpp"

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

int main() {
  const int width = 4;
  const int height = 4;
  const unsigned char image[width * height] = {
      0, 0, 0, 0,
      0, 255, 255, 0,
      0, 255, 255, 0,
      0, 0, 0, 0};
  const unsigned char expected[width * height] = {
      255, 255, 255, 255,
      255, 255, 255, 255,
      255, 255, 255, 255,
      255, 255, 255, 255};

  hls::stream<axis_pixel_t> input_stream;
  hls::stream<axis_pixel_t> output_stream;

  load_image(input_stream, image, width, height);
  sobel_stream(input_stream, output_stream, width, height, width);

  for (int index = 0; index < width * height; ++index) {
    unsigned char actual = output_stream.read().data;
    assert(actual == expected[index]);
  }

  return 0;
}
