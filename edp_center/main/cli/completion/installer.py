#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令补全安装工具
用于生成和安装 bash 补全脚本
"""

import sys
import os
from pathlib import Path


def generate_completion_script() -> str:
    """
    生成 bash 补全脚本
    
    Returns:
        bash 补全脚本内容
    """
    script = """# EDP 命令补全脚本
# 此脚本由 edp 自动生成，用于提供 bash 命令补全功能

# 检查 argcomplete 是否可用
if command -v register-python-argcomplete >/dev/null 2>&1; then
    # 使用 argcomplete 的自动补全
    eval "$(register-python-argcomplete edp)"
else
    # 如果没有 argcomplete，提供基本的补全
    _edp_complete() {
        local cur prev opts
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        
        # 基本命令和选项
        opts="-h --help -init -b --branch -run --run -i --info --edp-center --work-path --project -prj --version -v --block -blk --user -u --foundry --node --from-branch-step init-workspace load-config process-script load-workflow run"
        
        # 如果当前词是选项，提供选项补全
        if [[ ${cur} == -* ]]; then
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
        fi
        
        # 根据前一个词提供不同的补全
        case "${prev}" in
            -init|--init)
                # init 命令后可以跟其他选项
                COMPREPLY=( $(compgen -W "--project -prj --version -v --block -blk --user -u --foundry --node" -- ${cur}) )
                ;;
            -b|--branch|-branch)
                # branch 名称补全（从当前目录推断）
                COMPREPLY=( $(compgen -W "$(ls -d */ 2>/dev/null | sed 's|/$||')" -- ${cur}) )
                ;;
            -run|--run)
                # flow.step 格式补全
                if [[ ${cur} == *.* ]]; then
                    # 已经输入了 flow.step 格式
                    local flow="${cur%%.*}"
                    local step_prefix="${cur#*.}"
                    # 这里可以添加更智能的补全逻辑
                    COMPREPLY=( $(compgen -f -- ${cur}) )
                else
                    # 只输入了 flow 名称
                    COMPREPLY=( $(compgen -f -- ${cur}) )
                fi
                ;;
            -i|--info|-info)
                # flow 名称补全
                COMPREPLY=( $(compgen -f -- ${cur}) )
                ;;
            --project|-prj|--version|-v|--block|-blk|--user|-u|--foundry|--node)
                # 这些选项需要值，提供文件补全
                COMPREPLY=( $(compgen -f -- ${cur}) )
                ;;
            *)
                # 默认提供选项补全
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                ;;
        esac
    }
    
    complete -F _edp_complete edp
fi
"""
    return script


def install_completion_script(dest_dir: Path = None) -> bool:
    """
    安装补全脚本到指定目录
    
    Args:
        dest_dir: 目标目录（默认为 ~/.bash_completion.d/）
        
    Returns:
        是否安装成功
    """
    if dest_dir is None:
        home = Path.home()
        dest_dir = home / '.bash_completion.d'
    
    # 创建目标目录（如果不存在）
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"错误: 无法创建目录 {dest_dir}: {e}", file=sys.stderr)
        return False
    
    # 生成补全脚本
    script_content = generate_completion_script()
    script_path = dest_dir / 'edp-completion.bash'
    
    # 写入脚本文件
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        print(f"[OK] 补全脚本已安装到: {script_path}")
        print(f"[INFO] 请将以下内容添加到 ~/.bashrc 或 ~/.bash_profile:")
        print(f"      source {script_path}")
        print(f"[INFO] 或者运行以下命令:")
        print(f"      echo 'source {script_path}' >> ~/.bashrc")
        
        return True
    except Exception as e:
        print(f"错误: 无法写入补全脚本: {e}", file=sys.stderr)
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='EDP 命令补全安装工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 安装到默认位置 (~/.bash_completion.d/)
  python -m edp_center.main.cli.completion_installer
  
  # 安装到指定目录
  python -m edp_center.main.cli.completion_installer --dest /etc/bash_completion.d/
        """
    )
    
    parser.add_argument(
        '--dest',
        type=str,
        help='补全脚本安装目录（默认: ~/.bash_completion.d/）'
    )
    
    parser.add_argument(
        '--generate-only',
        action='store_true',
        help='只生成脚本内容，不安装（输出到标准输出）'
    )
    
    args = parser.parse_args()
    
    if args.generate_only:
        # 只生成脚本内容
        print(generate_completion_script())
        return 0
    
    # 安装补全脚本
    dest_dir = Path(args.dest) if args.dest else None
    success = install_completion_script(dest_dir)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

