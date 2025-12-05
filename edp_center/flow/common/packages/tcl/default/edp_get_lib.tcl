# Register the package
package provide lib_info 1.0
# This package help to get all lib related info
# Create namespace
namespace eval ::lib_info {
	namespace export get_physical_info get_lib_info get_sub_spef get_sub_netlist
}

#############################################################################################################################
# Description: this proc help to get sub spef information from the released_dir
# Arguments: 
#		release_dir:    - A dir released requried, basically, the all released info shall contained in the dir
#		sta_rc_corner   - Different sta_rc_corner get different spef file
#		sub_blk_list    - If sub_blk_list exist, then it shall find spef foreach sub_blk
#		SP_KEY          - Default latest
# Example: lib_info::get_sub_spef $my_released_dir sigrcmax_125c "blk1 blk2 blk3" SPEF latest
# Return: list of files matchs corner and sub_blk_name
# More: 
#############################################################################################################################

proc ::lib_info::get_sub_spef {release_dir sta_rc_corner sub_blk_list {DIR_KEY "SPEF"} {SP_KEY "latest"}} {

    if {$release_dir eq "" || $sub_blk_list eq ""} {return [list "" ""]}
    set abs_paths ""
    set pair_paths ""
    foreach ele $sub_blk_list {
        set base_spef [file join $release_dir $ele/$SP_KEY/$DIR_KEY/${ele}_${sta_rc_corner}.spef.gz]
        set gpd_spef [file join $release_dir $ele/$SP_KEY/$DIR_KEY/${ele}.gpd]
        
        # if nor base_sepf nor gpd_spef
        if {[catch {set files [glob $base_spef]} err] && [catch {set files [glob $gpd_spef]} err]} {
            puts "No matching gpd or spef for $ele"
            puts "Missing $ele $base_spef"
            puts "Missing $ele $gpd_spef"
            continue
        } else {
            # If exist gpd_spef, use gpd spef
            if {[catch {set files [glob $gpd_spef]} err] != 1} {
                set spef_file $gpd_spef
            } else {set spef_file $base_spef}
            puts "Get SPEF $ele $spef_file"
        }
        set sub_ele [list $ele $spef_file]
        # Add All matched spef files into a list for each sub_blk
        foreach match_file $files {
            lappend abs_paths [file normalize $match_file]
        }

        # Add pair_info into a list: {{blk1 spef1} {blk2 spef2} ..}
        lappend pair_paths $sub_ele
    }
    if {[llength $abs_paths] > 0} {
        return [list $abs_paths $pair_paths]
    }

    puts "No sub spef file got"
    return [list "" ""]
}


#############################################################################################################################
# Description: this proc help to get sub netlist information from the released_dir
# Arguments: 
#		release_dir:    - A dir released requried, basically, the all released info shall contained in the dir
#		sub_blk_list    - If sub_blk_list exist, then it shall find netlist foreach sub_blk
# Example: lib_info::get_sub_spef $my_released_dir "blk1 blk2 blk3"
# Return: list of files matchs and sub_blk_name
# More: 
#############################################################################################################################

proc ::lib_info::get_sub_netlist {release_dir sub_blk_list {DIR_KEY "NETLIST"} {SP_KEY "latest"}} {
    
    if {$release_dir eq "" || $sub_blk_list eq ""} {return ""}
    set abs_paths ""
    set pair_paths ""

    foreach ele $sub_blk_list {
        set required_netlist [file join $release_dir $ele/$SP_KEY/$DIR_KEY/${ele}.v.gz]
        if {[catch {set files [glob $required_netlist]} err]} {
            puts "No matching netlist for $ele $required_netlist"
            continue
        } else {
            puts "Get $DIR_KEY $ele $required_netlist"
        }
        foreach match_file $files {
            lappend abs_paths [file normalize $match_file]
        }
        # Add pair_info into a list: {{blk1 netlist1} {blk2 netlist2} ..}
        set sub_ele [list $ele $required_netlist]
        lappend pair_paths $sub_ele
    }

    if {[llength $abs_paths] > 0} {
        return [list $abs_paths $pair_paths]
    }

    puts "No sub netlist file got"
    return [list "" ""]
}


#############################################################################################################################
# Description: this proc help to get PHYSICAL LIB information from the previews setup
# Arguments: 
#		sub_key:    -lef gds oasis ovm cdl
#
# Example: lib_info::get_physical_info lef
# Return: list of values matching the sub_key
# More: Count STD/MEM/IP included
#############################################################################################################################

proc ::lib_info::get_physical_info {sub_key} {
    set array_key [list LIBRARY MEM_LIBRARY IP_LIBRARY]
    set result_list [list]
    set all_count 0
    puts "[string toupper $sub_key] INFO:"

    foreach lib_ele $array_key {
        # Use upvar to access the array by name
        upvar #0 $lib_ele lib_array
        if {![array exists lib_array]} {
            continue
        }
        # Iterate through the array and match keys with sub_key
        set count 0
        foreach lib_sub_key [array names lib_array] {
            if {[regexp $sub_key $lib_sub_key]} {
                set result_list [concat $result_list $lib_array($lib_sub_key)]
                set count [expr $count + 1]
            }
        }
        puts "  $sub_key $lib_ele count: $count"
        set all_count [expr $all_count + $count] 
    }
    puts "  $sub_key all count: $all_count"
    puts "==================================="
    return $result_list
}


#############################################################################################################################
# Description: this proc help to get TIMING LIB|DB information from the previews setup
# Arguments: 
#		sub_key:    - lib db
#		view_list:  - a view list for setup_view hold_view combine
#		extral_lib  - a extral key_word or list here, Samsung's cdk12m3mx2 is a std cell, but rc_corner related
#		              have to extal lib/db get to filter not required rc_corner lib
#
# Example: lib_info::get_lib_info lib func_sspg_0p6750v_125c_Cmax
# Example: lib_info::get_lib_info lib $scenrio_list 
# Return: list of values matching the sub_key
# More: Count STD/MEM/IP included
#############################################################################################################################
proc ::lib_info::check_match_or {input_str input_list} {
    # This proc works for if either one ele can match in input_str, return 1
    foreach ele $input_list {
        if {[regexp $ele $input_str]} {return 1}
    }
    return 0
}

proc ::lib_info::check_match_and {input_str input_list} {
    # This proc works for if all ele can match in input_str, return 1
    foreach ele $input_list {
        if {[regexp $ele $input_str] < 0} {return 0} else {return 1}
    }
    
}

proc ::lib_info::get_lib_info {sub_key view_list {extral_lib "cdk12m3mx2"}} {
    
    # In samsung, the 1.8v GPIO can support 1.2v or 1.8v
    # So in this case, this GPIO has 2 libs, but PT will default use lower voltage to link
    # We have to filter 1p08v db, extral_baned_list is required
    # lib_dir/ccs_lvf/ln04lpp_gpio_lib_1p8v_all_sigcmax_sspg0p675v1p62vm40c.db
    # lib_dir/ccs_lvf/ln04lpp_gpio_lib_1p8v_all_sigcmax_sspg0p675v1p08vm40c.db

    # This part add for GPIO 20250225, bias 10%, in Samsung, it has 2 version GPIO, for 1p8v or 1p2v
    set voltage_arr(0p75v)  "1p8v 1p2v 0p75v"
    set voltage_arr(0p675v) "1p62v 1p08v 0p675v"
    set voltage_arr(0p825v) "1p98v 1p32v 0p825v"
    set voltage_arr(0p72v)  "0p72v"
    set voltage_arr(0p88v)  "0p88v"
    set voltage_arr(0p8v)  "0p8v"
    # STAR_1 project has the request that use 1p62 only
    set extral_baned_list [list "gpio.*1p8v.*1p08v"]
    ###############################################

    puts "[string toupper $sub_key] INFO:"
    set array_key [list LIBRARY MEM_LIBRARY IP_LIBRARY]
    set lib_db ""
    set ip_db ""
    set mem_db ""
    set std_db ""
    foreach view $view_list {
        set combine_voltage [list]
        lassign [split $view "_"] sdc_mode process_corner voltage temperature rc_corner
        set max_or_min [string tolower [string range $rc_corner end-2 end]]
        set sig_rc_corner sig[string tolower $rc_corner]
        set voltage [regsub {0+(?=v)} $voltage ""]
        set pvt $process_corner$voltage$temperature
        set voltage_list $voltage_arr($voltage)
        # GPIO can have multi voltage info
        foreach ele $voltage_list {
            lappend pvvt_list $process_corner$voltage$ele$temperature 
        }
        # This list contains pvt pvv1t pvv2t ...
        set pvt_match_list [linsert $pvvt_list 0 $pvt]

        foreach lib_ele $array_key {
            # Use upvar to access the array by name
            upvar #0 $lib_ele lib_array
            if {![array exists lib_array]} {
                continue
            }
            # Iterate through the array and match keys with sub_key
            foreach lib_sub_key [array names lib_array] {
                if {$lib_ele eq "MEM_LIBRARY"} {
                    # MEM_LIBRARY Match sub_key(lib/db) and pvt/pvvt and RC info
                    # need pvt sub_key sig_rc_corner match
                    set pvt_match_or [::lib_info::check_match_or $lib_sub_key $pvt_match_list] 
                    if {[regexp $sub_key $lib_sub_key] && $pvt_match_or && [regexp $sig_rc_corner $lib_sub_key] } {
                        set lib_db [concat $lib_db $lib_array($lib_sub_key)]
                        set mem_db [concat $mem_db $lib_array($lib_sub_key)]
                    }
                } elseif {$lib_ele eq "IP_LIBRARY"} {
                    # IP_LIBRARY has specific logic
                    # need pvt sub_key sig_rc_corner func match
                    set final_pvvt_list_ip_mode [list]
                    foreach ele $pvt_match_list {lappend final_pvvt_list_ip_mode "$ele,$sub_key\$"}
                    if {[::lib_info::check_match_or $lib_sub_key $final_pvvt_list_ip_mode]} {
                        # rc(rcall|sigrcmax) shall map and func(all|FUNC) shall map
                        set match_rc_corner [expr {[regexp ",rcall" $lib_sub_key] || [regexp $sig_rc_corner $lib_sub_key]}]
                        set match_sdc_mode [expr {[regexp $sdc_mode $lib_sub_key] || [regexp ",all" $lib_sub_key]}]
                        if {$match_rc_corner && $match_sdc_mode} {
                            # For gpio extral requirement, gpio shall not contain keys in $extral_baned_list
                            if {[::lib_info::check_match_or $lib_sub_key $extral_baned_list] == 0} {
                                set lib_db [concat $lib_db $lib_array($lib_sub_key)]
                                set ip_db [concat $ip_db $lib_array($lib_sub_key)]
                            }
                        }
                    }
                } elseif {$lib_ele eq "LIBRARY"} {
                    # LIBRARY here is std cell
                    #STD cdk12m3mx2 is special sigcmax/sigcim
                    #STD NORMAL just need pvt match and sub_key match
                    set pvt_match_or [::lib_info::check_match_or $lib_sub_key $pvt_match_list] 
                    if {[regexp $sub_key $lib_sub_key] && $pvt_match_or} {
                        set match_found 0
                        foreach pattern $extral_lib {
                            if {[regexp $pattern $lib_sub_key]} {
                                set match_found 1
                                break 
                            }
                        }
                        if {$match_found == 1} {
                            #Case1: cdk version for Samsung K's clock buffer, if exist, the sig_rc_corner must match
                            if {[regexp $sig_rc_corner $lib_sub_key]} {
                                set lib_db [concat $lib_db $lib_array($lib_sub_key)]
                                set std_db [concat $std_db $lib_array($lib_sub_key)]
                            }
                        } else {
                            #Case2: if normal std cell, auto in
                            set lib_db [concat $lib_db $lib_array($lib_sub_key)]
                            set std_db [concat $std_db $lib_array($lib_sub_key)]
                        }
                    }
                }
            }
        }
    }
    # Decreasing Mode
    set lib_db [lsort -unique -decreasing $lib_db]
    puts "  $sub_key std count: [llength $std_db]"
    puts "  $sub_key mem count: [llength $mem_db]"
    puts "  $sub_key ip count: [llength $ip_db]"
    puts "  $sub_key all count: [llength $lib_db]"
    puts "==================================="
    return $lib_db
}

