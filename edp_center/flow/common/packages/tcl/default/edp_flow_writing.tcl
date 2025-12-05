# Register the package
package provide file_temp 1.0
# This package help to gen tempfile, do file key world replacement
# Create namespace
namespace eval ::file_temp {
	namespace export write_file var_check find_file get_template_file get_file_value get_var_value
}


#############################################################################################################################
# Description: this proc help to return default value if the var not exist
# Arguments: 
#		args		    - The required var name, the last one will be default value and recognized as string
# Example: file_temp::get_var_value var1 var2 1000
#############################################################################################################################
proc ::file_temp::get_var_value {args} {
    # If args length is 1, default_value is "", otherwise, the last one as the default value
    if {[llength $args] > 1} {
        set default_value [lindex $args end]
        set args [lrange $args 0 end-1]
    } else {
        set default_value ""
    }
    # Check each var
    foreach ele $args {
        upvar $ele local_var
        if {[info exists local_var]} {
            return $local_var
        }
    }
    # if all args without definition, use default_value
    if {![info exists local_var]} {
        puts "$args missing, use flow default value $default_value\n"
        return $default_value
    } 
}

#############################################################################################################################
# Description: this proc help to return all env_info and transform it into a std formate
# Arguments: 
#		args		    - The required sub_layers if exist
# Example: file_temp::get_env_info pv_calibre dummy
# Return: all info under as a list
#   pv_calibre(dummy,setenv,key) value      -> setenv key value
#   pv_calibre(dummy,unsetenv,key) value    -> unsetenv key value
#############################################################################################################################

proc ::file_temp::get_env_info {flow_name target_name args} {
    global $flow_name project
    set args_info [join $args ","]
    set setenv_key_prefix $target_name,setenv,
    set unsetenv_key_prefix $target_name,unsetenv,
    if {$args ne ""} {
        set setenv_key_prefix $target_name,$args_info,setenv,
        set unsetenv_key_prefix $target_name,$args_info,unsetenv,
    } 
    set setenv_key_list [array names $flow_name *$setenv_key_prefix*]
    set unsetenv_key_list [array names $flow_name *$unsetenv_key_prefix*]

    # Restore required info
    set setenv_info "# setenv info set by ${flow_name}(${setenv_key_prefix}ENV_KEYS)\n"
    set unsetenv_info "# unsetenv info set by ${flow_name}(${unsetenv_key_prefix}ENV_KEYS)\n"
    foreach ele $setenv_key_list {
        set env_key [lindex [split $ele ","] end]
        append setenv_info "setenv $env_key \"[set ${flow_name}($ele)]\"\n"
    }
    foreach ele $unsetenv_key_list {
        set env_key [lindex [split $ele ","] end]
        append unsetenv_info "unsetenv $env_key \"[set ${flow_name}($ele)]\"\n"
    }
    return [list $setenv_info $unsetenv_info]
}

#############################################################################################################################
# Description: this proc help to return default value if the var not exist
# Arguments: 
#		var_name		-The required var, value will be recognize a file path
#		args            -Other file paths
# Example: file_temp::get_file_value var_name args
# This function is strict and a file value must exist
#############################################################################################################################

proc ::file_temp::get_file_value {var_name args} {
    upvar $var_name local_var
    if {[info exists local_var] && [file exists $local_var]} {
        return $local_var
    } else {
        foreach ele $args {
            if {[file exists $ele]} {
                return $ele
            }
        }
        set args_info [join $args "\n"]
        error "$var_name file not exist, please check\n OR one of below shall be exist:\n $args_info"
    }
}


#############################################################################################################################
# Description: this proc help to check if all required var exist or not
# Arguments: 
#		var_list		-all vars need to be check
# Example: file_temp::var_check [list var1 var2 var3 ..]
# If error out, the missing_vars will show up in the error info
#############################################################################################################################

proc ::file_temp::var_check {var_list} {
    set existing_vars {}  ;# Store existing variable names
    set missing_vars {}   ;# Store missing variable names

    foreach var $var_list {
        # Use upvar to get reference to upper level variable
        upvar 1 $var local_var
        # Check if variable exists
        if {[info exists local_var]} {
            lappend existing_vars $var  ;# Add existing variable to list
        } else {
            lappend missing_vars $var   ;# Add missing variable to list
        }
    }

    # Return lists of existing and missing variables
    if {$missing_vars ne ""} {
        error "Missing required var, please setup vars: $missing_vars"
    }
    #return [list $existing_vars $missing_vars]
}


#############################################################################################################################
# Description: this proc help to check if all required var exist or not
# Arguments: 
#		dir		    - The target_file try to find in the dir
#		target_file - The required file name
# Example: file_temp::find_file {/path/to/template/file/dir my_temp.csh.temp}
# Return: /path/to/template/file/dir/my_temp.csh.temp
#############################################################################################################################

# Support proc help for file_file abs path 
proc ::file_temp::find_file {dir target_file} {
    foreach item [glob -nocomplain -directory $dir *] {
        if {[file tail $item] eq $target_file} {
            return $item
        }
        if {[file isdirectory $item]} {
            set result [find_file $item $target_file]
            if {$result ne ""} {
                return $result
            }
        }
    }
    return ""
}


#############################################################################################################################
# Description: this proc help to check if all required var exist or not
# Arguments: 
#		node_dir	    - The node_dir works for get template_file
#		project_name    - The template file under specific project
#		flow_name       - The template file under specific flow
#		temp_file_name  - required temp_file_name
# Example: file_temp::get_template_file {/path/to/template/file/node_dir star1_b0 pv_calibre dummy.csh.temp}
# possible_file1: /path/to/template/file/node_dir/common/templates/pv_calibre/template/path/to/dummy.csh.temp
# possible_file2: /path/to/template/file/node_dir/star1_b0/templateds/pv_calibre/template/path/to/dummy.csh.temp
# if possible_file2 exist: return possible_file2
# if not, return possible_file1
# if both not exist, error out
#############################################################################################################################

proc ::file_temp::get_template_file {node_dir project_name flow_name temp_file_name} {
    set dir_common [file join $node_dir common/templates/$flow_name/template/]
    set dir_project [file join $node_dir $project_name/templates/$flow_name/template/]
    # Get common
    set template_file_abs_default [::file_temp::find_file $dir_common $temp_file_name]
    set template_file_abs_project [::file_temp::find_file $dir_project $temp_file_name]
    if {$template_file_abs_project ne ""} {
        set template_file_abs_default $template_file_abs_project
    }

    if {$template_file_abs_default eq ""} {
        set error_message "Missing: $temp_file_name in $dir_common or $dir_project"
        error: $error_message
    }
    return $template_file_abs_default
}

#############################################################################################################################
# Description: this proc help to translate a template into a outputfile with different keyword for the further csh usage
# Arguments: 
#		temp_file		-input temp_file to be processed
#		out_file		-output file to be written after processing temp_file
#		mapdict			-keyword mapping dictionary for substituting keywords
#		-opendelimiter	-open delimiter string, default is "<<"
#		-closedelimiter	-close delimiter string, default is ">>"
#		-delundef		-if delete the undefined keyword (1) or preserve (0)
#
# Example: file_temp::write_file temp_file output.text $mapdict -delundef 1
#############################################################################################################################

proc ::file_temp::write_file {temp_file out_file mapdict args} {
	array set optargs [list -opendelimiter "<<:" -closedelimiter ":>>" -permissions "rw-r--r--" -delundef 0]        
	array set optargs $args
	set infile [open $temp_file "r"]
	set outfile [open $out_file "w"]
	while {[gets $infile line] >= 0} {
		if {[regexp "${optargs(-opendelimiter)}\\S+${optargs(-closedelimiter)}" $line]} {
			set rol $line
			set printline ""        
			# loop over this line untill process all keyword 
			while {$rol ne ""} {
				if {[regexp "^(.*?)${optargs(-opendelimiter)}(\\S+?)${optargs(-closedelimiter)}(.*)$" $rol -> sol match_var rol]} {
					append printline $sol
                    #update function here in 20250103
                    if {[string first "|" $match_var] != -1} {
                        set result [split $match_var "|"]
                        set match_var [lindex $result 0]
                        #update function here in 20250106, support $var_name to recognize var_name, not just var_name
                        set default_value [lindex $result 1]
                    }
                    # if get key, then replace, if not, then try default key, if no default key, then remain the basic
                    # it can be:
                    #1: pre_info+ <<:required_key|default_value:>> +post_info ->pre_info+ required_value +post_info
                    #2: pre_info+ <<:required_key|default_value:>> +post_info ->pre_info+ default_value +post_info (required_key not exist)
                    #3: pre_info+ <<:required_key:>> +post_info         ->pre_info+ required_value +post_info
                    #4: pre_info+ <<:required_key:>> +post_info         ->pre_info+ <<:required_key:>> +post_info (required_key not exist)
					if {[dict exists $mapdict $match_var]} {
						append printline [dict get $mapdict $match_var]        
					} elseif {[info exists default_value]} {
						append printline "$default_value"
                    } elseif {$optargs(-delundef) == 0} {
						# preserve undefined keyword if required
						append printline "${optargs(-opendelimiter)}${match_var}${optargs(-closedelimiter)}"
					}
                    if {[info exists default_value]} {
                        unset default_value
                    }
				} else {
					append printline $rol
					set rol ""
				}
			}
			# replace finished        
			puts $outfile $printline
		} else {
			# copy the line without keyword
			puts $outfile $line
		}
	}
	close $infile
	close $outfile
	file attributes $out_file -permission $optargs(-permissions)
}

