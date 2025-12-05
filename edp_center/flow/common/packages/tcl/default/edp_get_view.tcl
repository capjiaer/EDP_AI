# Register the package
package provide view_info 1.0

# This package help to dealwith view related proc, get view info or else

# Create namespace
namespace eval ::view_info {
	namespace export get_view_info
}

#############################################################################################################################
# Description: this proc help to get all required sceniro view information and return all info
# Arguments:    view        -Your sceniro view for STA run
# Example1: view_info::get_view_info FLATFUNC_sigrcmax_ssgp0p765v125c_setup
# Example2: view_info::get_view_info func_sspg_0p6750v_m40c_Cmax
# Return:   [list   FLATFUNC  sigrcmax_125c  ssgp0p765v125c sigrcmax_ssgp0p765c_setup   125c            SETUP       sigrcmax    max         -early]
#return     [list   $sdc_mode $sta_rc_corner $pvt_info      $delay_corner               $temperature    $time_ana   $rc_corner  $delay_type $derate_type]
#############################################################################################################################


proc ::view_info::get_view_info_old {view} { 
    set count [regexp -all "_" $view]
    if {$count == 3} {
        #                         FLATFUNC sigrcmax  ssgp0p765v125c setup
        lassign [split $view "_"] sdc_mode rc_corner pvt_info       time_ana
        set time_ana [string toupper $time_ana]
        if {$time_ana eq "SETUP"} {
            set delay_type "max" 
            set derate_type "-early"
        } elseif {$time_ana eq "HOLD"} {
            set delay_type "min"
            set derate_type "-late"
        }
        # Here the formate is {(process_corner)(voltage)(temperature)}
        set format_info {^(.*)(\d+p\d+v)(.*)$}

        # Check if user input view legal or not        sspg           op765v  125c
        if {[regexp $format_info $pvt_info matched_all process_corner voltage temperature]} {
        } else {
            error "$view is illegal, please check your input"
        }

        # Add rc_corner into rc_corner_list
        #                 sigrcmax_125c
        set sta_rc_corner ${rc_corner}_${temperature}
        #                 sigrcmax_ssgp0p765c
        set delay_corner  ${rc_corner}_$pvt_info

        # EG:  [list FLATFUNC  sigrcmax_125c  ssgp0p765v125c sigrcmax_ssgp0p765c_setup  125c         SETUP     sigrcmax   max         -early]
        return [list $sdc_mode $sta_rc_corner $pvt_info      $delay_corner              $temperature $time_ana $rc_corner $delay_type $derate_type]
    } elseif {$count == 4} {
        # Example2: view_info::get_view_info func_sspg_0p6750v_m40c_Cmax
        #                           func    sspg          0p6750v m40c          Cmax
        lassign [split $view "_"] sdc_mode process_corner voltage temperature rc_corner
        # pvt_info
        set pvt_info $process_corner$voltage$temperature

        # func -> FUNC
        set sdc_mode [string toupper $sdc_mode]
        # voltage 0p6750v -> 0p675v
        regsub {(\d+)0v} $voltage {\1v} voltage
        # rc_corner is Cmax -> sigcmax
        set rc_corner "sig[string tolower $rc_corner]"
        # sigcmax_m40c
        set sta_rc_corner ${rc_corner}_${temperature}
        set delay_corner  ${rc_corner}_$pvt_info

        return [list $sdc_mode $sta_rc_corner $pvt_info $delay_corner $temperature "NA" $rc_corner "NA" "NA"]
        #return [list $sdc_mode $sta_rc_corner $pvt_info $delay_corner $temperature $time_ana $rc_corner $delay_type $derate_type]
        
    }
}

#############################################################################################################################
# Description: this proc help to get all required sceniro view information and return all info
# Arguments:    view        -Your sceniro view for STA run
#               time_ana    -setup | hold
# Example: view_info::get_view_info setup func_sspg_0p6750v_m40c_Cmax
# Return:   [list   FLATFUNC  sigrcmax_125c  ssgp0p765v125c sigrcmax_ssgp0p765c_setup   125c            SETUP       sigrcmax    max         -early]
# Example: view_info::get_view_info setup func_tt_0p6750v_m40c_typical
# Return:   [list   FLATFUNC  typical_125c  tt0p765v125c typical0p765c_setup   125c            SETUP       sigrcmax    max         -early]
#return     [list   $sdc_mode $sta_rc_corner $pvt_info      $delay_corner               $temperature    $time_ana   $rc_corner  $delay_type $derate_type]
#############################################################################################################################
# NEW version of get_view_info proc
proc ::view_info::get_view_info {time_ana view} { 
    set count [regexp -all "_" $view]
    if {$count < 4} {
        error "Incorrect view infor for $view, at least 5 parts separated by '_':\n\
        func_processcorner_voltage_temperature_rccorner\n\
        func_processcorner_voltage1_voltage2_temperature_rccorner"
    }
    set time_ana [string toupper $time_ana]

    # SETUP AND HOLD
    if {$time_ana eq "SETUP"} {
        set delay_type "max" 
        set derate_type "-early"
    } elseif {$time_ana eq "HOLD"} {
        set delay_type "min"
        set derate_type "-late"
    }

    #                         func     sspg           0p6750v m40c        Cmax
    lassign [split $view "_"] sdc_mode process_corner voltage temperature rc_corner
    set sdc_mode [string toupper $sdc_mode];            #func -> FUNC
    set rc_corner "sig[string tolower $rc_corner]";     #Cmax -> sigcmax
    set voltage [string tolower $voltage];              #0P6750v -> 0p6750v
    regsub {(\d+)0v} $voltage {\1v} voltage;            #0p6750v -> 0p675v

    # pvt_info
    set pvt_info $process_corner$voltage$temperature

    # sigcmax_m40c
    set sta_rc_corner ${rc_corner}_${temperature}
    set delay_corner  ${rc_corner}_$pvt_info

    return [list $sdc_mode $sta_rc_corner $pvt_info $delay_corner $temperature $time_ana $rc_corner $delay_type $derate_type]

}


proc ::view_info::get_sta_rc_corner {view_list} { 
    set sta_rc_corner_list ""
    foreach view $view_list {
        # Add view check
        set count [regexp -all "_" $view]
        if {$count < 4} {
            error "Incorrect view infor for $view, at least 5 parts separated by '_':\n\
            func_processcorner_voltage_temperature_rccorner\n\
            func_processcorner_voltage1_voltage2_temperature_rccorner"
        }
        lassign [split $view "_"] sdc_mode process_corner voltage temperature rc_corner
        set rc_corner [string tolower $rc_corner]
        # Add case in 20250319 typical0p765c_setup, in this case, sig string is not required
        if {$rc_corner ne "typical"} {
            set rc_corner "sig$rc_corner"
        }
        set sta_rc_corner ${rc_corner}_${temperature}
        # Add new sta_rc_corner
        if {[lsearch -exact $sta_rc_corner_list $sta_rc_corner] == -1} {
            lappend sta_rc_corner_list $sta_rc_corner
        }
    }
    if {$sta_rc_corner_list ne ""} {
        return $sta_rc_corner_list
    } else {
        error "Get empty sta_rc_corner list base on input view_list, please check your input view list and try again"
    }
}

proc ::view_info::get_view_info_n12 {time_ana view} { 
    set count [regexp -all "_" $view]
    if {$count < 4} {
        error "Incorrect view infor for $view, at least 5 parts separated by '_':\n\
        func_processcorner_voltage_temperature_rccorner\n\
        func_processcorner_voltage1_voltage2_temperature_rccorner"
    }
    set time_ana [string toupper $time_ana]

    # SETUP AND HOLD
    if {$time_ana eq "SETUP"} {
        set delay_type "max" 
        set derate_type "-early"
    } elseif {$time_ana eq "HOLD"} {
        set delay_type "min"
        set derate_type "-late"
    }

    #                         func     sspg           0p6750v m40c        Cmax
    lassign [split $view "_"] sdc_mode process_corner voltage temperature rc_corner
    set sdc_mode [string toupper $sdc_mode];            #func -> FUNC
    set rc_corner "$rc_corner";     #Cmax -> sigcmax
    set voltage [string tolower $voltage];              #0P6750v -> 0p6750v
    regsub {(\d+)0v} $voltage {\1v} voltage;            #0p6750v -> 0p675v

    # pvt_info
    set pvt_info $process_corner$voltage$temperature

    # sigcmax_m40c
    set sta_rc_corner ${rc_corner}_${temperature}
    set delay_corner  ${rc_corner}_$pvt_info

    return [list $sdc_mode $sta_rc_corner $pvt_info $delay_corner $temperature $time_ana $rc_corner $delay_type $derate_type]

}


proc ::view_info::get_sta_rc_corner_n12 {view_list} { 
    set sta_rc_corner_list ""
    foreach view $view_list {
        # Add view check
        set count [regexp -all "_" $view]
        if {$count < 4} {
            error "Incorrect view infor for $view, at least 5 parts separated by '_':\n\
            func_processcorner_voltage_temperature_rccorner\n\
            func_processcorner_voltage1_voltage2_temperature_rccorner"
        }
        lassign [split $view "_"] sdc_mode process_corner voltage temperature rc_corner
        set rc_corner "$rc_corner"
        set sta_rc_corner ${rc_corner}_${temperature}
        # Add new sta_rc_corner
        if {[lsearch -exact $sta_rc_corner_list $sta_rc_corner] == -1} {
            lappend sta_rc_corner_list $sta_rc_corner
        }
    }
    if {$sta_rc_corner_list ne ""} {
        return $sta_rc_corner_list
    } else {
        error "Get empty sta_rc_corner list base on input view_list, please check your input view list and try again"
    }
}

