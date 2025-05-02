#=========================================================================
# START.tcl - Logic Lance Integration for Synthesis Flow
#=========================================================================
# This script sources a series of TCL scripts based on an execution order.
# It reads the execution order from the environment variable "order" passed
# by Logic Lance or defaults to the predefined sequence.
#
# Author : Hemant Kumar DM
# Date   : 2025
#

#-------------------------------------------------------------------------
# Fetch Execution Order (from Logic Lance configuration)
#-------------------------------------------------------------------------
# The "order" environment variable is set in the flow_config.json file
# or passed from Logic Lance at runtime. If not provided, use default order.
set order [split $::env(order) ","]

# If order is not defined, set default order
if {[llength $order] == 0} {
    set order {
        "setup-session.tcl"
        "designer-interface.tcl"
        "read-design.tcl"
        "constraints.tcl"
        "compile.tcl"
        "generate-results.tcl"
    }
}

#-------------------------------------------------------------------------
# Run the Scripts in the Defined Order
#-------------------------------------------------------------------------
foreach tcl $order {
    # First, try to find the script in the "inputs" directory
    if {[file exists "inputs/$tcl"]} {
        puts "\n  > Info: Sourcing \"inputs/$tcl\"\n"
        source -echo -verbose "inputs/$tcl"
    
    # If not found in "inputs", check the "scripts" directory within Logic Lance
    } elseif {[file exists "flow_gui/scripts/cadence/synthesis/$tcl"]} {
        puts "\n  > Info: Sourcing \"flow_gui/scripts/cadence/synthesis/$tcl\"\n"
        source -echo -verbose "flow_gui/scripts/cadence/synthesis/$tcl"
    
    # If still not found, print a warning and exit
    } else {
        puts "Warn: Did not find $tcl in either 'inputs' or 'scripts'"
        exit 1
    }
}

# End of synthesis flow
puts "Synthesis flow completed successfully!"
exit
