#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI启动脚本 - 可以直接运行，无需担心导入问题
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
# run_gui.py 在 edp_center/packages/edp_libkit/
# 需要找到 edp_center 的父目录（项目根目录）
current_file = Path(__file__).resolve()
# current_file.parent = edp_center/packages/edp_libkit/
# current_file.parent.parent = edp_center/packages/
# current_file.parent.parent.parent = edp_center/
# 需要 edp_center 的父目录作为项目根目录
project_root = current_file.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入并运行GUI
from edp_center.packages.edp_libkit.gui import main

if __name__ == '__main__':
    main()

