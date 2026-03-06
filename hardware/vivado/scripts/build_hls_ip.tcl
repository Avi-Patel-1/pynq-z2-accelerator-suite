set root_dir [file normalize [file join [file dirname [info script]] .. ..]]
set hls_dir [file join $root_dir hls]
set part_name xc7z020clg400-1
set clock_period_ns 10.0

proc build_booth_multiplier {hls_dir part_name clock_period_ns} {
  open_project [file join $hls_dir booth_multiplier booth_multiplier_prj]
  set_top booth_multiplier
  add_files [file join $hls_dir booth_multiplier booth_multiplier.cpp]
  add_files [file join $hls_dir booth_multiplier booth_multiplier.hpp]
  add_files -tb [file join $hls_dir booth_multiplier tb_booth_multiplier.cpp]
  open_solution -reset solution1
  set_part $part_name
  create_clock -period $clock_period_ns -name default
  csim_design
  csynth_design
  export_design -format ip_catalog
  close_project
}

proc build_conv3x3 {hls_dir part_name clock_period_ns} {
  open_project [file join $hls_dir conv3x3 conv3x3_prj]
  set_top conv3x3_stream
  add_files [file join $hls_dir common kernel_modes.hpp]
  add_files [file join $hls_dir common stream_utils.hpp]
  add_files [file join $hls_dir conv3x3 conv3x3.cpp]
  add_files [file join $hls_dir conv3x3 conv3x3.hpp]
  add_files -tb [file join $hls_dir conv3x3 tb_conv3x3.cpp]
  open_solution -reset solution1
  set_part $part_name
  create_clock -period $clock_period_ns -name default
  csim_design
  csynth_design
  export_design -format ip_catalog
  close_project
}

proc build_sobel {hls_dir part_name clock_period_ns} {
  open_project [file join $hls_dir sobel sobel_prj]
  set_top sobel_stream
  add_files [file join $hls_dir common kernel_modes.hpp]
  add_files [file join $hls_dir common stream_utils.hpp]
  add_files [file join $hls_dir conv3x3 conv3x3.cpp]
  add_files [file join $hls_dir conv3x3 conv3x3.hpp]
  add_files [file join $hls_dir sobel sobel_stream.cpp]
  add_files [file join $hls_dir sobel sobel_stream.hpp]
  add_files -tb [file join $hls_dir sobel tb_sobel_stream.cpp]
  open_solution -reset solution1
  set_part $part_name
  create_clock -period $clock_period_ns -name default
  csim_design
  csynth_design
  export_design -format ip_catalog
  close_project
}

build_booth_multiplier $hls_dir $part_name $clock_period_ns
build_conv3x3 $hls_dir $part_name $clock_period_ns
build_sobel $hls_dir $part_name $clock_period_ns
exit
