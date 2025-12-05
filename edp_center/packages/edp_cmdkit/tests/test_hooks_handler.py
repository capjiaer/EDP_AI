#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 hooks_handler 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.hooks_handler import (
    is_hook_file_empty
)


class TestHooksHandler(unittest.TestCase):
    """测试 hooks_handler 模块"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 hooks 目录
        self.hooks_dir = self.temp_path / "hooks"
        self.hooks_dir.mkdir()

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_is_hook_file_empty_with_empty_content(self):
        """测试空内容"""
        self.assertTrue(is_hook_file_empty(""))
        self.assertTrue(is_hook_file_empty("   \n  \n  "))

    def test_is_hook_file_empty_with_comments_only(self):
        """测试只有注释的内容"""
        content = "# This is a comment\n# Another comment\n  \n"
        self.assertTrue(is_hook_file_empty(content))

    def test_is_hook_file_empty_with_code(self):
        """测试包含代码的内容"""
        content = "# Comment\nputs \"Hello\"\n# Another comment"
        self.assertFalse(is_hook_file_empty(content))

    # 注意：已移除 #import util 机制，以下测试已删除：
    # - test_get_util_pre_* 系列测试
    # - test_get_util_post_* 系列测试
    # - test_get_util_replace_* 系列测试
    # - test_get_util_override_* 系列测试
    # 这些测试不再需要，因为框架已统一使用 #import source 机制


if __name__ == '__main__':
    unittest.main()

