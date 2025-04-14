read_verilog -sv $RTL_PATH/*.sv
hierarchy -check -top UDP
proc
opt
fsm
opt
memory
opt
read_liberty -ignore_miss_func 45nm/lib/slow.lib 
read_liberty -overwrite -ignore_miss_func 45nm/lib/fast.lib 
techmap
opt
abc -liberty 45nm/lib/slow.lib -script +strash;dretime;dch;-f;map,-D 1000
clean
write_verilog -noattr yosys_netlist.v
