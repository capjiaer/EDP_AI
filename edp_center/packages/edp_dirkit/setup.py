#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DirKit 安装脚本
"""

from setuptools import setup, find_packages

version = '0.1.0'

long_description = """
# DirKit

DirKit 是一个用于文件和目录操作的工具库，主要用于从 `edp_center` 资源库初始化项目环境。

## 特性

- **目录操作**：创建、复制、链接目录
- **文件操作**：复制、链接文件
- **项目初始化**：从 edp_center 资源库初始化项目环境
- **配置和流程提取**：自动提取和合并配置文件和流程定义
"""

setup(
    name='dirkit',
    version=version,
    description='文件和目录操作工具库',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Anping Chen',
    author_email='capjiaer@163.com',
    url='https://github.com/capjiaer/edp_packages',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    install_requires=[
        # 基础依赖，不需要额外的第三方库
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'flake8>=3.8',
        ],
    },
    entry_points={
        'console_scripts': [
            'dirkit=dirkit.cli:main',
        ],
    },
)

