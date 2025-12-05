# EDP Sub Steps Manager
# Interactive sub_steps debugging management system
# 
# Main entry file, loads core functions and command interface

# Get current script directory
set edp_sub_steps_dir [file dirname [file normalize [info script]]]

# Load core functions
source [file join $edp_sub_steps_dir edp_sub_steps_core.tcl]

# Load command interface
source [file join $edp_sub_steps_dir edp_sub_steps_commands.tcl]
