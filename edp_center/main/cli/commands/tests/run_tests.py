#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行 CLI 命令测试
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_center_root = test_file_dir.parent.parent.parent.parent
sys.path.insert(0, str(edp_center_root))


def run_all_tests():
    """运行所有测试"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(test_file_dir),
        pattern='test_*.py',
        top_level_dir=str(edp_center_root)
    )
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回退出代码
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_name):
    """运行特定测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # 运行所有测试
        exit_code = run_all_tests()
    
    sys.exit(exit_code)

