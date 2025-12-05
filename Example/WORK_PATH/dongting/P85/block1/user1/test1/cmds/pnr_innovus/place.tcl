# All packages from general common package default path
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/common_default.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_dealwith_var.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_flow_writing.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_get_lib.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_get_lsf.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_get_view.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_sub_steps_commands.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_sub_steps_core.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/common/packages/tcl/default/edp_sub_steps_manager.tcl

# All packages from foundry node level default path
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/packages/tcl/default/node_default.tcl

# All packages from project level default path
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/dongting/packages/tcl/default/project_default.tcl
# Auto-generated sub_steps source statements based on C:/Users/anping.chen/Desktop/EDP_AI/edp_center/config/SAMSUNG/S8/common/pnr_innovus/dependency.yaml
# Create namespaces for sub_step procs
namespace eval pnr_innovus {}

# ========== Sub_step: innovus_restore_design.tcl (proc: pnr_innovus::restore_design) ==========
# Sub Step: pnr_innovus::restore_design
# 恢复设计状态
# 文件位置：proc 目录下

proc ::pnr_innovus::restore_design {} {
    # 声明全局变量（框架自动添加）
    global pnr_innovus

    # 声明全局变量（数组），以便在 namespace 中访问和修改
    global edp project
    
    puts "========== Sub Step: pnr_innovus::restore_design =========="
    
    # 示例：访问全局变量 edp(flow_path)
    if {[info exists edp(flow_path)]} {
        puts "EDP flow path: $edp(flow_path)"
    }
    
    # 从配置中获取 restore 文件路径
    if {[info exists project(work_path)]} {
        set restore_file [file join $project(work_path) restore.db]
        if {[file exists $restore_file]} {
            puts "Restoring design from: $restore_file"
            puts "INFO: Simulating restoreDesign command"
            puts "Design restored successfully."
        } else {
            puts "Warning: Restore file not found: $restore_file"
        }
    } else {
        puts "Warning: project(work_path) not defined, skipping restore."
    }
    
    puts "========== End of Sub Step: pnr_innovus::restore_design =========="
}
# ========== End of Sub_step: innovus_restore_design.tcl ==========

# ========== Sub_step: innovus_config_design.tcl (proc: pnr_innovus::config_design) ==========
# Sub Step: pnr_innovus::config_design
# 配置设计参数

proc ::pnr_innovus::config_design {} {
    # 声明全局变量（框架自动添加）
    global edp project

    # 声明全局变量（数组），以便在 namespace 中访问和修改
    global pnr_innovus
    
    puts "========== Sub Step: pnr_innovus::config_design =========="
    
    # 配置全局布局参数
    if {[info exists pnr_innovus(place,global_max_util)]} {
        set util_value $pnr_innovus(place,global_max_util)
        puts "INFO: Simulating setPlaceMode -place_global_max_util $util_value"
        puts "Set global max utilization: $util_value"
    } else {
        set util_value 0.85
        puts "INFO: Simulating setPlaceMode -place_global_max_util $util_value"
        puts "Using default global max utilization: $util_value"
    }
    
    # 其他配置参数...
    puts "Design configuration completed."
    puts "========== End of Sub Step: pnr_innovus::config_design =========="
}
# ========== End of Sub_step: innovus_config_design.tcl ==========

# ========== Sub_step: innovus_add_tie_cell.tcl (proc: pnr_innovus::add_tie_cell) ==========
# Sub Step: pnr_innovus::add_tie_cell
# 添加 Tie Cell

proc ::pnr_innovus::add_tie_cell {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus

    # 声明全局变量（数组），以便在 namespace 中访问和修改
    
    puts "========== Sub Step: pnr_innovus::add_tie_cell =========="
    
    # 添加 Tie Cell 的逻辑
    # 这里可以根据配置参数来添加不同的 Tie Cell
    
    puts "Tie cells added."
    puts "========== End of Sub Step: pnr_innovus::add_tie_cell =========="
}
# ========== End of Sub_step: innovus_add_tie_cell.tcl ==========

# ========== Sub_step: innovus_save_design.tcl (proc: pnr_innovus::save_design) ==========
# Sub Step: pnr_innovus::save_design
# 保存设计

proc ::pnr_innovus::save_design {} {
    # 声明全局变量（框架自动添加）
    global edp pnr_innovus

    # 声明全局变量（数组），以便在 namespace 中访问和修改
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
# ========== End of Sub_step: innovus_save_design.tcl ==========

# ========== Sub_step: innovus_report_design.tcl (proc: pnr_innovus::report_design) ==========
# Sub Step: pnr_innovus::report_design
# 生成设计报告

proc ::pnr_innovus::report_design {} {
    # 声明全局变量（框架自动添加）
    global edp pnr_innovus

    # 声明全局变量（数组），以便在 namespace 中访问和修改
    global project
    
    puts "========== Sub Step: pnr_innovus::report_design =========="
    
    if {[info exists project(work_path)]} {
        set report_dir [file join $project(work_path) rpts]
        file mkdir $report_dir
        
        # 生成各种报告（模拟）
        puts "INFO: Simulating report generation"
        set fp [open [file join $report_dir timing.rpt] w]
        puts $fp "Timing report (simulated)"
        close $fp
        set fp [open [file join $report_dir area.rpt] w]
        puts $fp "Area report (simulated)"
        close $fp
        puts "Design reports generated in: $report_dir (simulated)"
    } else {
        puts "Warning: project(work_path) not defined, skipping report."
    }
    
    puts "========== End of Sub Step: pnr_innovus::report_design =========="
}
# ========== End of Sub_step: innovus_report_design.tcl ==========

# ========== Sub_step: innovus_check_pd.tcl (proc: pnr_innovus::check_pd) ==========
# Sub Step: pnr_innovus::check_pd
# 检查物理设计

proc ::pnr_innovus::check_pd {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus

    # 声明全局变量（数组），以便在 namespace 中访问和修改
    
    puts "========== Sub Step: pnr_innovus::check_pd =========="
    
    # 执行物理设计检查（模拟）
    puts "INFO: Simulating checkDesign -all"
    puts "Physical design check completed."
    
    puts "========== End of Sub Step: pnr_innovus::check_pd =========="
}
# ========== End of Sub_step: innovus_check_pd.tcl ==========

# ========== Sub_step: innovus_save_metrics.tcl (proc: pnr_innovus::save_metrics) ==========
# Sub Step: pnr_innovus::save_metrics
# 保存设计指标

proc ::pnr_innovus::save_metrics {} {
    # 声明全局变量（框架自动添加）
    global edp pnr_innovus

    # 声明全局变量（数组），以便在 namespace 中访问和修改
    global project
    
    puts "========== Sub Step: pnr_innovus::save_metrics =========="
    
    if {[info exists project(work_path)]} {
        set metrics_file [file join $project(work_path) metrics.txt]
        
        # 保存设计指标（模拟）
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
# ========== End of Sub_step: innovus_save_metrics.tcl ==========

source C:/Users/anping.chen/Desktop/EDP_AI/Example/WORK_PATH/dongting/P85/block1/user1/test1/runs/pnr_innovus.place/full.tcl


# ========== Auto-generated sub_steps calls ==========
# Sub_steps are automatically generated from dependency.yaml
pnr_innovus::restore_design
pnr_innovus::config_design
pnr_innovus::add_tie_cell
pnr_innovus::save_design
pnr_innovus::report_design
pnr_innovus::check_pd
pnr_innovus::save_metrics
# ========== End of auto-generated sub_steps calls ==========
