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

source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_restore_design.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_config_design.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_add_tie_cell.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_save_design.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_report_design.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_check_pd.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pnr_innovus/proc/innovus_save_metrics.tcl
source C:/Users/anping.chen/Desktop/EDP_AI/Example/WORK_PATH/dongting/P85/block1/user1/main/runs/pnr_innovus.place/full.tcl


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
