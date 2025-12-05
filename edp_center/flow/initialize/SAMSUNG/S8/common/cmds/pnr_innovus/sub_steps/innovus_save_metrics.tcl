# Sub Step: pnr_innovus::save_metrics
# Save design metrics

proc ::pnr_innovus::save_metrics {} {
    # Declare global variables (arrays) to access and modify in namespace
    global project
    
    puts "========== Sub Step: pnr_innovus::save_metrics =========="
    
    if {[info exists project(work_path)]} {
        set metrics_file [file join $project(work_path) metrics.txt]
        
        # Save design metrics (simulated)
        set fp [open $metrics_file w]
        puts $fp "Design Metrics:"
        puts $fp "Area: N/A (simulated)"
        puts $fp "Timing: N/A (simulated)"
        close $fp
        
        puts "Metrics saved to: $metrics_file"
    } else {
        puts "Warning: project(work_path) not defined, skipping metrics save."
    }
    
    puts "========== End of Sub Step: pnr_innovus::save_metrics =========="
}

