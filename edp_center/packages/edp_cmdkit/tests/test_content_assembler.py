#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 content_assembler 模块
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

from edp_cmdkit.content_assembler import (
    validate_no_import_between_sub_steps,
    assemble_content_with_hooks
)


class TestContentAssembler(unittest.TestCase):
    """测试 content_assembler 模块"""

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
        
        # 创建 common 目录
        self.common_dir = self.config_path / "common" / "flow1"
        self.common_dir.mkdir(parents=True)
        
        # 创建主脚本
        self.main_script = self.temp_path / "main.tcl"
        
        # 创建 hooks 目录
        self.hooks_dir = self.temp_path / "hooks"
        self.hooks_dir.mkdir()

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_assemble_content_with_hooks_step_pre(self):
        """测试整合 step.pre hook"""
        # 创建 step.pre hook
        step_pre_file = self.hooks_dir / "step.pre"
        step_pre_file.write_text("puts \"Pre hook\"")
        
        # 创建主脚本
        self.main_script.write_text("puts \"Main script\"")
        
        result = assemble_content_with_hooks(
            self.main_script,
            [self.temp_path],
            hooks_dir=self.hooks_dir,
            step_name="step1"
        )
        
        self.assertIn("Pre hook", result)
        self.assertIn("Main script", result)
        self.assertIn("step.pre hook", result)

    def test_assemble_content_with_hooks_step_post(self):
        """测试整合 step.post hook"""
        # 创建 step.post hook
        step_post_file = self.hooks_dir / "step.post"
        step_post_file.write_text("puts \"Post hook\"")
        
        # 创建主脚本
        self.main_script.write_text("puts \"Main script\"")
        
        result = assemble_content_with_hooks(
            self.main_script,
            [self.temp_path],
            hooks_dir=self.hooks_dir,
            step_name="step1"
        )
        
        self.assertIn("Post hook", result)
        self.assertIn("Main script", result)
        self.assertIn("step.post hook", result)

    def test_assemble_content_with_hooks_both(self):
        """测试同时整合 step.pre 和 step.post"""
        # 创建 hooks
        step_pre_file = self.hooks_dir / "step.pre"
        step_pre_file.write_text("puts \"Pre hook\"")
        
        step_post_file = self.hooks_dir / "step.post"
        step_post_file.write_text("puts \"Post hook\"")
        
        # 创建主脚本
        self.main_script.write_text("puts \"Main script\"")
        
        result = assemble_content_with_hooks(
            self.main_script,
            [self.temp_path],
            hooks_dir=self.hooks_dir,
            step_name="step1"
        )
        
        # 检查顺序：pre -> main -> post
        pre_idx = result.find("Pre hook")
        main_idx = result.find("Main script")
        post_idx = result.find("Post hook")
        
        self.assertLess(pre_idx, main_idx)
        self.assertLess(main_idx, post_idx)

    def test_assemble_content_with_hooks_empty_hooks(self):
        """测试空 hooks（只有注释）"""
        # 创建空的 step.pre hook（只有注释）
        step_pre_file = self.hooks_dir / "step.pre"
        step_pre_file.write_text("# Empty hook\n# Just comments")
        
        # 创建主脚本
        self.main_script.write_text("puts \"Main script\"")
        
        result = assemble_content_with_hooks(
            self.main_script,
            [self.temp_path],
            hooks_dir=self.hooks_dir,
            step_name="step1"
        )
        
        # 空 hook 不应该被添加
        self.assertNotIn("step.pre hook", result)
        self.assertIn("Main script", result)

    def test_validate_no_import_between_sub_steps_no_sub_steps(self):
        """测试没有 sub_steps 时验证通过"""
        # 创建主脚本
        main_content = "puts \"Main script\"\n#import source helper.tcl\nputs \"After import\""
        
        # 没有 sub_steps，应该通过验证
        validate_no_import_between_sub_steps(
            main_content,
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1"
        )
        # 如果没有异常，测试通过

    def test_validate_no_import_between_sub_steps_with_import(self):
        """测试在 sub_steps 之间使用 #import 时抛出异常"""
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
        
        # 创建主脚本（在 sub_steps 之间使用 #import）
        main_content = (
            "flow1::proc1\n"
            "#import source helper.tcl\n"
            "flow1::proc2"
        )
        
        # 应该抛出 ValueError
        with self.assertRaises(ValueError) as context:
            validate_no_import_between_sub_steps(
                main_content,
                self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1"
            )
        
        error_msg = str(context.exception)
        self.assertIn("sub_steps", error_msg.lower())
        self.assertIn("import", error_msg.lower())

    def test_validate_no_import_between_sub_steps_no_import(self):
        """测试没有在 sub_steps 之间使用 #import 时验证通过"""
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
        
        # 创建主脚本（没有在 sub_steps 之间使用 #import）
        main_content = (
            "puts \"Before\"\n"
            "flow1::proc1\n"
            "flow1::proc2\n"
            "puts \"After\"\n"
            "#import source helper.tcl\n"
        )
        
        # 应该通过验证（没有异常）
        validate_no_import_between_sub_steps(
            main_content,
            self.edp_center, "FOUNDRY", "NODE", None, "flow1", "step1"
        )

    def test_assemble_content_file_not_found(self):
        """测试主脚本文件不存在时抛出异常"""
        nonexistent_script = self.temp_path / "nonexistent.tcl"
        
        with self.assertRaises(IOError):
            assemble_content_with_hooks(
                nonexistent_script,
                [self.temp_path]
            )


if __name__ == '__main__':
    unittest.main()

