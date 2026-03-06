# Vivado Notes

This folder keeps the build scripts for the PYNQ-Z2 overlay.

Typical flow:

1. Run `build_hls_ip.tcl` in Vitis HLS to package the Booth multiplier and the streaming filter IP.
2. Run `create_block_design.tcl` in Vivado to build the Zynq system, DMA path, and AXI interconnect.
3. Run `package_overlay.tcl` after synthesis and implementation to copy the `.bit` and `.hwh` files into `hardware/export/`.

The scripts use the `xc7z020clg400-1` device directly. If the local board files include the PYNQ-Z2 preset, the block design script will apply it. Otherwise the DDR and MIO settings should be checked once in the Vivado GUI and the project can be saved again.
