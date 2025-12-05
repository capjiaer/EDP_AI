#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Main Setup - 安装配置文件
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='edp-main',
    version='0.1.0',
    description='EDP Main - 统一的工作流管理工具',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='EDP Team',
    author_email='',
    url='',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'pyyaml>=5.1',
    ],
    # 注意：edp-dirkit, configkit, edp-cmdkit, flowkit 需要单独安装
    # 或者通过开发模式安装：
    # pip install -e edp_center/packages/edp_dirkit
    # pip install -e edp_center/packages/edp_configkit
    # pip install -e edp_center/packages/edp_cmdkit
    # pip install -e edp_center/packages/edp_flowkit
    entry_points={
        'console_scripts': [
            'edp-main=edp_center.main.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

