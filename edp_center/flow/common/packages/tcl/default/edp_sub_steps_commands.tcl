# EDP Sub Steps Manager - Command Interface
# Command parsing and execution interface

# Helper function to parse -skip parameter
proc edp_run_parse_skip {args start_idx} {
    set skip_list {}
    set i $start_idx
    while {$i < [llength $args]} {
        set arg [lindex $args $i]
        if {$arg == "-skip"} {
            incr i
            while {$i < [llength $args] && [string index [lindex $args $i] 0] != "-"} {
                lappend skip_list [lindex $args $i]
                incr i
            }
        } else {
            incr i
        }
    }
    return $skip_list
}

# Helper function: automatically show sub_steps status after edp_run execution
proc edp_run_show_info {} {
    # Directly call edp_run -info to show sub_steps status
    edp_run -info
}

proc edp_run {args} {
    if {[llength $args] == 0} {
        edp_run -help
        return
    }
    
    set cmd [lindex $args 0]
    
    # If not starting with -, treat as step_ref (proc_name or index)
    if {[string index $cmd 0] != "-"} {
        # Check if -force parameter exists
        set force 0
        if {[lsearch -exact $args "-force"] != -1} {
            set force 1
        }
        set result [edp_sub_steps::run_single $cmd $force]
        
        # Automatically show sub_steps status after execution
        if {$result} {
            edp_run_show_info
        }
        return
    }
    
    if {$cmd == "-init"} {
        set arg [lindex $args 1]
        if {$arg == ""} {
            puts "ERROR: -init requires sub_steps_config"
            return
        }
        
        if {[string match "*\(*" $arg]} {
            if {[regexp {^(\w+)\((.*)\)$} $arg match array_name key]} {
                if {[info exists ::${array_name}($key)]} {
                    set sub_steps_config [set ::${array_name}($key)]
                } else {
                    puts "ERROR: Variable '$arg' does not exist"
                    return
                }
            } else {
                puts "ERROR: Invalid variable name format"
                return
            }
        } else {
            set sub_steps_config [lrange $args 1 end]
        }
        
        if {[llength $sub_steps_config] == 0} {
            puts "ERROR: sub_steps_config is empty"
            return
        }
        
        edp_sub_steps::init $sub_steps_config
        puts "Sub steps manager initialized."
        edp_run -info
    } elseif {$cmd == "-info"} {
        set all_steps [edp_sub_steps::get_all]
        set count [edp_sub_steps::get_count]
        if {$count == 0} {
            puts "No sub_steps defined"
            return
        }
        
        set current_idx [edp_sub_steps::get_current_index]
        set next_step [edp_sub_steps::get_next_step]
        
        puts "========== Available Sub Steps =========="
        set idx 0
        set success_count 0
        set failed_count 0
        set pending_count 0
        set skipped_count 0
        
        # Calculate maximum proc_name length for alignment
        set max_name_len 0
        foreach proc_name $all_steps {
            set name_len [string length $proc_name]
            if {$name_len > $max_name_len} {
                set max_name_len $name_len
            }
        }
        
        foreach proc_name $all_steps {
            set status [edp_sub_steps::get_step_status $idx]
            set status_mark ""
            
            if {$status == "success"} {
                set status_mark "\[OK\]"
                incr success_count
            } elseif {$status == "failed"} {
                set status_mark "\[FAILED\]"
                incr failed_count
            } elseif {$status == "skipped"} {
                set status_mark "\[SKIPPED\]"
                incr skipped_count
            } else {
                set status_mark "\[PENDING\]"
                incr pending_count
            }
            
            # Format output, align status markers
            set formatted_name [format "%-*s" $max_name_len $proc_name]
            set formatted_status [format "%9s" $status_mark]
            
            # If this is the next to execute, add marker
            if {$idx == [expr {$current_idx + 1}] && $next_step != ""} {
                puts "  \[$idx\] $formatted_name $formatted_status  <-- next"
            } else {
                puts "  \[$idx\] $formatted_name $formatted_status"
            }
            incr idx
        }
        puts "========================================="
        puts "Total: $count sub_step(s)"
        puts "  Success: $success_count"
        puts "  Failed:  $failed_count"
        puts "  Skipped: $skipped_count"
        puts "  Pending: $pending_count"
        if {$current_idx >= 0} {
            set last_step [lindex $all_steps $current_idx]
            set last_status [edp_sub_steps::get_step_status $current_idx]
            puts "Last executed: \[$current_idx\] $last_step ($last_status)"
        } else {
            puts "Last executed: None (not started)"
        }
        if {$next_step != ""} {
            puts "Next to execute: \[[expr {$current_idx + 1}]\] $next_step"
        } else {
            puts "Next to execute: None (all completed)"
        }
        puts "========================================="
    } elseif {$cmd == "-next"} {
        # Check if -skip parameter exists
        if {[lsearch -exact $args "-skip"] != -1} {
            set result [edp_sub_steps::skip_next]
            if {!$result} {
                set current_idx [edp_sub_steps::get_current_index]
                set count [edp_sub_steps::get_count]
                if {$current_idx >= 0 && [expr {$current_idx + 1}] < $count} {
                    puts "No more sub_steps to skip"
                }
            }
        } else {
            set result [edp_sub_steps::run_next]
            if {!$result} {
                # run_next already printed message, no need to print again here
                # Only handle other cases
                set current_idx [edp_sub_steps::get_current_index]
                set count [edp_sub_steps::get_count]
                if {$current_idx >= 0 && [expr {$current_idx + 1}] < $count} {
                    puts "No more sub_steps to execute"
                }
            } else {
                # Automatically show sub_steps status after execution
                edp_run_show_info
            }
        }
    } elseif {$cmd == "-from"} {
        set from_proc [lindex $args 1]
        set to_proc ""
        set skip_list {}
        set force 0
        
        if {$from_proc == ""} {
            puts "ERROR: -from requires a step reference (index or proc name)"
            return
        }
        
        # Parse -to, -skip and -force parameters
        set i 2
        while {$i < [llength $args]} {
            set arg [lindex $args $i]
            if {$arg == "-to"} {
                incr i
                set to_proc [lindex $args $i]
                incr i
            } elseif {$arg == "-skip"} {
                incr i
                while {$i < [llength $args] && [string index [lindex $args $i] 0] != "-"} {
                    lappend skip_list [lindex $args $i]
                    incr i
                }
            } elseif {$arg == "-force"} {
                set force 1
                incr i
            } else {
                incr i
            }
        }
        
        set result [edp_sub_steps::run_range $from_proc $to_proc $skip_list $force]
        # Automatically show sub_steps status after execution
        if {$result} {
            edp_run_show_info
        }
    } elseif {$cmd == "-to"} {
        set to_proc [lindex $args 1]
        set skip_list [edp_run_parse_skip $args 2]
        set force 0
        
        # Check if -force parameter exists
        if {[lsearch -exact $args "-force"] != -1} {
            set force 1
        }
        
        if {$to_proc == ""} {
            puts "ERROR: -to requires a step reference (index or proc name)"
            return
        }
        set result [edp_sub_steps::run_range "" $to_proc $skip_list $force]
        # Automatically show sub_steps status after execution
        if {$result} {
            edp_run_show_info
        }
    } elseif {$cmd == "-all"} {
        set skip_list [edp_run_parse_skip $args 1]
        set all_steps [edp_sub_steps::get_all]
        if {[llength $all_steps] == 0} {
            puts "No sub_steps defined"
            return
        }
        set result [edp_sub_steps::run_range [lindex $all_steps 0] [lindex $all_steps end] $skip_list]
        # Automatically show sub_steps status after execution
        if {$result} {
            edp_run_show_info
        }
    } elseif {$cmd == "-help"} {
        puts "========== EDP Sub Steps Manager Help =========="
        puts "  edp_run -init <var_name>     Initialize with variable (e.g., edp(execution_plan,place))"
        puts "  edp_run -info                Display all sub_steps with current position"
        puts "  edp_run -next                 Execute next sub_step"
        puts "  edp_run -next -skip           Skip next sub_step"
        puts "  edp_run <step_ref>            Execute specified sub_step (index or proc_name)"
        puts "  edp_run <step_ref> -force     Execute specified sub_step with force flag"
        puts "  edp_run -from <step_ref>      Execute from step to end"
        puts "  edp_run -from <step_ref> -to <step_ref>  Execute range"
        puts "  edp_run -from <step_ref> -to <step_ref> -skip <step_ref1> ...  Execute range with skip"
        puts "  edp_run -from <step_ref> -to <step_ref> -force  Execute range with force"
        puts "  edp_run -to <step_ref>        Execute from start to step"
        puts "  edp_run -to <step_ref> -skip <step_ref1> ...  Execute to step with skip"
        puts "  edp_run -to <step_ref> -force  Execute to step with force"
        puts "  edp_run -all                  Execute all steps"
        puts "  edp_run -all -skip <step_ref1> ...  Execute all with skip"
        puts ""
        puts "  Note: <step_ref> can be either:"
        puts "    - An index number (e.g., 0, 1, 2)"
        puts "    - A proc name (e.g., pnr_innovus::restore_design)"
        puts ""
        puts "  If you try to execute a step that:"
        puts "    - Skips previous pending steps, or"
        puts "    - Has already been executed"
        puts "  you'll be warned. Use -force to execute anyway."
        puts "=============================================="
    } else {
        puts "ERROR: Unknown command: $cmd"
        puts "Use 'edp_run -help' for help"
    }
}

