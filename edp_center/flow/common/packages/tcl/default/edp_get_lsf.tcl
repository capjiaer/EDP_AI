# Register the package
package provide lsf_info 1.0

# This package help to gen tempfile, do file key world replacement
# Create namespace
namespace eval ::lsf_info {
	namespace export get_lsf_info
}

#############################################################################################################################
# Description: this proc help to get lsf information and resource lsf information from full.tcl, to build inside lsf run if exec cmds required
# Arguments: 
#		flow_name		- get lsf info by flow level information
#
# Example: lsf_info::get_lsf_info temp_file ext_starrc
# Return: array lsf | bsub_info | resource_str
#############################################################################################################################

proc ::lsf_info::get_lsf_info {flow_name} {
    global project lsf
    # lsf info merge
    # Some default values:
    set lsf(queue) "normal"
    set lsf(lsf_opt) "-Ip"
    set lsf(memory) "500"
    set lsf(span) 1
    set lsf(pre_lsf) ""
    set lsf(cpu_num) 4
    set lsf(machine) ""
    upvar 1 $flow_name flow_array
    foreach ele {cpu_num lsf memory pre_lsf queue span tool_opt log_info log_redirection lsf_opt machine} {
        #Initial every one 20250219
        if {[info exists flow_array(default,$ele)]} {
            set lsf($ele) $flow_array(default,$ele)
        }

        if {[info exists flow_array($project(step),$ele)]} {
            set lsf($ele) $flow_array($project(step),$ele)
        }
    }
    set machine_info ""
    if {$lsf(machine) ne ""} {
        set machine_value [join $lsf(machine) ","]
        set $machine_info "-m \"$machine_value\""
    }
    set resource_str    "-n $lsf(cpu_num) -R \"rusage\[mem=$lsf(memory)\] span\[hosts=$lsf(span)\]\""
    set bsub_info       "$lsf(pre_lsf) bsub $lsf(lsf_opt) $machine_info -q $lsf(queue) $resource_str"
    set bsub_info       [regsub -all {\s+} $bsub_info " "]

    return [list $bsub_info $resource_str]
}


