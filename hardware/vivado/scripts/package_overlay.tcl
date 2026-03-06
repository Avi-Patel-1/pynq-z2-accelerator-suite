set root_dir [file normalize [file join [file dirname [info script]] .. ..]]
set export_dir [file join $root_dir export]
set impl_dir [file join $root_dir vivado build pynq_z2_accel pynq_z2_accel.runs impl_1]
set bit_file [file join $impl_dir pynq_z2_accel_bd_wrapper.bit]
set hwh_file [file join $root_dir vivado build pynq_z2_accel pynq_z2_accel.gen sources_1 bd pynq_z2_accel_bd hw_handoff pynq_z2_accel_bd.hwh]

file mkdir $export_dir

if {[file exists $bit_file]} {
  file copy -force $bit_file [file join $export_dir pynq_z2_accel.bit]
}

if {[file exists $hwh_file]} {
  file copy -force $hwh_file [file join $export_dir pynq_z2_accel.hwh]
}

exit
