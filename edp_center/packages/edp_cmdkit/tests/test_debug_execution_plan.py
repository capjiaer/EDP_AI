#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 debug_execution_plan 模块
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import yaml

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入模块
from edp_cmdkit.debug_execution_plan import parse_main_script_for_execution_plan


class TestDebugExecutionPlan(unittest.TestCase):
    """测试 debug_execution_plan 模块"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 edp_center 目录结构
        self.edp_center = self.temp_path / "edp_center"
        self.edp_center.mkdir()
        
        # 创建 config 目录结构
        self.config_dir = self.edp_center / "config" / "FOUNDRY" / "NODE"
        self.config_dir.mkdir(parents=True)
        
        # 创建 flow 目录结构
        self.flow_dir = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE"
        self.flow_dir.mkdir(parents=True)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_dependency_yaml(self, flow_name: str, step_name: str, sub_steps: list):
        """创建 dependency.yaml 文件"""
        dep_file = self.config_dir / "common" / flow_name / "dependency.yaml"
        dep_file.parent.mkdir(parents=True, exist_ok=True)
        
        dependency = {
            flow_name: {
                "dependency": [
                    {
                        step_name: {
                            "out": f"{step_name}.pass",
                            "cmd": f"{step_name}.tcl",
                            "sub_steps": sub_steps
                        }
                    }
                ]
            }
        }
        
        with open(dep_file, 'w', encoding='utf-8') as f:
            yaml.dump(dependency, f, default_flow_style=False)
    
    def test_parse_main_script_with_sub_steps(self):
        """测试解析包含 sub_steps 的主脚本"""
        # 创建 dependency.yaml
        sub_steps = [
            {"sub_step1.tcl": "flow::sub_step1"},
            {"sub_step2.tcl": "flow::sub_step2"}
        ]
        self._create_dependency_yaml("test_flow", "test_step", sub_steps)
        
        # 创建主脚本内容（需要实际调用 proc，而不是字符串）
        main_script = """
flow::sub_step1
some code
flow::sub_step2
"""
        
        execution_plan = parse_main_script_for_execution_plan(
            main_script,
            "test_step",
            str(self.edp_center),
            "FOUNDRY",
            "NODE",
            None,
            "test_flow"
        )
        
        # 检查执行计划
        self.assertIn("flow::sub_step1", execution_plan)
        self.assertIn("flow::sub_step2", execution_plan)
        self.assertEqual(len(execution_plan), 2)
    
    def test_parse_main_script_with_util_blocks(self):
        """测试解析包含 util 代码块的主脚本"""
        # 创建 dependency.yaml（空 sub_steps）
        self._create_dependency_yaml("test_flow", "test_step", [])
        
        # 创建主脚本内容（包含 util 代码块）
        main_script = """
# ========== util: helper.tcl ==========
puts "Hello from helper"
# ========== end of util: helper.tcl ==========
"""
        
        execution_plan = parse_main_script_for_execution_plan(
            main_script,
            "test_step",
            str(self.edp_center),
            "FOUNDRY",
            "NODE",
            None,
            "test_flow"
        )
        
        # util 代码块不再被识别，执行计划应该为空
        self.assertEqual(len(execution_plan), 0)
    
    def test_parse_main_script_with_mixed_content(self):
        """测试解析包含 sub_steps 和 util 代码块的混合内容"""
        # 创建 dependency.yaml
        sub_steps = [
            {"sub_step1.tcl": "flow::sub_step1"}
        ]
        self._create_dependency_yaml("test_flow", "test_step", sub_steps)
        
        # 创建主脚本内容
        main_script = """
# ========== util: helper.tcl ==========
puts "helper code"
# ========== end of util: helper.tcl ==========
flow::sub_step1
some code
"""
        
        execution_plan = parse_main_script_for_execution_plan(
            main_script,
            "test_step",
            str(self.edp_center),
            "FOUNDRY",
            "NODE",
            None,
            "test_flow"
        )
        
        # 检查执行计划（util 代码块不再被识别）
        self.assertIn("flow::sub_step1", execution_plan)
    
    def test_parse_main_script_without_edp_center(self):
        """测试在没有 edp_center_path 的情况下解析"""
        main_script = """
some code
"""
        
        execution_plan = parse_main_script_for_execution_plan(
            main_script,
            "test_step",
            None,
            None,
            None,
            None,
            "test_flow"
        )
        
        # 应该返回空的执行计划
        self.assertEqual(len(execution_plan), 0)
    
    def test_parse_main_script_with_project(self):
        """测试解析项目特定的 sub_steps"""
        # 创建 common dependency.yaml
        common_sub_steps = [
            {"sub_step1.tcl": "flow::sub_step1"}
        ]
        self._create_dependency_yaml("test_flow", "test_step", common_sub_steps)
        
        # 创建项目 dependency.yaml
        project_dep_file = self.config_dir / "PROJECT" / "test_flow" / "dependency.yaml"
        project_dep_file.parent.mkdir(parents=True, exist_ok=True)
        
        project_sub_steps = [
            {"sub_step2.tcl": "flow::sub_step2"}
        ]
        project_dependency = {
            "test_flow": {
                "dependency": [
                    {
                        "test_step": {
                            "out": "test_step.pass",
                            "cmd": "test_step.tcl",
                            "sub_steps": project_sub_steps
                        }
                    }
                ]
            }
        }
        
        with open(project_dep_file, 'w', encoding='utf-8') as f:
            yaml.dump(project_dependency, f, default_flow_style=False)
        
        main_script = """
flow::sub_step2
"""
        
        execution_plan = parse_main_script_for_execution_plan(
            main_script,
            "test_step",
            str(self.edp_center),
            "FOUNDRY",
            "NODE",
            "PROJECT",
            "test_flow"
        )
        
        # 应该使用项目特定的 sub_steps
        self.assertIn("flow::sub_step2", execution_plan)
        self.assertNotIn("flow::sub_step1", execution_plan)


if __name__ == '__main__':
    unittest.main()

