# EDP Sub Steps Manager - Core Functions
# Core data structures and management functions

namespace eval edp_sub_steps {
    variable sub_steps_list {}
    variable sub_steps_dict {}
    variable current_index -1
    variable step_status {}  ;# Dictionary: index -> status ("pending", "success", "failed")
    
    proc init {sub_steps_config} {
        variable sub_steps_list
        variable sub_steps_dict
        variable step_status
        
        set sub_steps_list {}
        set sub_steps_dict {}
        set step_status {}
        
        if {[llength $sub_steps_config] == 0} {
            puts "WARNING: sub_steps_config is empty"
            return
        }
        
        set len [llength $sub_steps_config]
        
        # Determine format: if even number of elements, might be old format {file_name proc_name ...}
        # If odd number of elements, or all elements look like proc names, then new format {proc_name proc_name ...}
        set is_old_format 0
        if {$len % 2 == 0} {
            # Check if first element looks like a filename (contains .tcl or path separator)
            set first_elem [lindex $sub_steps_config 0]
            if {[string match "*.tcl" $first_elem] || [string match "*/*" $first_elem] || [string match "*\\*" $first_elem]} {
                set is_old_format 1
            }
        }
        
        set idx 0
        if {$is_old_format} {
            # Old format: {file_name proc_name file_name proc_name ...}
            for {set i 0} {$i < $len} {incr i 2} {
                set file_name [lindex $sub_steps_config $i]
                set proc_name [lindex $sub_steps_config [expr {$i + 1}]]
                if {$file_name != "" && $proc_name != ""} {
                    lappend sub_steps_list $proc_name
                    dict set sub_steps_dict $proc_name $file_name
                    dict set step_status $idx "pending"
                    incr idx
                }
            }
        } else {
            # New format (execution plan): {proc_name proc_name ...}
            foreach proc_name $sub_steps_config {
                if {$proc_name != ""} {
                    lappend sub_steps_list $proc_name
                    # Execution plan doesn't have file_name, so don't set sub_steps_dict
                    dict set step_status $idx "pending"
                    incr idx
                }
            }
        }
    }
    
    proc get_all {} {
        variable sub_steps_list
        return $sub_steps_list
    }
    
    proc get_count {} {
        variable sub_steps_list
        return [llength $sub_steps_list]
    }
    
    proc find_index {proc_name} {
        variable sub_steps_list
        return [lsearch -exact $sub_steps_list $proc_name]
    }
    
    # Parse parameter: if number, return index; if string, find index corresponding to proc name
    proc parse_step_ref {ref} {
        variable sub_steps_list
        # Check if pure number (might be index)
        if {[string is integer $ref]} {
            set idx $ref
            if {$idx >= 0 && $idx < [llength $sub_steps_list]} {
                return $idx
            } else {
                puts "ERROR: Index $idx is out of range (0-[expr {[llength $sub_steps_list] - 1}])"
                return -1
            }
        } else {
            # Treat as proc name
            set idx [find_index $ref]
            if {$idx == -1} {
                puts "ERROR: Sub step '$ref' not found"
            }
            return $idx
        }
    }
    
    proc validate_proc {proc_name} {
        variable sub_steps_list
        if {[lsearch -exact $sub_steps_list $proc_name] == -1} {
            puts "ERROR: Sub step '$proc_name' not found"
            edp_run -info
            return 0
        }
        return 1
    }
    
    # Check if there are skipped steps
    proc check_skipped_steps {target_idx} {
        variable step_status
        variable sub_steps_list
        
        set skipped_steps {}
        for {set i 0} {$i < $target_idx} {incr i} {
            set status [get_step_status $i]
            if {$status == "pending"} {
                set proc_name [lindex $sub_steps_list $i]
                lappend skipped_steps [list $i $proc_name]
            }
        }
        return $skipped_steps
    }
    
    proc execute_proc {proc_name idx} {
        variable current_index
        variable step_status
        puts "========== Executing: $proc_name =========="
        if {[catch {$proc_name} result]} {
            puts "========== FAILED: $proc_name =========="
            puts "ERROR: $result"
            puts "=========================================="
            set current_index $idx
            dict set step_status $idx "failed"
            return 0
        }
        puts "========== SUCCESS: $proc_name =========="
        puts "=========================================="
        set current_index $idx
        dict set step_status $idx "success"
        return 1
    }
    
    proc get_step_status {idx} {
        variable step_status
        if {[dict exists $step_status $idx]} {
            return [dict get $step_status $idx]
        }
        return "pending"
    }
    
    proc run_range {from_proc to_proc skip_list {force 0}} {
        variable sub_steps_list
        
        set from_idx 0
        set to_idx [expr {[llength $sub_steps_list] - 1}]
        
        if {$from_proc != ""} {
            set from_idx [parse_step_ref $from_proc]
            if {$from_idx == -1} {
                return 0
            }
        }
        
        if {$to_proc != ""} {
            set to_idx [parse_step_ref $to_proc]
            if {$to_idx == -1} {
                return 0
            }
        }
        
        if {$from_idx > $to_idx} {
            puts "ERROR: Invalid range (from_idx=$from_idx > to_idx=$to_idx)"
            return 0
        }
        
        # Check if there are skipped steps (unexecuted steps before from_idx)
        set skipped_steps [check_skipped_steps $from_idx]
        if {[llength $skipped_steps] > 0 && !$force} {
            puts "WARNING: The following steps will be skipped:"
            foreach skipped $skipped_steps {
                set skipped_idx [lindex $skipped 0]
                set skipped_proc [lindex $skipped 1]
                puts "  \[$skipped_idx\] $skipped_proc"
            }
            puts ""
            puts "To execute anyway, use: edp_run -from $from_proc -to $to_proc -force"
            puts "Or execute skipped steps first."
            return 0
        }
        
        # Check if there are already executed steps in range (non-force mode)
        if {!$force} {
            set already_executed {}
            for {set i $from_idx} {$i <= $to_idx} {incr i} {
                set status [get_step_status $i]
                if {$status != "pending"} {
                    set proc_name [lindex $sub_steps_list $i]
                    lappend already_executed [list $i $proc_name $status]
                }
            }
            if {[llength $already_executed] > 0} {
                puts "WARNING: The following steps have already been executed:"
                foreach executed $already_executed {
                    set exec_idx [lindex $executed 0]
                    set exec_proc [lindex $executed 1]
                    set exec_status [lindex $executed 2]
                    puts "  \[$exec_idx\] $exec_proc (status: $exec_status)"
                }
                puts ""
                puts "To re-execute, use: edp_run -from $from_proc -to $to_proc -force"
                return 0
            }
        }
        
        set executed 0
        set failed 0
        # Convert indices in skip_list to proc_name, build skip_indices set
        set skip_indices {}
        foreach skip_ref $skip_list {
            set skip_idx [parse_step_ref $skip_ref]
            if {$skip_idx != -1} {
                lappend skip_indices $skip_idx
            }
        }
        
        for {set i $from_idx} {$i <= $to_idx} {incr i} {
            set proc_name [lindex $sub_steps_list $i]
            # Check if in skip list (by index or proc_name)
            if {[lsearch -exact $skip_indices $i] != -1 || [lsearch -exact $skip_list $proc_name] != -1} {
                puts "Skipping: \[$i\] $proc_name"
                continue
            }
            if {![execute_proc $proc_name $i]} {
                set failed 1
                puts "Execution stopped at \[$i\] $proc_name due to failure"
                return 0
            }
            incr executed
        }
        if {$executed > 0} {
            puts "Successfully executed $executed sub_step(s)"
        }
        return 1
    }
    
    proc run_single {step_ref {force 0}} {
        variable sub_steps_list
        set idx [parse_step_ref $step_ref]
        if {$idx == -1} {
            return 0
        }
        
        set proc_name [lindex $sub_steps_list $idx]
        set status [get_step_status $idx]
        
        # Check if step has already been executed
        if {$status != "pending" && !$force} {
            puts "WARNING: Step \[$idx\] $proc_name has already been executed (status: $status)"
            puts "To re-execute, use: edp_run $step_ref -force"
            return 0
        }
        
        # Check if there are skipped steps
        set skipped_steps [check_skipped_steps $idx]
        if {[llength $skipped_steps] > 0 && !$force} {
            puts "WARNING: The following steps will be skipped:"
            foreach skipped $skipped_steps {
                set skipped_idx [lindex $skipped 0]
                set skipped_proc [lindex $skipped 1]
                puts "  \[$skipped_idx\] $skipped_proc"
            }
            puts ""
            puts "To execute anyway, use: edp_run $step_ref -force"
            puts "Or execute skipped steps first."
            return 0
        }
        
        return [execute_proc $proc_name $idx]
    }
    
    proc run_next {} {
        variable sub_steps_list
        variable current_index
        set next_idx [expr {$current_index + 1}]
        if {$next_idx >= [llength $sub_steps_list]} {
            puts "All sub_steps have been executed"
            return 0
        }
        set proc_name [lindex $sub_steps_list $next_idx]
        return [run_single $proc_name 1]
    }
    
    proc skip_next {} {
        variable sub_steps_list
        variable current_index
        variable step_status
        set next_idx [expr {$current_index + 1}]
        if {$next_idx >= [llength $sub_steps_list]} {
            puts "No more sub_steps to skip"
            return 0
        }
        set proc_name [lindex $sub_steps_list $next_idx]
        puts "========== SKIPPED: $proc_name =========="
        puts "=========================================="
        set current_index $next_idx
        dict set step_status $next_idx "skipped"
        return 1
    }
    
    proc get_current_index {} {
        variable current_index
        return $current_index
    }
    
    proc get_current_step {} {
        variable sub_steps_list
        variable current_index
        if {$current_index < 0 || $current_index >= [llength $sub_steps_list]} {
            return ""
        }
        return [lindex $sub_steps_list $current_index]
    }
    
    proc get_next_step {} {
        variable sub_steps_list
        variable current_index
        set next_idx [expr {$current_index + 1}]
        if {$next_idx >= [llength $sub_steps_list]} {
            return ""
        }
        return [lindex $sub_steps_list $next_idx]
    }
}

