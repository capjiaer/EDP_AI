对于一个具体的process，这里是以SAMSUNG/S8 为例
    common意味着golden flow，未来所有的基础flow从
    FOUNDRY/NODE/common 里面取用，对应
    SAMSUNG/S8/common
对于每个project, 比如dongting
可以overwrite掉common里面的同位置文件，起到update和hack的作用

1: 所有的flow 放到 cmds 下面
    steps: 里面是各个具体flow的主要内容（推荐：使用 steps/ 目录）
    helpers: 里面是各个flow的辅助内容（推荐：使用 helpers/ 目录）
    sub_steps: 里面是各个flow的sub_step proc定义（推荐：使用 sub_steps/ 目录）
    DRC为例 cmds/pv_calibre/steps/calibre.drc.tcl是里面的主脚本（推荐：使用 steps/ 目录）
    cmds/pv_calibre/helpers/drc_switch.tcl 是辅助脚本（推荐：使用 helpers/ 目录）
    平台提供了 #import source 方式调用辅助脚本
    注意：请使用 steps/ 和 helpers/ 目录（旧结构 scripts/ 和 util/ 已不再支持）
    
    #import source <your_script_name> 会变成:
    source real/path/to/your_script_name.tcl

举例说明：
假设你有一个 calibre_drc.tcl，内容为
puts 1
#import source drc_switch.tcl
puts 2

最终应用内容转化为-->
puts 1
source real/path/to/drc_switch.tcl
puts 2

总结：
一个flow的完整形态等于
1：cmds/pv_calibre/steps/your_flow_script.tcl（推荐：使用 steps/ 目录）
2：所有在 your_flow_script.tcl 里面引用的 util
3：flow/common/packages/tcl/defaults scripts 的source
4：flow/common/packages/tcl/<flow_name> 下面的scripts 的 source


最终的flow形态：
source realpath/to/flow/common/packages/tcl/defaults/xxx.tcl
source realpath/to/flow/common/packages/tcl/<flow_name>/xxx.tcl

source realpath/to/<foundry>/<node>/common/packages/tcl/defaults/xxx.tcl
source realpath/to/<foundry>/<node>/common/packages/tcl/<flow_name>/xxx.tcl

source realpath/to/<foundry>/<node>/<project_name>/packages/tcl/default/xxx.tcl
source realpath/to/<foundry>/<node>/<project_name>/packages/tcl/<flow_name>/xxx.tcl

unpacked scripts from realpath/to/initialize/<foundry>/<node>/common/cmds/<flow_name>/steps/flow_info.tcl（推荐：使用 steps/ 目录）
    
注意：已移除 #import util 机制，统一使用 #import source
    
平台会按照顺序source 全部的需要的组件，然后展开主flow文件，放到user的cmds 目录下，然后通过平台以合适方式执行该文件
本质上，这个packages 系统就是一个插件系统
