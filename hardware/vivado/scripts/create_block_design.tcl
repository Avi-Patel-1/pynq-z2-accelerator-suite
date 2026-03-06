set root_dir [file normalize [file join [file dirname [info script]] .. ..]]
set proj_dir [file join $root_dir vivado build]
set proj_name pynq_z2_accel
set bd_name pynq_z2_accel_bd
set part_name xc7z020clg400-1
set board_part tul.com.tw:pynq-z2:part0:1.0

file mkdir $proj_dir
create_project $proj_name $proj_dir -part $part_name -force

if {[llength [get_board_parts $board_part -quiet]] > 0} {
  set_property board_part $board_part [current_project]
}

set ip_repo_paths [list \
  [file join $root_dir hls booth_multiplier booth_multiplier_prj solution1 impl ip] \
  [file join $root_dir hls conv3x3 conv3x3_prj solution1 impl ip] \
  [file join $root_dir hls sobel sobel_prj solution1 impl ip]]
set_property ip_repo_paths $ip_repo_paths [current_project]
update_ip_catalog

create_bd_design $bd_name

create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
if {[llength [get_board_parts $board_part -quiet]] > 0} {
  apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 \
    -config {make_external "FIXED_IO, DDR" apply_board_preset "1" Master "Disable" Slave "Disable"} \
    [get_bd_cells processing_system7_0]
}

set_property -dict [list \
  CONFIG.PCW_USE_S_AXI_HP0 {1} \
  CONFIG.PCW_USE_M_AXI_GP0 {1} \
  CONFIG.PCW_EN_CLK0_PORT {1} \
  CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100.0}] [get_bd_cells processing_system7_0]

create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_0
set_property -dict [list \
  CONFIG.c_include_mm2s {1} \
  CONFIG.c_include_s2mm {1} \
  CONFIG.c_sg_include_stscntrl_strm {0} \
  CONFIG.c_m_axi_mm2s_data_width {64} \
  CONFIG.c_m_axi_s2mm_data_width {64}] [get_bd_cells axi_dma_0]

create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 smartconnect_ctrl_0
set_property -dict [list CONFIG.NUM_MI {3}] [get_bd_cells smartconnect_ctrl_0]

create_bd_cell -type ip -vlnv xilinx.com:hls:booth_multiplier:1.0 booth_multiplier_0
create_bd_cell -type ip -vlnv xilinx.com:hls:conv3x3_stream:1.0 conv3x3_0
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 smartconnect_mem_0
set_property -dict [list CONFIG.NUM_SI {2}] [get_bd_cells smartconnect_mem_0]

connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] \
  [get_bd_pins axi_dma_0/s_axi_lite_aclk] \
  [get_bd_pins axi_dma_0/m_axi_mm2s_aclk] \
  [get_bd_pins axi_dma_0/m_axi_s2mm_aclk] \
  [get_bd_pins conv3x3_0/ap_clk] \
  [get_bd_pins booth_multiplier_0/ap_clk] \
  [get_bd_pins smartconnect_ctrl_0/aclk] \
  [get_bd_pins smartconnect_mem_0/aclk]

connect_bd_net [get_bd_pins processing_system7_0/FCLK_RESET0_N] \
  [get_bd_pins axi_dma_0/axi_resetn] \
  [get_bd_pins booth_multiplier_0/ap_rst_n] \
  [get_bd_pins conv3x3_0/ap_rst_n] \
  [get_bd_pins smartconnect_ctrl_0/aresetn] \
  [get_bd_pins smartconnect_mem_0/aresetn]

apply_bd_automation -rule xilinx.com:bd_rule:axi4 \
  -config {Clk_master "/processing_system7_0/FCLK_CLK0" Clk_slave "/processing_system7_0/FCLK_CLK0" Clk_xbar "/processing_system7_0/FCLK_CLK0" Master "/processing_system7_0/M_AXI_GP0" Slave "/smartconnect_ctrl_0/S00_AXI" intc_ip "New AXI Interconnect"} \
  [get_bd_intf_pins smartconnect_ctrl_0/S00_AXI]

connect_bd_intf_net [get_bd_intf_pins axi_dma_0/M_AXI_MM2S] [get_bd_intf_pins smartconnect_mem_0/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_dma_0/M_AXI_S2MM] [get_bd_intf_pins smartconnect_mem_0/S01_AXI]
connect_bd_intf_net [get_bd_intf_pins smartconnect_mem_0/M00_AXI] [get_bd_intf_pins processing_system7_0/S_AXI_HP0]

connect_bd_intf_net [get_bd_intf_pins smartconnect_ctrl_0/M00_AXI] [get_bd_intf_pins booth_multiplier_0/s_axi_CTRL]
connect_bd_intf_net [get_bd_intf_pins smartconnect_ctrl_0/M01_AXI] [get_bd_intf_pins conv3x3_0/s_axi_CTRL]
connect_bd_intf_net [get_bd_intf_pins smartconnect_ctrl_0/M02_AXI] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]

connect_bd_intf_net [get_bd_intf_pins axi_dma_0/M_AXIS_MM2S] [get_bd_intf_pins conv3x3_0/s_axis]
connect_bd_intf_net [get_bd_intf_pins conv3x3_0/m_axis] [get_bd_intf_pins axi_dma_0/S_AXIS_S2MM]

assign_bd_address
save_bd_design
validate_bd_design
exit
