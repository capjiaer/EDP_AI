#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行 Example 集成测试
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_ai_root = test_file_dir.parent.parent
sys.path.insert(0, str(edp_ai_root))


def run_all_tests():
    """运行所有集成测试"""
    # 发现并加载测试
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(test_file_dir),
        pattern='test_*.py',
        top_level_dir=str(edp_ai_root)
    )
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回退出代码
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)

