#!/bin/tcsh
# 
# EDP 环境设置脚本（Csh/Tcsh 版本）
# 功能：
#   1. 设置 PATH
#   2. 设置环境变量
#
# 使用方法：
#   source /path/to/EDP_AI/edp_center/bin/edp_env.csh
#   或者在 ~/.cshrc 中添加：
#   source /path/to/EDP_AI/edp_center/bin/edp_env.csh

# 获取脚本所在目录
# 在 csh/tcsh 中，source 时 $0 是 shell 名称，不是脚本路径
# 最简单可靠的方式：假设用户在 edp_center/bin 目录下 source，或者从当前目录向上查找
set edp_bin_dir = ""
set edp_center_dir = ""

# 方法 1: 如果当前目录就是 edp_center/bin（最常见的情况）
if ( -f "./edp_env.csh" ) then
    set edp_bin_dir = `pwd`
    set edp_center_dir = `cd .. && pwd`
else
    # 方法 2: 从当前目录向上查找 edp_center/bin
    set current_dir = `pwd`
    set found = "0"
    set depth = 0
    while ( $depth < 10 && "$current_dir" != "/" )
        if ( -f "$current_dir/edp_center/bin/edp_env.csh" ) then
            set edp_bin_dir = "$current_dir/edp_center/bin"
            set edp_center_dir = "$current_dir/edp_center"
            set found = "1"
            break
        endif
        set current_dir = `dirname "$current_dir"`
        @ depth++
    end
    
    # 方法 3: 如果还是找不到，尝试从环境变量获取
    if ( "$found" != "1" ) then
        if ( $?EDP_BIN_PATH ) then
            set edp_bin_dir = "$EDP_BIN_PATH"
            set edp_center_dir = `cd "$edp_bin_dir/.." && pwd`
        else if ( $?EDP_CENTER_PATH ) then
            set edp_center_dir = "$EDP_CENTER_PATH"
            set edp_bin_dir = "$edp_center_dir/bin"
        else
            echo "⚠️  无法确定 edp_center/bin 目录" >& /dev/stderr
            echo "   请确保在 edp_center/bin 目录下 source，或使用完整路径：" >& /dev/stderr
            echo "   source /path/to/EDP_AI/edp_center/bin/edp_env.csh" >& /dev/stderr
            # 使用当前目录作为默认值（可能不正确，但至少不会报错）
            set edp_bin_dir = `pwd`
            set edp_center_dir = `cd .. && pwd`
        endif
    endif
endif

# 1. 设置 PATH（如果还没有添加）
if ( `echo $path | grep -c "$edp_bin_dir"` == 0 ) then
    set path = ($edp_bin_dir $path)
endif

# 1.1 确保关键命令有执行权限（如果文件存在但不可执行）
if ( -f "$edp_bin_dir/edp_init" && ! -x "$edp_bin_dir/edp_init" ) then
    chmod +x "$edp_bin_dir/edp_init" >& /dev/null
endif
if ( -f "$edp_bin_dir/edp" && ! -x "$edp_bin_dir/edp" ) then
    chmod +x "$edp_bin_dir/edp" >& /dev/null
endif
if ( -f "$edp_bin_dir/edp_info" && ! -x "$edp_bin_dir/edp_info" ) then
    chmod +x "$edp_bin_dir/edp_info" >& /dev/null
endif

# 1.2 修复可能的文件格式问题（Windows CRLF -> Unix LF）
# 如果文件存在但无法执行，可能是换行符问题
if ( -f "$edp_bin_dir/edp_init" ) then
    # 检查并修复 CRLF 换行符（如果存在）
    # 使用 sed 或 tr 来移除 \r 字符
    if ( `file "$edp_bin_dir/edp_init" | grep -c "CRLF"` > 0 ) then
        # 检测到 CRLF，转换为 LF
        sed -i 's/\r$//' "$edp_bin_dir/edp_init" >& /dev/null
    endif
endif

# 2. 设置 PYTHONPATH（如果需要）
# 先检查 PYTHONPATH 是否存在，避免 "Undefined variable" 错误
if ( $?PYTHONPATH ) then
    # PYTHONPATH 已存在，检查是否包含 edp_center_dir
    if ( `echo "$PYTHONPATH" | grep -c "$edp_center_dir"` == 0 ) then
        setenv PYTHONPATH "$edp_center_dir:$PYTHONPATH"
    endif
else
    # PYTHONPATH 不存在，直接设置
    setenv PYTHONPATH "$edp_center_dir"
endif

# 3. 设置环境变量
setenv EDP_CENTER_PATH "$edp_center_dir"
setenv EDP_BIN_PATH "$edp_bin_dir"

# 4. 刷新 csh/tcsh 的命令 hash 表（重要！）
# 在 csh/tcsh 中，修改 PATH 后需要 rehash 才能找到新命令
rehash

# 5. 调试信息（可选，可以通过环境变量控制）
# 设置 EDP_DEBUG=1 来显示调试信息
# 注意：在 csh/tcsh 中，必须先检查变量是否存在（$?EDP_DEBUG），再访问其值
if ( $?EDP_DEBUG ) then
    if ( "$EDP_DEBUG" == "1" ) then
        echo "[DEBUG] EDP_BIN_PATH: $edp_bin_dir" >& /dev/stderr
        echo "[DEBUG] PATH contains edp_center/bin: `echo $path | grep -c "$edp_bin_dir"`" >& /dev/stderr
        echo "[DEBUG] Checking files:" >& /dev/stderr
        if ( -f "$edp_bin_dir/edp" ) then
            echo "[DEBUG]   ✓ edp exists: $edp_bin_dir/edp" >& /dev/stderr
            ls -l "$edp_bin_dir/edp" >& /dev/stderr
        else
            echo "[DEBUG]   ✗ edp NOT found: $edp_bin_dir/edp" >& /dev/stderr
        endif
        if ( -f "$edp_bin_dir/edp_init" ) then
            echo "[DEBUG]   ✓ edp_init exists: $edp_bin_dir/edp_init" >& /dev/stderr
            ls -l "$edp_bin_dir/edp_init" >& /dev/stderr
        else
            echo "[DEBUG]   ✗ edp_init NOT found: $edp_bin_dir/edp_init" >& /dev/stderr
        endif
        echo "[DEBUG] Testing commands:" >& /dev/stderr
        if ( `which edp >& /dev/null` ) then
            echo "[DEBUG]   ✓ which edp: `which edp`" >& /dev/stderr
        else
            echo "[DEBUG]   ✗ which edp: not found" >& /dev/stderr
        endif
        if ( `which edp_init >& /dev/null` ) then
            echo "[DEBUG]   ✓ which edp_init: `which edp_init`" >& /dev/stderr
        else
            echo "[DEBUG]   ✗ which edp_init: not found" >& /dev/stderr
        endif
    endif
endif

