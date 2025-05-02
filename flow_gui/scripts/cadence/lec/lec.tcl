

# Define Paths
set LOG_PATH logs
set LIB_PATH ../../LIB
set SLOW_LIB slow.lib
set MAP2FINAL_REPORTS_PATH reports/map2final
set RTL2MAP_REPORTS_PATH reports/rtl2map
set RTL_PATH ../RTL_Sources
set RTL_LIST [glob -nocomplain $RTL_PATH/*]

set_screen_display -progress

# Argument '-no_exit' was specified.
#set_dofile_abort exit

### Alias mapping flow is enabled. ###
# Root attribute 'alias_flow' was 'true'.

set lec_version [regsub {(-)[A-Za-z]} $env(LEC_VERSION) ""]

# Turns on the flowgraph datapath solver.
set wlec_analyze_dp_flowgraph true
# Indicates that resource sharing datapath optimization is present.
set share_dp_analysis true

# The flowgraph solver is recommended for datapath analysis in LEC 19.1 or newer.
set lec_version_required "19.10100"
if {$lec_version >= $lec_version_required &&
    $wlec_analyze_dp_flowgraph} {
    set DATAPATH_SOLVER_OPTION "-flowgraph"
} elseif {$share_dp_analysis} {
    set DATAPATH_SOLVER_OPTION "-share"
} else {
    set DATAPATH_SOLVER_OPTION ""
}

# This composite dofile includes two compare operations: rtl-to-fv_map and
# fv_map-to-revised. The 'fv_map' netlist was automatically written in the
# verification directory during the syn_map command.

# This function is only valid for a flat compare
proc is_pass {} {
    redirect -variable compare_result {report_verification}
    foreach i [split $compare_result "\n"] {
        if {[regexp {Compare Results:\s+PASS} $i]} {
            return true
        }
    }
    return false
}

tcl_set_command_name_echo on

set logfile ${LOG_PATH}/rtl_to_final.lec.log ;# user can modify this name for succeeding runs

set_log_file $logfile -replace

usage -auto -elapse

set_mapping_method -sensitive

# Comparing intermediate 'fv_map' netlist vs. revised netlist.

set_verification_information ${MAP2FINAL_REPORTS_PATH}/fv_map_${DESIGN}_netlistv_db

read_implementation_information ../Genus/fv/${DESIGN} -golden fv_map -revised ${DESIGN}_netlistv

# Root attribute 'wlec_multithread_license_list' can be used to specify a license list
# for multithreaded processing. The default list is used otherwise.
set_parallel_option -threads 4,4 -norelease_license
set_compare_options -threads 4,4

set env(RC_VERSION)     "21.18-s082_1"
set env(CDN_SYNTH_ROOT) "/opt/cadence/installs/Genus_21_18/tools.lnx86"
set CDN_SYNTH_ROOT      "/opt/cadence/installs/Genus_21_18/tools.lnx86"
set env(CW_DIR) "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware"
set CW_DIR      "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware"
set lec_version_required "21.20249"
if { ($lec_version < $lec_version_required) &&
    [file exists /opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/old_encrypt_sim]} {
    set env(CW_DIR_SIM) "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/old_encrypt_sim"
    set CW_DIR_SIM      "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/old_encrypt_sim"
} else {
    set env(CW_DIR_SIM) "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/sim"
    set CW_DIR_SIM      "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/sim"
}
set_multiplier_implementation boothrca -both

# default is to error out when module definitions are missing
set_undefined_cell black_box -noascend -both

# ILM modules: 

add_search_path . /opt/cadence/installs/Genus_21_18/tools.lnx86/lib/tech -library -both
read_library -liberty -both ${LIB_PATH}/${SLOW_LIB}

read_design -verilog95   -golden -lastmod -noelab ../Genus/fv/${DESIGN}/fv_map.v.gz
elaborate_design -golden -root ${DESIGN}

read_design -verilog95   -revised -lastmod -noelab ../Genus/outputs/${DESIGN}_netlist.v
elaborate_design -revised -root ${DESIGN}

#add_name_alias fv/UDP/fv_map.singlebit.original_name.alias.json.gz -golden
#set_mapping_method -alias -golden

report_design_data
report_black_box

set_flatten_model -seq_constant
set_flatten_model -seq_constant_x_to 0
set_flatten_model -nodff_to_dlat_zero
set_flatten_model -nodff_to_dlat_feedback
set_flatten_model -hier_seq_merge

#add_name_alias fv/UDP/UDP_netlistv.singlebit.original_name.alias.json.gz -revised
#set_mapping_method -alias -revised
#add_renaming_rule r1alias _reg((\\\[%w\\\])*(/U\\\$%d)*)$ @1 -type dff dlat -both

# Reports the quality of the implementation information.
# This command is only available with LEC 20.10-p100 or later.
set lec_version_required "20.10100"
if {$lec_version >= $lec_version_required} {
    check_verification_information -verbose
}

set_analyze_option -auto -report_map

set_system_mode lec
report_mapped_points
report_unmapped_points -summary
report_unmapped_points -notmapped
report_unmapped_points -extra -unreachable
add_compared_points -all
report_compared_points
compare

report_compare_data
report_compare_data -class nonequivalent -class abort -class notcompared
report_verification -verbose
report_statistics

write_compared_points ${MAP2FINAL_REPORTS_PATH}/noneq_compared_points_${DESIGN}_fv_map_${DESIGN}_netlistv.tcl -class noneq -tclmode -replace
set lec_version_required "21.10100"
if {$lec_version >= $lec_version_required} {
    analyze_nonequivalent -source_diagnosis
    report_nonequivalent_analysis > ${MAP2FINAL_REPORTS_PATH}/noneq.source_diag.${DESIGN}.fv_map.${DESIGN}_netlistv.rpt
}
report_test_vector -noneq > ${MAP2FINAL_REPORTS_PATH}/noneq.test_vector.${DESIGN}.fv_map.${DESIGN}_netlistv.rpt

# Check intermediate 'fv_map' netlist vs. revised netlist compare result
if {![is_pass]} {
    error "// ERROR: Compare was not equivalent."
}

write_verification_information
report_verification_information

# Reports how effective the implementation information was.
# This command is only available with LEC 18.20-d330 or later.
set lec_version_required "18.20330"
if {$lec_version >= $lec_version_required} {
    report_implementation_information -verbose
}


##############################
# Generate Reports
##############################

source map2final_reports.tcl

write_mapped_points > ${MAP2FINAL_REPORTS_PATH}/mapped_pts.rpt
report_unmapped_points -summary > ${MAP2FINAL_REPORTS_PATH}/unmapped_points.rpt
report_compare_data -summary > ${MAP2FINAL_REPORTS_PATH}/compared_points.rpt
report_mapped_points -summary > ${MAP2FINAL_REPORTS_PATH}/mapped_points.rpt
report_design_data -summary > ${MAP2FINAL_REPORTS_PATH}/design_data.rpt
report_design_similarity -revised -verbose > ${MAP2FINAL_REPORTS_PATH}/similarity(%).rpt
report_floating_signals -all > ${MAP2FINAL_REPORTS_PATH}/floating_signals.rpt
report_primary_inputs > ${MAP2FINAL_REPORTS_PATH}/inputs.rpt
report_primary_outputs > ${MAP2FINAL_REPORTS_PATH}/outputs.rpt
report_verification -summary -verbose > ${MAP2FINAL_REPORTS_PATH}/verification.rpt
report_compare_data -CLASS NONEQuivalent > ${MAP2FINAL_REPORTS_PATH}/non_equivalent_points.rpt
report_statistics > ${MAP2FINAL_REPORTS_PATH}/statistics.rpt


reset

set_mapping_method -sensitive

# Comparing RTL vs. intermediate 'fv_map' netlist.

set_verification_information ${MAP2FINAL_REPORTS_PATH}/rtl_fv_map_db

read_implementation_information ../Genus/fv/${DESIGN} -revised fv_map

# Root attribute 'wlec_multithread_license_list' can be used to specify a license list
# for multithreaded processing. The default list is used otherwise.
set_parallel_option -threads 4,4 -norelease_license
set_compare_options -threads 4,4

set env(RC_VERSION)     "21.18-s082_1"
set env(CDN_SYNTH_ROOT) "/opt/cadence/installs/Genus_21_18/tools.lnx86"
set CDN_SYNTH_ROOT      "/opt/cadence/installs/Genus_21_18/tools.lnx86"
set env(CW_DIR) "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware"
set CW_DIR      "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware"
set lec_version_required "21.20249"
if { ($lec_version < $lec_version_required) &&
    [file exists /opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/old_encrypt_sim]} {
    set env(CW_DIR_SIM) "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/old_encrypt_sim"
    set CW_DIR_SIM      "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/old_encrypt_sim"
} else {
    set env(CW_DIR_SIM) "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/sim"
    set CW_DIR_SIM      "/opt/cadence/installs/Genus_21_18/tools.lnx86/lib/chipware/sim"
}
set_multiplier_implementation boothrca -both

# default is to error out when module definitions are missing
set_undefined_cell black_box -noascend -both

# ILM modules: 

add_search_path . /opt/cadence/installs/Genus_21_18/tools.lnx86/lib/tech -library -both
read_library -liberty -both ${LIB_PATH}/${SLOW_LIB}

set_undriven_signal 0 -golden
set lec_version_required "16.20100"
if {$lec_version >= $lec_version_required} {
    set_naming_style genus -golden
} else {
    set_naming_style rc -golden
}
set_naming_rule "%s\[%d\]" -instance_array -golden
set_naming_rule "%s_reg" -register -golden
set_naming_rule "%L.%s" "%L\[%d\].%s" "%s" -instance -golden
set_naming_rule "%L.%s" "%L\[%d\].%s" "%s" -variable -golden
set lec_version_required "17.10200"
if {$lec_version >= $lec_version_required} {
    set_naming_rule -ungroup_separator {_} -golden
}

# Align LEC's treatment of mismatched port widths with constant
# connections with Genus's. Genus message CDFG-467 and LEC message
# HRC3.6 may indicate the presence of this issue.
# This option is only available with LEC 17.20-d301 or later.
set lec_version_required "17.20301"
if {$lec_version >= $lec_version_required} {
    set_hdl_options -const_port_extend
}
set_hdl_options -unsigned_conversion_overflow on
set_hdl_options -v_to_vd on

set lec_version_required "20.20226"
if {$lec_version >= $lec_version_required} {
    set_hdl_options -VERILOG_INCLUDE_DIR "sep:src"
} else {
    set_hdl_options -VERILOG_INCLUDE_DIR "sep:src:cwd"
}

foreach file $RTL_LIST {
    puts "Processing file: $file"
    if {[string match "*.sv" $file]} {
        read_design -enumconstraint -define SYNTHESIS -merge bbox -golden -lastmod -noelab -sv09 $file
    } else {
        read_design -enumconstraint -define SYNTHESIS -merge bbox -golden -lastmod -noelab $file
    }
}
elaborate_design -golden -root ${DESIGN} -rootonly -rootonly  

read_design -verilog95   -revised -lastmod -noelab ../Genus/fv/${DESIGN}/fv_map.v.gz
elaborate_design -revised -root ${DESIGN}

uniquify -all -nolib -golden

report_design_data
report_black_box

set_flatten_model -seq_constant
set_flatten_model -seq_constant_x_to 0
set_flatten_model -nodff_to_dlat_zero
set_flatten_model -nodff_to_dlat_feedback
set_flatten_model -hier_seq_merge

set_flatten_model -balanced_modeling

#add_name_alias fv/UDP/fv_map.singlebit.original_name.alias.json.gz -revised
#set_mapping_method -alias -revised
#add_renaming_rule r1alias _reg((\\\[%w\\\])*(/U\\\$%d)*)$ @1 -type dff dlat -both

# Reports the quality of the implementation information.
# This command is only available with LEC 20.10-p100 or later.
set lec_version_required "20.10100"
if {$lec_version >= $lec_version_required} {
    check_verification_information -verbose
}

set_analyze_option -auto -report_map

write_hier_compare_dofile hier_tmp3.lec.do -verbose -noexact_pin_match -constraint -usage \
-replace -balanced_extraction -input_output_pin_equivalence \
-prepend_string "report_design_data; report_unmapped_points -summary; report_unmapped_points -notmapped; report_unmapped_points -extra -unreachable; analyze_datapath -module -verbose; eval analyze_datapath $DATAPATH_SOLVER_OPTION -verbose" \
-append_string "report_compare_data -class nonequivalent -class abort -class notcompared; report_verification -verbose"
run_hier_compare hier_tmp3.lec.do -dynamic_hierarchy -verbose

report_hier_compare_result -dynamicflattened

report_verification -hier -verbose

set_system_mode lec
report_mapped_points
report_unmapped_points -summary
report_unmapped_points -notmapped
report_unmapped_points -extra -unreachable
add_compared_points -all
report_compared_points
compare

report_compare_data
report_compare_data -class nonequivalent -class abort -class notcompared
report_verification -verbose
report_statistics

write_compared_points ${RTL2MAP_REPORTS_PATH}/noneq.compared_points.${DESIGN}.rtl.fv_map.tcl -class noneq -tclmode -replace

set lec_version_required "21.10100"
if {$lec_version >= $lec_version_required} {
    analyze_nonequivalent -source_diagnosis
    report_nonequivalent_analysis > ${RTL2MAP_REPORTS_PATH}/noneq.source_diag.${DESIGN}.rtl.fv_map.rpt
}

report_test_vector -noneq > ${RTL2MAP_REPORTS_PATH}/noneq.test_vector.${DESIGN}.rtl.fv_map.rpt
set_system_mode setup
write_verification_information
report_verification_information

# Reports how effective the implementation information was.
# This command is only available with LEC 18.20-d330 or later.
set lec_version_required "18.20330"
if {$lec_version >= $lec_version_required} {
    report_implementation_information -verbose
}

##############################
# Generate Reports
##############################
write mapped points > ${RTL2MAP_REPORTS_PATH}/mapped_pts.rpt
report unmapped points -summary > ${RTL2MAP_REPORTS_PATH}/unmapped_points.rpt
report compare data -summary > ${RTL2MAP_REPORTS_PATH}/compared_points.rpt
report mapped points -summary > ${RTL2MAP_REPORTS_PATH}/mapped_points.rpt
report design data -summary > ${RTL2MAP_REPORTS_PATH}/design_data.rpt
report design similarity -revised -verbose > ${RTL2MAP_REPORTS_PATH}/similarity(%).rpt
report floating signals -all > ${RTL2MAP_REPORTS_PATH}/floating_signals.rpt
report primary inputs > ${RTL2MAP_REPORTS_PATH}/inputs.rpt
report primary outputs > ${RTL2MAP_REPORTS_PATH}/outputs.rpt
report verification -summary -verbose > ${RTL2MAP_REPORTS_PATH}/verification.rpt
report compare data -CLASS NONEQuivalent > ${RTL2MAP_REPORTS_PATH}/non_equivalent_points.rpt
report statistics > ${RTL2MAP_REPORTS_PATH}/statistics.rpt

puts "No of compare points = [get_compare_points -count]"
puts "No of diff points    = [get_compare_points -NONequivalent -count]"
puts "No of abort points   = [get_compare_points -abort -count]"
puts "No of unknown points = [get_compare_points -unknown -count]"
if {[get_compare_points -count] == 0} {
    puts "---------------------------------"
    puts "ERROR: No compare points detected"
    puts "---------------------------------"
}
if {[get_compare_points -NONequivalent -count] > 0} {
    puts "------------------------------------"
    puts "ERROR: Different Key Points detected"
    puts "------------------------------------"
}
if {[get_compare_points -abort -count] > 0} {
    puts "-----------------------------"
    puts "ERROR: Abort Points detected "
    puts "-----------------------------"
}
if {[get_compare_points -unknown -count] > 0} {
    puts "----------------------------------"
    puts "ERROR: Unknown Key Points detected"
    puts "----------------------------------"
}

# Generate a detailed summary of the run.
# This command is available with LEC 19.10-p100 or later.
set lec_version_required "19.10100"
if {$lec_version >= $lec_version_required} {
    analyze_results -logfiles $logfile
}

vpxmode

puts "LEC completed successfully. Reports saved in reports folder."

