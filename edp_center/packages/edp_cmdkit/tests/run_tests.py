#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行 edp_cmdkit 的所有测试
"""

import sys
import unittest
from pathlib import Path

# 添加包路径
package_dir = Path(__file__).parent.parent
sys.path.insert(0, str(package_dir.parent.parent))

if __name__ == '__main__':
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    suite = loader.discover(str(Path(__file__).parent), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)

