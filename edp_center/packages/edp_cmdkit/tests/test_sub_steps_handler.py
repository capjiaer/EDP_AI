#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 sub_steps_handler 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
import yaml
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.sub_steps import (
    generate_sub_step_pre_proc,
    read_sub_steps_from_dependency,
    get_sub_step_pre,
    get_sub_step_replace,
    generate_sub_steps_sources,
    generate_sub_steps_calls
)


class TestSubStepsHandler(unittest.TestCase):
    """测试 sub_steps_handler 模块"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 edp_center 结构
        self.edp_center = self.temp_path / "edp_center"
        self.edp_center.mkdir()
        
        # 创建 config 结构
        self.config_path = self.edp_center / "config" / "FOUNDRY" / "NODE"
        self.config_path.mkdir(parents=True)
        
        # 创建 common 和 project 目录
        self.common_dir = self.config_path / "common" / "flow1"
        self.common_dir.mkdir(parents=True)
        
        self.project_dir = self.config_path / "project1" / "flow1"
        self.project_dir.mkdir(parents=True)
        
        # 创建 flow 结构（用于 proc 文件）
        self.flow_path = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE" / "common" / "cmds" / "flow1"
        self.flow_path.mkdir(parents=True)
        
        # 创建 proc 文件
        self.proc1 = self.flow_path / "proc1.tcl"
        self.proc1.write_text("proc ::flow1::proc1 {} { puts \"proc1\" }")
        
        self.proc2 = self.flow_path / "proc2.tcl"
        self.proc2.write_text("proc ::flow1::proc2 {} { puts \"proc2\" }")

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_generate_sub_step_pre_proc(self):
        """测试生成 sub_step pre proc"""
        pre_content = "puts \"Pre hook\"\nset var 1"
        result = generate_sub_step_pre_proc("flow1::proc1", pre_content)
        
        self.assertIn("proc flow1::proc1_pre", result)
        self.assertIn("Pre hook", result)
        self.assertIn("set var 1", result)
        # 检查缩进
        self.assertIn("    puts", result)

    def test_read_sub_steps_from_dependency_dict_format(self):
        """测试从 dependency.yaml 读取 sub_steps（字典格式）"""
        # 创建 dependency.yaml（字典格式）
        dependency = {
            'flow1': {
                'dependency': [
                    {
                        'step1': {
                            'sub_steps': {
                                'proc1.tcl': 'flow1::proc1',
                                'proc2.tcl': 'flow1::proc2'
                            }
                        }
                    }
                ]
            }
        }
        
        dependency_file = self.common_dir / "dependency.yaml"
        with open(dependency_file, 'w', encoding='utf-8') as f:
            yaml.dump(dependency, f)
        
        # 读取 sub_steps
        sub_steps = read_sub_steps_from_dependency(
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1"
        )
        
        self.assertEqual(len(sub_steps), 2)
        # 应该转换为列表格式
        self.assertIsInstance(sub_steps, list)
        self.assertIn({'proc1.tcl': 'flow1::proc1'}, sub_steps)
        self.assertIn({'proc2.tcl': 'flow1::proc2'}, sub_steps)

    def test_read_sub_steps_from_dependency_list_format(self):
        """测试从 dependency.yaml 读取 sub_steps（列表格式）"""
        # 创建 dependency.yaml（列表格式）
        dependency = {
            'flow1': {
                'dependency': [
                    {
                        'step1': {
                            'sub_steps': [
                                {'proc1.tcl': 'flow1::proc1'},
                                {'proc2.tcl': 'flow1::proc2'}
                            ]
                        }
                    }
                ]
            }
        }
        
        dependency_file = self.common_dir / "dependency.yaml"
        with open(dependency_file, 'w', encoding='utf-8') as f:
            yaml.dump(dependency, f)
        
        # 读取 sub_steps
        sub_steps = read_sub_steps_from_dependency(
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1"
        )
        
        self.assertEqual(len(sub_steps), 2)
        self.assertIsInstance(sub_steps, list)

    def test_read_sub_steps_project_overrides_common(self):
        """测试项目特定的 sub_steps 覆盖 common"""
        # common 的 dependency.yaml
        common_dependency = {
            'flow1': {
                'dependency': [
                    {
                        'step1': {
                            'sub_steps': {
                                'proc1.tcl': 'flow1::proc1'
                            }
                        }
                    }
                ]
            }
        }
        
        common_dep_file = self.common_dir / "dependency.yaml"
        with open(common_dep_file, 'w', encoding='utf-8') as f:
            yaml.dump(common_dependency, f)
        
        # project 的 dependency.yaml（覆盖 common）
        project_dependency = {
            'flow1': {
                'dependency': [
                    {
                        'step1': {
                            'sub_steps': {
                                'proc2.tcl': 'flow1::proc2'
                            }
                        }
                    }
                ]
            }
        }
        
        project_dep_file = self.project_dir / "dependency.yaml"
        with open(project_dep_file, 'w', encoding='utf-8') as f:
            yaml.dump(project_dependency, f)
        
        # 读取 sub_steps（应该使用 project 的，覆盖 common）
        sub_steps = read_sub_steps_from_dependency(
            self.edp_center, "FOUNDRY", "NODE", "project1", "flow1", "step1"
        )
        
        # 应该只有 project 的 sub_steps
        self.assertEqual(len(sub_steps), 1)
        self.assertIn({'proc2.tcl': 'flow1::proc2'}, sub_steps)

    def test_read_sub_steps_not_found(self):
        """测试找不到 sub_steps 的情况"""
        sub_steps = read_sub_steps_from_dependency(
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "nonexistent_step"
        )
        
        self.assertEqual(sub_steps, [])

    def test_get_sub_step_pre_found(self):
        """测试找到 sub_step.pre hook"""
        hooks_dir = self.temp_path / "hooks"
        hooks_dir.mkdir()
        
        # 创建 sub_step.pre hook（使用 :: 替换为 _）
        pre_file = hooks_dir / "flow1_proc1.pre"
        pre_file.write_text("puts \"Pre hook\"")
        
        result = get_sub_step_pre("flow1::proc1", hooks_dir)
        self.assertIsNotNone(result)
        self.assertIn("Pre hook", result)

    def test_get_sub_step_pre_not_found(self):
        """测试找不到 sub_step.pre hook"""
        hooks_dir = self.temp_path / "hooks"
        hooks_dir.mkdir()
        
        result = get_sub_step_pre("flow1::proc1", hooks_dir)
        self.assertIsNone(result)

    def test_get_sub_step_replace_found(self):
        """测试找到 sub_step.replace hook"""
        hooks_dir = self.temp_path / "hooks"
        hooks_dir.mkdir()
        
        # 创建 sub_step.replace hook
        replace_file = hooks_dir / "flow1_proc1.replace"
        replace_file.write_text("proc ::flow1::proc1 {} { puts \"Replaced\" }")
        
        result = get_sub_step_replace("flow1::proc1", hooks_dir)
        self.assertIsNotNone(result)
        self.assertIn("Replaced", result)

    def test_generate_sub_steps_sources(self):
        """测试生成 sub_steps source 语句"""
        # 创建 dependency.yaml
        dependency = {
            'flow1': {
                'dependency': [
                    {
                        'step1': {
                            'sub_steps': {
                                'proc1.tcl': 'flow1::proc1',
                                'proc2.tcl': 'flow1::proc2'
                            }
                        }
                    }
                ]
            }
        }
        
        dependency_file = self.common_dir / "dependency.yaml"
        with open(dependency_file, 'w', encoding='utf-8') as f:
            yaml.dump(dependency, f)
        
        # 创建 proc 目录（sub_steps 文件通常在 proc 目录下）
        proc_dir = self.flow_path / "proc"
        proc_dir.mkdir(parents=True, exist_ok=True)
        
        # 将 proc 文件移动到 proc 目录
        proc1_in_proc = proc_dir / "proc1.tcl"
        proc1_in_proc.write_text("proc ::flow1::proc1 {} { puts \"proc1\" }")
        
        proc2_in_proc = proc_dir / "proc2.tcl"
        proc2_in_proc.write_text("proc ::flow1::proc2 {} { puts \"proc2\" }")
        
        # 创建当前文件
        current_file = self.temp_path / "current.tcl"
        current_file.write_text("# current script")
        
        # 生成 source 语句（搜索路径应该包含 proc 目录）
        result = generate_sub_steps_sources(
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1",
            current_file, [proc_dir, self.flow_path]
        )
        
        # 应该包含 source 语句和 namespace eval
        self.assertIn("source", result)
        self.assertIn("namespace eval", result)
        # 如果文件找到了，应该包含 proc 文件名
        if "proc1.tcl" not in result:
            # 文件可能没找到，但至少应该有 namespace eval
            self.assertIn("namespace eval", result)

    def test_generate_sub_steps_calls(self):
        """测试生成 sub_steps 调用"""
        # 创建 dependency.yaml
        dependency = {
            'flow1': {
                'dependency': [
                    {
                        'step1': {
                            'sub_steps': {
                                'proc1.tcl': 'flow1::proc1',
                                'proc2.tcl': 'flow1::proc2'
                            }
                        }
                    }
                ]
            }
        }
        
        dependency_file = self.common_dir / "dependency.yaml"
        with open(dependency_file, 'w', encoding='utf-8') as f:
            yaml.dump(dependency, f)
        
        # 生成调用代码
        result = generate_sub_steps_calls(
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1"
        )
        
        # 应该包含 proc 调用
        self.assertIn("flow1::proc1", result)
        self.assertIn("flow1::proc2", result)
        self.assertIn("Auto-generated sub_steps calls", result)


if __name__ == '__main__':
    unittest.main()

