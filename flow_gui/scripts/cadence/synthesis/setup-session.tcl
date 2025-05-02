#=========================================================================
# setup-session.tcl (LogicLance)
#=========================================================================
# Description : Sets up design kit (TECHKIT) paths and tool-specific variables
# Author      : LogicLance Team
#=========================================================================

puts "🔧 Setting up session for synthesis..."

#-------------------------------------------------------------------------
# Load techkit variables
#-------------------------------------------------------------------------

set techkit_tcl "$::env(LOGICLANCE_ROOT)/configs/techkit/techkit.tcl"


if {[file exists $techkit_tcl]} {
    puts "📦 Sourcing TECHKIT file: $techkit_tcl"
    source -echo -verbose $techkit_tcl
} else {
    puts "❌ ERROR: TECHKIT file not found at $techkit_tcl"
    exit 1
}



#-------------------------------------------------------------------------
# Set tool attributes
#-------------------------------------------------------------------------

if {[info exists vars(libs_typical,timing)]} {
    set_attr library $vars(libs_typical,timing)
    puts "🔧 Library set to: $vars(libs_typical,timing)"
}

if {[info exists vars(lef_files)]} {
    set_attr lef_library $vars(lef_files)
    puts "🔧 LEF library set to: $vars(lef_files)"
}

if {[info exists vars(qrcTechFile)] && [file exists $vars(qrcTechFile)]} {
    set_attr qrc_tech_file $vars(qrcTechFile)
    puts "🔧 QRC tech file set to: $vars(qrcTechFile)"
}

if {[info exists vars(capTableFile)] && [file exists $vars(capTableFile)]} {
    set_attr cap_table_file $vars(capTableFile)
    puts "🔧 Cap table file set to: $vars(capTableFile)"
}

set_attr hdl_flatten_complex_port true
set_attr hdl_resolve_instance_with_libcell true

#-------------------------------------------------------------------------
# Cell avoid list
#-------------------------------------------------------------------------

if {[info exists TECHKIT_DONT_USE_CELL_LIST]} {
    puts "⚠️  Avoiding cells listed in TECHKIT_DONT_USE_CELL_LIST"
    set_attribute avoid true [get_lib_cells $TECHKIT_DONT_USE_CELL_LIST]
}

puts "✅ setup-session.tcl complete."
