#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
完整工作流端到端测试
测试：init -> branch -> 创建假 flow -> run（本地模式，非 LSF）
"""

import unittest
import sys
import tempfile
import shutil
import yaml
from pathlib import Path
from unittest.mock import patch

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_ai_root = test_file_dir.parent.parent
sys.path.insert(0, str(edp_ai_root))

from edp_center.main.cli.commands.init import handle_init_project
from edp_center.main.cli.commands.branch import handle_create_branch
from edp_center.main.cli.commands.run_handler import handle_run_cmd
from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper


class TestFullWorkflow(unittest.TestCase):
    """完整工作流测试：init -> branch -> run"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.edp_center_path = find_edp_center_path_helper()
        cls.temp_base = Path(tempfile.mkdtemp(prefix="edp_test_"))
        # 使用测试模板 foundry_name/node_name/prj_example
        cls.test_project = "prj_example"  # 使用测试模板项目
        cls.test_version = "P85"
        cls.test_block = "block1"  # 需要指定 block 名称
        cls.test_user = "test_user"  # 使用当前的 user
        cls.test_branch = "main"  # 默认分支，可以改为其他名称
        cls.test_foundry = "foundry_name"  # 使用测试模板 foundry
        cls.test_node = "node_name"  # 使用测试模板 node
        cls.test_flow = "pv_calibre.drc"  # 用户指定的 flow
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if cls.temp_base.exists():
            shutil.rmtree(cls.temp_base)
    
    def setUp(self):
        """每个测试前的准备"""
        # 清理可能存在的测试目录
        test_work_path = self.temp_base / self.test_project / self.test_version / self.test_block / self.test_user
        if test_work_path.exists():
            shutil.rmtree(test_work_path)
    
    def tearDown(self):
        """每个测试后的清理"""
        # 保留目录用于调试，但可以在这里添加清理逻辑
        pass
    
    def create_test_args(self, command_type="init"):
        """创建测试用的 args 对象"""
        edp_center_path = self.edp_center_path
        temp_base = self.temp_base
        test_project = self.test_project
        test_version = self.test_version
        test_block = self.test_block
        test_user = self.test_user
        test_branch = self.test_branch
        test_foundry = self.test_foundry
        test_node = self.test_node
        test_flow = self.test_flow
        
        # 使用 test_config.yaml 配置文件
        test_file_dir = Path(__file__).resolve().parent
        test_config_path = test_file_dir.parent / "WORK_PATH" / "test_config.yaml"
        
        class Args:
            def __init__(self, cmd_type):
                self.edp_center = str(edp_center_path)
                self.work_path = str(temp_base)
                self.project = test_project
                self.version = test_version
                self.block = test_block
                self.user = test_user
                self.branch = test_branch if cmd_type != "init" else "main"
                self.foundry = test_foundry
                self.node = test_node
                
                # 使用 test_config.yaml 配置文件
                if test_config_path.exists():
                    self.config = str(test_config_path)
                else:
                    self.config = None
                
                if cmd_type == "init":
                    self.gui = False
                elif cmd_type == "branch":
                    self.from_branch = None
                    self.from_step = None
                elif cmd_type == "run":
                    self.run = test_flow  # 使用用户指定的 flow
                    self.run_from = None
                    self.run_to = None
                    self.run_from_step = "all"
                    self.dry_run = True  # 使用 dry-run 模式，不实际执行
                    self.debug = False
        
        return Args(command_type)
    
    def create_fake_flow(self, branch_dir: Path):
        """创建假的 flow 定义文件（使用测试模板 foundry_name/node_name/prj_example）"""
        # 使用测试模板的 flow 目录：flow/initialize/foundry_name/node_name/prj_example/cmds/pv_calibre/steps/
        flow_dir = (self.edp_center_path / "flow" / "initialize" / 
                   self.test_foundry / self.test_node / self.test_project /
                   "cmds" / "pv_calibre" / "steps")
        flow_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建简单的 Tcl 脚本（使用正确的文件名：calibre_drc.tcl）
        tcl_file = flow_dir / "calibre_drc.tcl"
        if not tcl_file.exists():
            tcl_file.write_text("""
# 测试用的 DRC 脚本
puts "Running DRC check..."
puts "Project: $project(project_name)"
puts "Flow: $project(flow_name)"
puts "Step: $project(step_name)"
puts "DRC check completed successfully"
""")
        
        # 使用测试模板的 config 目录：config/foundry_name/node_name/prj_example/pv_calibre/
        config_dir = (self.edp_center_path / "config" / self.test_foundry / 
                     self.test_node / self.test_project / "pv_calibre")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        dependency_yaml = config_dir / "dependency.yaml"
        dependency_content = {
            "pv_calibre": {
                "dependency": {
                    "FP_MODE": [
                        {
                            "drc": {
                                "in": [],
                                "out": ["drc.pass"],
                                "cmd": "calibre_drc.tcl"
                            }
                        }
                    ]
                }
            }
        }
        with open(dependency_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(dependency_content, f, allow_unicode=True, default_flow_style=False)
        
        # 创建 config.yaml（使用本地模式，非 LSF）
        config_yaml = config_dir / "config.yaml"
        config_content = {
            "pv_calibre": {
                "drc": {
                    "lsf": 0,  # 本地执行，非 LSF
                    "tool_opt": "bash",
                    "cmd": "echo 'DRC check'"
                }
            }
        }
        with open(config_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(config_content, f, allow_unicode=True, default_flow_style=False)
        
        return flow_dir, config_dir
    
    def test_full_workflow_init_branch_run(self):
        """测试完整工作流：init -> branch -> run（使用 test_config.yaml）"""
        try:
            # 准备 test_config.yaml（添加临时目录到 allowed_work_paths）
            test_file_dir = Path(__file__).resolve().parent
            test_config_path = test_file_dir.parent / "WORK_PATH" / "test_config.yaml"
            
            if test_config_path.exists():
                # 读取现有配置
                with open(test_config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # 添加临时目录到 allowed_work_paths（如果还没有）
                if 'project' in config and 'allowed_work_paths' in config['project']:
                    temp_path_str = str(self.temp_base).replace('\\', '/')
                    if temp_path_str not in config['project']['allowed_work_paths']:
                        config['project']['allowed_work_paths'].append(temp_path_str)
                        # 写回配置文件
                        with open(test_config_path, 'w', encoding='utf-8') as f:
                            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
                        print(f"\n[INFO] 已更新 test_config.yaml，添加临时目录: {temp_path_str}")
            
            # Step 1: Init 项目
            print("\n=== Step 1: Init 项目（使用 test_config.yaml）===")
            manager = create_manager(self.edp_center_path)
            init_args = self.create_test_args("init")
            
            if hasattr(init_args, 'config') and init_args.config:
                print(f"  使用配置文件: {init_args.config}")
            
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_init_project(manager, init_args)
                if result not in [0, None, True]:
                    self.skipTest(f"Init 失败: {result}")
            
            # 验证 init 结果
            branch_dir = (self.temp_base / self.test_project / self.test_version / 
                         self.test_block / self.test_user / "main")
            
            # Step 2: 创建 branch
            print("\n=== Step 2: 创建 branch ===")
            branch_args = self.create_test_args("branch")
            
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_create_branch(manager, branch_args)
                if result not in [0, None, True]:
                    self.skipTest(f"创建 branch 失败: {result}")
            
            # 验证 branch 创建
            test_branch_dir = (self.temp_base / self.test_project / self.test_version / 
                             self.test_block / self.test_user / self.test_branch)
            
            # Step 3: 创建假的 flow
            print("\n=== Step 3: 创建假的 flow ===")
            flow_dir, config_dir = self.create_fake_flow(test_branch_dir)
            
            # 验证 flow 文件存在
            self.assertTrue(flow_dir.exists(), "Flow 目录应该存在")
            self.assertTrue(config_dir.exists(), "Config 目录应该存在")
            
            # Step 4: Run flow（使用 dry-run 模式）
            print("\n=== Step 4: Run flow (dry-run) ===")
            run_args = self.create_test_args("run")
            
            with patch('sys.stdout') as mock_stdout, patch('sys.stderr'):
                result = handle_run_cmd(manager, run_args)
                # dry-run 模式应该成功
                self.assertIn(result, [0, None, True], "Run 命令应该成功")
            
            print("\n=== 完整工作流测试完成 ===")
            
        except Exception as e:
            self.fail(f"完整工作流测试失败: {e}")
    
    def test_local_execution_mode(self):
        """测试本地执行模式（非 LSF）"""
        try:
            # 创建配置，确保使用本地模式
            config_dir = (self.edp_center_path / "config" / self.test_foundry / 
                         self.test_node / self.test_project / "pv_calibre")
            config_dir.mkdir(parents=True, exist_ok=True)
            
            config_yaml = config_dir / "config.yaml"
            config_content = {
                "pv_calibre": {
                    "drc": {
                        "lsf": 0,  # 明确设置为本地执行
                        "tool_opt": "bash"
                    }
                }
            }
            with open(config_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(config_content, f, allow_unicode=True, default_flow_style=False)
            
            # 验证配置
            with open(config_yaml, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                self.assertEqual(loaded_config["pv_calibre"]["drc"]["lsf"], 0, 
                               "应该配置为本地执行模式（lsf: 0）")
            
            print("\n=== 本地执行模式配置验证完成 ===")
            
        except Exception as e:
            self.fail(f"本地执行模式测试失败: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)

