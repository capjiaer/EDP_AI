#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Main Entry Point
Wrapper script for CLI access
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import and run CLI
from edp_center.main.cli import main

if __name__ == '__main__':
    sys.exit(main())

