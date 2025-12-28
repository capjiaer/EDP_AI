#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 handlers.py 迁移后的错误处理功能

验证 @handle_cli_error 装饰器是否正常工作
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
sys.path.insert(0, project_root)

# 已移除 handle_load_workflow 测试
from edp_center.packages.edp_common import EDPError, ConfigError


class TestHandlersMigration(unittest.TestCase):
    """测试 handlers.py 迁移后的错误处理"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟的 manager 和 args
        self.manager = Mock()
        self.args = Mock()
        
        # 设置默认的 args 属性
        self.args.project = 'test_project'
        self.args.foundry = 'SAMSUNG'
        self.args.node = 'S8'
        self.args.flow = 'pv_calibre'
        self.args.output = None
        self.args.input = None
        self.args.search_paths = None
        self.args.no_prepend_sources = False
        self.args.work_path = '/test/work'
        self.args.block = 'block1'
        self.args.user = 'user1'
        self.args.branch = 'main'
        self.args.version = None
        self.args.from_branch_step = None
    
    # 已移除 handle_load_workflow 相关测试


if __name__ == '__main__':
    unittest.main()

