# Sub Step: pnr_innovus::save_design
# Save design

proc ::pnr_innovus::save_design {} {
    # Declare global variables (arrays) to access and modify in namespace
    global project
    
    puts "========== Sub Step: pnr_innovus::save_design =========="
    
    if {[info exists project(work_path)]} {
        set save_file [file join $project(work_path) design.db]
        puts "Saving design to: $save_file"
        puts "INFO: Simulating saveDesign command"
        puts "Design saved successfully."
    } else {
        puts "Warning: project(work_path) not defined, skipping save."
    }
    
    puts "========== End of Sub Step: pnr_innovus::save_design =========="
}

