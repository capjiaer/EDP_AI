# Helper Util File
# Util files only contain helper proc definitions for sub_steps to call
# Use via #import source helper.tcl, which will load these proc definitions
# Each sub_step can call these helper procs when needed

# Helper proc: Get timing information
proc helper_get_timing {} {
    puts "Getting timing information..."
    return "timing_info"
}

# Helper proc: Check design status
proc helper_check_design {} {
    puts "Checking design status..."
    return "design_ok"
}

