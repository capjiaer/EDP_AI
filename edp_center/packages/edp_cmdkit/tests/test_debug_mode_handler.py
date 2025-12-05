#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 debug_mode_handler 模块
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.debug_mode_handler import (
    escape_tcl_string,
    generate_debug_mode_script
)


class TestDebugModeHandler(unittest.TestCase):
    """测试 debug_mode_handler 模块"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_escape_tcl_string(self):
        """测试 Tcl 字符串转义"""
        # escape_tcl_string 对于代码块直接返回（因为会放在 proc {} 块中）
        text = 'puts "Hello World"'
        result = escape_tcl_string(text)
        self.assertEqual(result, text)
        
        # 多行代码
        multiline = 'puts "Line 1"\nputs "Line 2"'
        result = escape_tcl_string(multiline)
        self.assertEqual(result, multiline)
    
    def test_generate_debug_mode_script_simple(self):
        """测试生成简单的 debug 模式脚本"""
        original_content = """
puts "Hello World"
"""
        
        # Mock parse_main_script_func
        def mock_parse_func(content, step_name, edp_center_path, foundry, node, project, flow_name, hooks_dir=None):
            return [], {}
        
        result = generate_debug_mode_script(
            original_content,
            "test_step",
            self.temp_path / "test.tcl",
            None,
            None,
            None,
            None,
            "test_flow",
            mock_parse_func
        )
        
        # 检查结果包含原始内容
        self.assertIn("Hello World", result)
        # 检查结果包含 edp_run 调用
        self.assertIn("edp_run", result)
    
    def test_generate_debug_mode_script_with_step_hooks(self):
        """测试生成包含 step hooks 的 debug 模式脚本"""
        original_content = """
# ========== step.pre hook ==========
puts "pre hook"
# ========== end of step.pre hook ==========
puts "main script"
# ========== step.post hook ==========
puts "post hook"
# ========== end of step.post hook ==========
"""
        
        def mock_parse_func(content, step_name, edp_center_path, foundry, node, project, flow_name, hooks_dir=None):
            return [], {}
        
        result = generate_debug_mode_script(
            original_content,
            "test_step",
            self.temp_path / "test.tcl",
            None,
            None,
            None,
            None,
            "test_flow",
            mock_parse_func
        )
        
        # 检查结果包含 hooks 内容
        self.assertIn("pre hook", result)
        self.assertIn("post hook", result)
        self.assertIn("main script", result)
    
    def test_generate_debug_mode_script_with_execution_plan(self):
        """测试生成包含执行计划的 debug 模式脚本"""
        original_content = """
puts "main script"
"""
        
        def mock_parse_func(content, step_name, edp_center_path, foundry, node, project, flow_name, hooks_dir=None):
            # 返回一个执行计划
            execution_plan = ["proc1", "proc2"]
            return execution_plan
        
        result = generate_debug_mode_script(
            original_content,
            "test_step",
            self.temp_path / "test.tcl",
            None,
            None,
            None,
            None,
            "test_flow",
            mock_parse_func
        )
        
        # 检查结果包含执行计划
        self.assertIn("proc1", result)
        self.assertIn("proc2", result)
        self.assertIn("edp_run", result)
    
    def test_generate_debug_mode_script_with_util_procs(self):
        """测试生成包含 util procs 的 debug 模式脚本"""
        original_content = """
puts "main script"
"""
        
        def mock_parse_func(content, step_name, edp_center_path, foundry, node, project, flow_name, hooks_dir=None):
            execution_plan = []
            return execution_plan
        
        result = generate_debug_mode_script(
            original_content,
            "test_step",
            self.temp_path / "test.tcl",
            None,
            None,
            None,
            None,
            "test_flow",
            mock_parse_func
        )
        
        # 检查结果包含 util proc 定义
        self.assertIn("util_helper", result)
        self.assertIn("helper code", result)


if __name__ == '__main__':
    unittest.main()

