set RTL_PATH $::env(RTL_PATH)
set LIB_PATH $::env(LIB_PATH)
set OUTPUTS_PATH $::env(OUTPUTS_PATH)

puts "Enter top design name:"
set TOP_NAME [gets stdin]

read_verilog -sv $RTL_PATH/*.sv
hierarchy -check -top $TOP_NAME
proc
opt
fsm
opt
memory
opt
read_liberty -ignore_miss_func $LIB_PATH/slow.lib 
read_liberty -overwrite -ignore_miss_func $LIB_PATH/fast.lib 
techmap
opt
abc -liberty $LIB_PATH/slow.lib -script +strash;dretime;dch;-f;map,-D 1000
clean
write_verilog -noattr -sv -output $OUTPUTS_PATH/$TOP_NAME.v
