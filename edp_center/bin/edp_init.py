#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Init Entry Point
Wrapper script for CLI access (初始化相关命令)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'edp_center' / 'packages' / 'edp_configkit'))

# Import and run CLI
from edp_center.main.cli.cli_init import main

if __name__ == '__main__':
    sys.exit(main())

