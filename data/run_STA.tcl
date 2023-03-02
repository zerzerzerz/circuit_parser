read_liberty NangateOpenCellLibrary_typical.lib
read_verilog 6_final.v

link_design gcd

read_sdc 6_final.sdc

# read_spef 6_final.spef 

# write_sdf -digits 8 6_final.sdf

# report_checks -group_count 2147483647 -endpoint_count 1 -digits 6 -format full -path_delay min_max -no_line_splits > path.log
report_checks -group_count 2147483647 -endpoint_count 1 -digits 6 -format summary > path_summary.log

with_output_to_variable PI {report_object_full_names [get_ports * -filter "direction==input"]}
echo $PI > primary_input
with_output_to_variable PO {report_object_full_names [get_ports * -filter "direction==output"]}
echo $PO > primary_output

exit