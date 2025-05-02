puts "Enter the TOP module Name"
gets stdin DESIGN

set SYN_EFF high
set DATE [clock format [clock seconds] -format "%b%d-%T"] 

# Genus folders
set LOG_PATH $LOG_PATH/synthesis/
set OUTPUTS_PATH $OUTPUTS_PATH/synthesis/
set REPORTS_PATH $REPORTS_PATH/synthesis/

# Subdirectories
set early_CD_report_path ${REPORTS_PATH}/Check_design/early
set early_TL_report_path ${REPORTS_PATH}/Timing_lint/early
set generic_report_path ${REPORTS_PATH}/generic
set map_report_path ${REPORTS_PATH}/map
set opt_report_path ${REPORTS_PATH}/opt
set final_report_path ${REPORTS_PATH}/final
set late_CD_report_path ${REPORTS_PATH}/Check_design/late
set late_TL_report_path ${REPORTS_PATH}/Timing_lint/late

# Other tools paths
set LEC_PATH ${OUTPUTS_PATH}/LEC/Gen_by_genus
set LEC_LOG_PATH ${OUTPUTS_PATH}/LEC/logs
set TEMPUS_PATH ${OUTPUTS_PATH}/TEMPUS/Gen_by_genus
set INNOVUS_PATH ${OUTPUTS_PATH}/INNOVUS/Gen_by_genus

# ======= CREATE ALL NEEDED DIRECTORIES =======
foreach dir [list \
    $LOG_PATH \
    $OUTPUTS_PATH \
    $REPORTS_PATH \
    $early_CD_report_path \
    $early_TL_report_path \
    $generic_report_path \
    $map_report_path \
    $opt_report_path \
    $final_report_path \
    $late_CD_report_path \
    $late_TL_report_path \
    $LEC_PATH \
    $LEC_LOG_PATH \
    $TEMPUS_PATH \
    $INNOVUS_PATH \
] {
    if {![file exists $dir]} {
        file mkdir $dir
    }
}

##############################
# Input Paths
##############################

set SLOW_LIB $LIB_PATH/slow.lib
set FAST_LIB $LIB_PATH/fast.lib
set LEF1 $LEF_PATH/gsclib045_tech.lef
set LEF2 $LEF_PATH/gsclib045_macro.lef

##############################
# Load Libraries
##############################

read_libs -min_libs ${FAST_LIB} -max_libs ${SLOW_LIB}

##############################
# Load Design
##############################

if {[llength $RTL_PATH] == 0} {
    puts "Error: No HDL files found or specified."
    exit 1
} else {
    puts "Reading the following HDL files: $RTL_PATH"
    foreach file $RTL_PATH {
        puts "Processing file: $file"
        if {[string match *.sv $file]} {
            read_hdl -language sv $file
        } else {
            read_hdl $file
        }
    }
}

puts "Elaborating Design"
elaborate $DESIGN
puts "Runtime & Memory after 'read_hdl'"

check_design 
check_design -all > ${early_CD_report_path}/all_CD.rpt

uniquify $DESIGN -verbose

read_sdc ${SDC_PATH}/${DESIGN}_Constraints.sdc

path_adjust -from [all_inputs] -to [all_registers] -delay -1500 -name PA_I2O
path_adjust -from [all_inputs] -to [all_outputs] -delay -1500 -name PA_I2C
path_adjust -from [all_registers] -to [all_outputs] -delay -1500 -name PA_C2O
path_adjust -from [all_registers] -to [all_registers] -delay -1500 -name PA_C2C

report timing -lint -verbose > ${early_TL_report_path}/all_TL.rpt

##############################
# Synthesize Design - Generic
##############################

set_db syn_generic_effort $SYN_EFF
syn_gen
puts "Runtime & Memory after 'syn_gen'"
time_info GENERIC

report_dp > $generic_report_path/${DESIGN}_datapath.rpt
write_snapshot -directory $generic_report_path -tag generic
report_summary -directory $generic_report_path
write_hdl > ${OUTPUTS_PATH}/${DESIGN}_generic.v
write_sdc > ${OUTPUTS_PATH}/${DESIGN}_generic.sdc

##############################
# Synthesize Design - Map Gates
##############################

set_db syn_map_effort $SYN_EFF
syn_map
puts "Runtime & Memory after 'syn_map'"
time_info MAPPED

report_dp > $map_report_path/${DESIGN}_datapath.rpt
write_snapshot -directory $map_report_path -tag map
report_summary -directory $map_report_path
write_hdl > ${OUTPUTS_PATH}/${DESIGN}_map.v
write_sdc > ${OUTPUTS_PATH}/${DESIGN}_map.sdc

write_do_lec -golden_design rtl \
             -revised_design ${OUTPUTS_PATH}/${DESIGN}_map.v \
             -checkpoint ${OUTPUTS_PATH}/${DESIGN}_check_point.ckp \
             -no_exit \
             -verbose \
             -logfile ${LEC_LOG_PATH}/rtl_to_map.lec.log > ${LEC_PATH}/rtl_to_map.lec.do

##############################
# Optimize Netlist
##############################

set_db syn_opt_effort $SYN_EFF
syn_opt
puts "Runtime & Memory after 'syn_opt'"
time_info OPT

report_dp > $opt_report_path/${DESIGN}_datapath.rpt
write_snapshot -directory $opt_report_path -tag netlist
report_summary -directory $opt_report_path
report_timing -path_type full -max_paths 1000000 -max_slack 0 > ${final_report_path}/timing_all_paths.rpt
write_reports -directory $final_report_path -tag final

write_hdl > ${OUTPUTS_PATH}/${DESIGN}_netlist.v
write_sdc > ${OUTPUTS_PATH}/${DESIGN}_netlist.sdc

write_do_lec -golden_design rtl \
             -revised_design ${OUTPUTS_PATH}/${DESIGN}_netlist.v \
             -checkpoint ${OUTPUTS_PATH}/${DESIGN}_check_point.ckp \
             -no_exit \
             -verbose \
             -logfile ${LEC_LOG_PATH}/rtl_to_final.lec.log > ${LEC_PATH}/rtl_to_final.lec.do

check_design 
check_design -all > ${late_CD_report_path}/all_CD.rpt
report timing -lint -verbose > ${late_TL_report_path}/all_TL.rpt

##############################
# SDF, SPEF, Tempus and Innovus Generation
##############################

write_sdf -version 2.1 -recrem split -setuphold merge_when_paired -edges check_edge > ${OUTPUTS_PATH}/${DESIGN}.sdf

write_tempus -libs ${LIB_PATH}/${SLOW_LIB} \
             -netlist ${OUTPUTS_PATH}/${DESIGN}_netlist.v \
             -no_exit \
             -sdf ${OUTPUTS_PATH}/${DESIGN}.sdf \
             -sdc ${OUTPUTS_PATH}/${DESIGN}_netlist.sdc > ${TEMPUS_PATH}/${DESIGN}_tempus.tcl

write_design -innovus -base_name ${INNOVUS_PATH}/${DESIGN}

puts "Final Runtime & Memory."
time_info FINAL
puts "============================"
puts "Synthesis Finished ........."
puts "============================"

file rename genus.cmd ${LOG_PATH}/genus_${DATE}.cmd     
file rename genus.log ${LOG_PATH}/genus_${DATE}.log
