# Create namespace for EDP variable management system
namespace eval ::edp_var {
    # Global storage for all variable information
    variable protected
    variable allowed_values
    variable descriptions
    
    # Initialize storage arrays
    array set protected {}
    array set allowed_values {}
    array set descriptions {}
}

# ==================== Unified Variable Configuration ====================
# Configure variable with protection, constraint, and description in one call
# Usage: edp_configure_var varName -protect value -constraint "val1 val2" -description "desc"
proc edp_configure_var {varName args} {
    set protect_value ""
    set constraint_value ""
    set description_value ""
    
    # Parse arguments
    set i 0
    while {$i < [llength $args]} {
        set arg [lindex $args $i]
        switch -exact $arg {
            "-protect" {
                incr i
                if {$i < [llength $args]} {
                    set protect_value [lindex $args $i]
                }
            }
            "-constraint" {
                incr i
                if {$i < [llength $args]} {
                    set constraint_value [lindex $args $i]
                }
            }
            "-description" {
                incr i
                if {$i < [llength $args]} {
                    set description_value [lindex $args $i]
                }
            }
            default {
                error "Unknown option: $arg. Use -protect, -constraint, or -description"
            }
        }
        incr i
    }
    
    # Apply protection if specified
    if {$protect_value != ""} {
        edp_protect_var $varName $protect_value
    }
    
    # Apply constraint if specified
    if {$constraint_value != ""} {
        edp_constraint_var $varName $constraint_value
    }
    
    # Apply description if specified
    if {$description_value != ""} {
        edp_descript_var $varName $description_value
    }
}

# ==================== Batch Configuration ====================
# Configure multiple variables at once from a dictionary
# Usage: edp_configure_vars {
#     varName1 {-protect val1 -description "desc1"}
#     varName2 {-protect val2 -constraint "val1 val2" -description "desc2"}
# }
proc edp_configure_vars {varConfigDict} {
    foreach {varName config} $varConfigDict {
        eval edp_configure_var [list $varName] $config
    }
}

# ==================== Protect System ====================
# Protect variable from modification
proc edp_protect_var {varName value} {
    # Check if it's an array element
    if {[regexp {^(.+)\((.+)\)$} $varName -> arrayName elementPath]} {
        upvar 1 $arrayName array
        
        # Set initial value for array element
        set array($elementPath) $value
        
        # Store protected value
        set ::edp_var::protected($varName) $value
        
        # Add write trace
        trace add variable array write [list ::edp_var::protect_array_trace $varName $elementPath]
    } else {
        upvar 1 $varName var
        
        # Set initial value for variable
        set var $value
        
        # Store protected value
        set ::edp_var::protected($varName) $value
        
        # Add write trace
        trace add variable var write [list ::edp_var::protect_trace $varName]
    }
}

# Remove protection from variable
proc edp_unprotect_var {varName} {
    # Check if variable is protected
    if {![info exists ::edp_var::protected($varName)]} {
        puts "Warning: Variable '$varName' is not protected."
        return
    }
    
    if {[regexp {^(.+)\((.+)\)$} $varName -> arrayName elementPath]} {
        upvar 1 $arrayName array
        if {[info exists array]} {
            trace remove variable array write [list ::edp_var::protect_array_trace $varName $elementPath]
        }
    } else {
        upvar 1 $varName var
        if {[info exists var]} {
            trace remove variable var write [list ::edp_var::protect_trace $varName]
        }
    }
    
    # Remove from protected list
    array unset ::edp_var::protected $varName
}

# Protection trace callbacks
proc ::edp_var::protect_trace {varName name1 name2 op} {
    upvar 1 $name1 var
    set newValue $var
    set var $::edp_var::protected($varName)
    puts "Warning: Variable '$varName' is protected. Attempt to change value from '$::edp_var::protected($varName)' to '$newValue' was blocked."
}

proc ::edp_var::protect_array_trace {fullName elementPath name1 name2 op} {
    upvar 1 $name1 array
    if {$name2 eq $elementPath} {
        set newValue $array($elementPath)
        set array($elementPath) $::edp_var::protected($fullName)
        puts "Warning: Array element '$fullName' is protected. Attempt to change value from '$::edp_var::protected($fullName)' to '$newValue' was blocked."
    }
}

# List protected variables
proc edp_list_protected_vars {} {
    if {[array size ::edp_var::protected] == 0} {
        puts "No protected variables found."
        return {}
    }
    
    puts "\nProtected variables:"
    puts "===================="
    set result {}
    foreach name [lsort [array names ::edp_var::protected]] {
        puts "$name = $::edp_var::protected($name)"
        lappend result $name
    }
    return $result
}

# ==================== Constraint System ====================

# Set constraints on variable
proc edp_constraint_var {varName allowed_list} {
    set values [split $allowed_list]

    # Check if it's an array element
    if {[regexp {^(.+)\((.+)\)$} $varName -> arrayName elementPath]} {
        upvar 1 $arrayName array
        set ::edp_var::allowed_values($varName) $values
        
        # Initialize array element with first allowed value if it doesn't exist
        if {![info exists array($elementPath)]} {
            set array($elementPath) [lindex $values 0]
        } elseif {[lsearch -exact $values $array($elementPath)] == -1} {
            set old_value $array($elementPath)
            error "ERROR: Value '$old_value' of variable '$varName' is not in constraint list. Allowed values are: $values"
        }
        
        # Add write trace
        trace add variable array write [list ::edp_var::constraint_array_trace $varName $elementPath]
    } else {
        upvar 1 $varName var
        set ::edp_var::allowed_values($varName) $values

        # Initialize variable with first allowed value if it doesn't exist
        if {![info exists var]} {
            set var [lindex $values 0]
        } elseif {[lsearch -exact $values $var] == -1} {
            set old_value $var
            error "ERROR: Value '$old_value' of variable '$varName' is not in constraint list. Allowed values are: $values"
        }
        
        # Add write trace
        trace add variable var write [list ::edp_var::constraint_trace $varName]
    }
}

# Remove constraints from variable
proc edp_unconstraint_var {varName} {
    # Check if variable has constraints
    if {![info exists ::edp_var::allowed_values($varName)]} {
        puts "Warning: Variable '$varName' has no constraints."
        return
    }
    
    if {[regexp {^(.+)\((.+)\)$} $varName -> arrayName elementPath]} {
        upvar 1 $arrayName array
        if {[info exists array]} {
            trace remove variable array write [list ::edp_var::constraint_array_trace $varName $elementPath]
        }
    } else {
        upvar 1 $varName var
        if {[info exists var]} {
            trace remove variable var write [list ::edp_var::constraint_trace $varName]
        }
    }
    array unset ::edp_var::allowed_values $varName
    puts "Constraints removed from variable '$varName'"
}

# Constraint trace callback
proc ::edp_var::constraint_trace {varName name1 name2 op} {
    upvar 1 $name1 var
    set newValue $var
    
    if {[lsearch -exact $::edp_var::allowed_values($varName) $newValue] == -1} {
        # Restore previous value (before the invalid assignment)
        # Note: We can't easily get the previous value here, so we'll use error
        error "ERROR: Cannot set '$varName' to '$newValue'. Allowed values are: $::edp_var::allowed_values($varName)"
    }
}

# Array constraint trace callback
proc ::edp_var::constraint_array_trace {fullName elementPath name1 name2 op} {
    upvar 1 $name1 array
    if {$name2 eq $elementPath} {
        set newValue $array($elementPath)
        
        if {[lsearch -exact $::edp_var::allowed_values($fullName) $newValue] == -1} {
            # Restore previous value (before the invalid assignment)
            # Note: We can't easily get the previous value here, so we'll use error
            error "ERROR: Cannot set '$fullName' to '$newValue'. Allowed values are: $::edp_var::allowed_values($fullName)"
        }
    }
}

# List constrained variables
proc edp_list_constrained_vars {} {
    if {[array size ::edp_var::allowed_values] == 0} {
        puts "No constrained variables found."
        return {}
    }
    
    puts "\nConstrained variables:"
    puts "===================="
    set result {}
    foreach name [lsort [array names ::edp_var::allowed_values]] {
        set current_value "undefined"
        
        # Check if it's an array element
        if {[regexp {^(.+)\((.+)\)$} $name -> arrayName elementPath]} {
            upvar 1 $arrayName array
            if {[info exists array] && [info exists array($elementPath)]} {
                set current_value $array($elementPath)
            }
        } else {
            upvar 1 $name var
            if {[info exists var]} {
                set current_value $var
            }
        }
        
        puts "$name:"
        puts "  Current value: $current_value"
        puts "  Allowed values: $::edp_var::allowed_values($name)"
        lappend result $name
    }
    return $result
}

# Get constraints for variable
proc edp_get_constrained_var {varName} {
    if {[info exists ::edp_var::allowed_values($varName)]} {
        set values $::edp_var::allowed_values($varName)
        return "Allowed values for '$varName': $values"
    } else {
        return "No constraints defined for '$varName'"
    }
}

# ==================== Description System ====================

# Set variable description
proc edp_descript_var {varName description} {
    set ::edp_var::descriptions($varName) $description
    puts "Description set for '$varName'"
}

# Get variable description
proc edp_get_descripted_var {varName} {
    if {[info exists ::edp_var::descriptions($varName)]} {
        return $::edp_var::descriptions($varName)
    } else {
        return "No description available for '$varName'"
    }
}

# List all variable descriptions
proc edp_list_descripted_vars {} {
    if {[array size ::edp_var::descriptions] == 0} {
        puts "No variable descriptions found."
        return {}
    }
    
    puts "\nVariable Descriptions:"
    puts "====================="
    set result {}
    foreach name [lsort [array names ::edp_var::descriptions]] {
        puts "$name:"
        puts "  Description: $::edp_var::descriptions($name)"
        # Try to get the current value if it exists
        if {[uplevel 1 info exists $name]} {
            set value [uplevel 1 set $name]
            puts "  Current value: $value"
        } else {
            # For array elements
            if {[regexp {^(.+)\((.+)\)$} $name -> arrayName elementPath]} {
                if {[uplevel 1 array exists $arrayName]} {
                    set arrayVar [uplevel 1 array get $arrayName $elementPath]
                    if {[llength $arrayVar] > 0} {
                        puts "  Current value: [lindex $arrayVar 1]"
                    } else {
                        puts "  Current value: <undefined>"
                    }
                } else {
                    puts "  Current value: <undefined>"
                }
            } else {
                puts "  Current value: <undefined>"
            }
        }
        puts ""
        lappend result $name
    }
    return $result
}

# Remove variable description
proc edp_undescript_var {varName} {
    if {[info exists ::edp_var::descriptions($varName)]} {
        array unset ::edp_var::descriptions $varName
        puts "Description removed for '$varName'"
    } else {
        puts "No description found for '$varName'"
    }
}
