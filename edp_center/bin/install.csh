#!/bin/tcsh
# 
# EDP 一键安装脚本（Csh/Tcsh 版本）
# 用户只需要 source 这个脚本，就能完成所有设置
# 
# 使用方法：
#   source /path/to/EDP_AI/edp_center/bin/install.csh
# 
# 或者：
#   . /path/to/EDP_AI/edp_center/bin/install.csh

# 获取脚本所在目录（edp_center/bin 的绝对路径）
# 在 csh/tcsh 中，source 时 $0 是 shell 名称，不是脚本路径
# 需要特殊处理
set SCRIPT_DIR = ""
set BIN_DIR = ""
set PROJECT_ROOT = ""

# 方法 1: 如果当前目录就是 edp_center/bin（最常见的情况）
if ( -f "./install.csh" ) then
    set SCRIPT_DIR = `pwd`
    set BIN_DIR = "$SCRIPT_DIR"
    set PROJECT_ROOT = `cd ../.. && pwd`
else
    # 方法 2: 从当前目录向上查找 edp_center/bin
    set current_dir = `pwd`
    set found = "0"
    set depth = 0
    while ( $depth < 10 && "$current_dir" != "/" )
        if ( -f "$current_dir/edp_center/bin/install.csh" ) then
            set SCRIPT_DIR = "$current_dir/edp_center/bin"
            set BIN_DIR = "$SCRIPT_DIR"
            set PROJECT_ROOT = "$current_dir"
            set found = "1"
            break
        endif
        set current_dir = `dirname "$current_dir"`
        @ depth++
    end
    
    # 方法 3: 如果还是找不到，尝试从环境变量获取
    if ( "$found" != "1" ) then
        if ( $?EDP_BIN_PATH ) then
            set BIN_DIR = "$EDP_BIN_PATH"
            set PROJECT_ROOT = `cd "$BIN_DIR/../.." && pwd`
        else if ( $?EDP_CENTER_PATH ) then
            set BIN_DIR = "$EDP_CENTER_PATH/bin"
            set PROJECT_ROOT = `cd "$EDP_CENTER_PATH/.." && pwd`
        else
            echo "⚠️  无法确定 edp_center/bin 目录" >& /dev/stderr
            echo "   请确保在 edp_center/bin 目录下 source，或使用完整路径：" >& /dev/stderr
            echo "   source /path/to/EDP_AI/edp_center/bin/install.csh" >& /dev/stderr
            # 使用当前目录作为默认值（可能不正确，但至少不会报错）
            set BIN_DIR = `pwd`
            set PROJECT_ROOT = `cd ../.. && pwd`
        endif
    endif
endif

echo "=== EDP 一键安装 ==="
echo ""
echo "项目根目录: $PROJECT_ROOT"
echo "bin 目录: $BIN_DIR"
echo ""

# 步骤 0: 设置可执行权限
echo "[0/3] 设置可执行权限..."
if ( -d "$BIN_DIR" ) then
    # 设置所有脚本文件的可执行权限
    chmod +x "$BIN_DIR"/edp "$BIN_DIR"/edp_init "$BIN_DIR"/edp_info >& /dev/null
    chmod +x "$BIN_DIR"/edp.py "$BIN_DIR"/edp_init.py "$BIN_DIR"/edp_info.py >& /dev/null
    chmod +x "$BIN_DIR"/*.sh "$BIN_DIR"/*.csh >& /dev/null
    echo "   ✓ 可执行权限已设置"
else
    echo "   ⚠️  bin 目录不存在: $BIN_DIR"
endif
echo ""

# 步骤 1: 设置 PATH
echo "[1/3] 设置 PATH..."
if ( -f "$BIN_DIR/setup_path.sh" ) then
    # 检查 shell 类型并设置对应的配置文件
    set SHELL_CONFIG = "$HOME/.cshrc"
    if ( $?TCSH_VERSION ) then
        set SHELL_CONFIG = "$HOME/.tcshrc"
    endif
    
    # 检查是否已经添加
    if ( `grep -c "$BIN_DIR" "$SHELL_CONFIG" 2>/dev/null` > 0 ) then
        echo "   ✓ PATH 已经包含 $BIN_DIR"
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# EDP Main - Add bin directory to PATH" >> "$SHELL_CONFIG"
        echo "set path = (\$path $BIN_DIR)" >> "$SHELL_CONFIG"
        echo "   ✓ PATH 配置已添加"
    endif
    
    # 立即添加到当前 shell 的 PATH
    if ( `echo $path | grep -c "$BIN_DIR"` == 0 ) then
        set path = ($BIN_DIR $path)
    endif
    echo "   ✓ PATH 已添加到当前 shell"
else
    echo "   ⚠️  setup_path.sh 不存在，跳过 PATH 设置"
endif
echo ""

# 步骤 2: 检查命令是否可用
echo "[2/3] 检查命令..."
if ( `which edp >& /dev/null` ) then
    echo "   ✓ edp 命令可用: `which edp`"
else
    echo "   ❌ edp 命令不可用"
    echo "   请检查 PATH 设置"
endif
if ( `which edp_init >& /dev/null` ) then
    echo "   ✓ edp_init 命令可用: `which edp_init`"
else
    echo "   ❌ edp_init 命令不可用"
    echo "   请检查 PATH 设置"
endif
if ( `which edp_info >& /dev/null` ) then
    echo "   ✓ edp_info 命令可用: `which edp_info`"
else
    echo "   ❌ edp_info 命令不可用"
    echo "   请检查 PATH 设置"
endif
echo ""

# 总结
echo "=== 安装完成 ==="
echo ""
echo "✅ 所有设置已完成！"
echo ""
echo "现在可以使用："
echo "  edp --help        # 运行相关命令"
echo "  edp_init --help   # 初始化相关命令"
echo "  edp_info --help   # 信息查询相关命令"
echo ""
echo "注意："
echo "  - PATH 配置已添加到 $SHELL_CONFIG"
echo "  - 当前 shell 已激活 PATH"
echo "  - 新开的 shell 会自动加载配置（无需再次 source）"
echo ""

