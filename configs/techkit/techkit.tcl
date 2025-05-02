#=========================================================================
# TECHKIT Setup TCL File
#=========================================================================
# This file is sourced by every ASIC flow tcl script that uses the
# TECHKIT. This allows us to set TECHKIT-specific variables.

#-------------------------------------------------------------------------
# TECHKIT_PROCESS
#-------------------------------------------------------------------------
# This variable is used by the tool flow to automatically
# configure process-specific options (e.g., extraction engines).
#
# The process can be "28", "180", etc., with units in nm.

set TECHKIT_PROCESS 45  ;# Change to the relevant process node, e.g., 28nm, 180nm

#-------------------------------------------------------------------------
# Preferred routing layers
#-------------------------------------------------------------------------
# These variables are used by tools like Synopsys DC and Innovus.
# Modify for your design kit's specific routing layers.

set TECHKIT_MIN_ROUTING_LAYER_DC metal2
set TECHKIT_MAX_ROUTING_LAYER_DC metal7

set TECHKIT_MAX_ROUTING_LAYER_INNOVUS 7

#-------------------------------------------------------------------------
# Power mesh layers
#-------------------------------------------------------------------------
# Used for the coarse power mesh.

set TECHKIT_POWER_MESH_BOT_LAYER 8
set TECHKIT_POWER_MESH_TOP_LAYER 9

#-------------------------------------------------------------------------
# TECHKIT_DRIVING_CELL
#-------------------------------------------------------------------------
# This variable should indicate which cell to use with the
# set_driving_cell command. Usually, an inverter cell is used.

set TECHKIT_DRIVING_CELL "INV_X2"

#-------------------------------------------------------------------------
# TECHKIT_TYPICAL_ON_CHIP_LOAD
#-------------------------------------------------------------------------
# Default timing constraints assuming driving another block of logic.
# Adjust load capacitance as necessary for your design.

set TECHKIT_TYPICAL_ON_CHIP_LOAD 7 ;# Load capacitance in picofarads

#-------------------------------------------------------------------------
# TECHKIT_FILLER_CELLS
#-------------------------------------------------------------------------
# List of filler cells in the library, ordered from largest to smallest.

set TECHKIT_FILLER_CELLS \
  "FILLCELL_X32 \
   FILLCELL_X16 \
   FILLCELL_X8 \
   FILLCELL_X4 \
   FILLCELL_X2 \
   FILLCELL_X1"

#-------------------------------------------------------------------------
# TECHKIT_TIE_CELLS
#-------------------------------------------------------------------------
# Cells for tying high to VDD and low to VSS.

set TECHKIT_TIE_CELLS \
  "LOGIC1_X1 \
   LOGIC0_X1"

#-------------------------------------------------------------------------
# TECHKIT_WELL_TAP_CELL
#-------------------------------------------------------------------------
# Well tap cell and its spacing rule, if applicable.

set TECHKIT_WELL_TAP_CELL     "WELLTAP_X1"
set TECHKIT_WELL_TAP_INTERVAL 120

#-------------------------------------------------------------------------
# TECHKIT_END_CAP_CELL
#-------------------------------------------------------------------------
# End cap cells, if needed.

set TECHKIT_END_CAP_CELL ""

#-------------------------------------------------------------------------
# TECHKIT_ANTENNA_CELL
#-------------------------------------------------------------------------
# Antenna diode cell to avoid antenna DRC violations.

set TECHKIT_ANTENNA_CELL "ANTENNA_X1"

#-------------------------------------------------------------------------
# TECHKIT_LVS_EXCLUDE_CELL_LIST (OPTIONAL)
#-------------------------------------------------------------------------
# Exclude physical-only cells from the LVS netlist.

set TECHKIT_LVS_EXCLUDE_CELL_LIST \
  "FILL* \
   WELLTAP*"

#-------------------------------------------------------------------------
# TECHKIT_VIRTUOSO_EXCLUDE_CELL_LIST (OPTIONAL)
#-------------------------------------------------------------------------
# Exclude cells from Virtuoso simulation (e.g., decaps).

set TECHKIT_VIRTUOSO_EXCLUDE_CELL_LIST \
  "FILL* \
   WELLTAP*"

#-------------------------------------------------------------------------
# TECHKIT_BUF_CELL_LIST (OPTIONAL)
#-------------------------------------------------------------------------
# List of buffer cells to use for timing ECOs.

set TECHKIT_BUF_CELL_LIST \
  "BUF_X1 \
   BUF_X2 \
   BUF_X4 \
   BUF_X8 \
   BUF_X16 \
   BUF_X32"

#-------------------------------------------------------------------------
# Support for open-source tools (if applicable)
#-------------------------------------------------------------------------
# Extra variables for open-source toolchains.

set TECHKIT_TIE_HI_CELL "LOGIC1_X1"
set TECHKIT_TIE_LO_CELL "LOGIC0_X1"
set TECHKIT_TIE_HI_PORT "Z"
set TECHKIT_TIE_LO_PORT "Z"

set TECHKIT_MIN_BUF_CELL   "BUF_X1"
set TECHKIT_MIN_BUF_PORT_I "A"
set TECHKIT_MIN_BUF_PORT_O "Z"
