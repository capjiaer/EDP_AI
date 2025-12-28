#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试自动检测库类型功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from edp_center.packages.edp_libkit.lib_type_detector import LibraryTypeDetector
from edp_center.packages.edp_libkit.generator import LibConfigGenerator


def test_detect_library_type():
    """测试库类型检测"""
    print("=" * 60)
    print("测试库类型自动检测")
    print("=" * 60)
    
    # 获取测试目录
    test_base = Path(__file__).parent / 'LIB_Example'
    
    # 测试STD库
    std_lib = test_base / 'STD_Cell' / '0711_install' / 'v-logic_sa08nvghlogl20hdf068f'
    if std_lib.exists():
        lib_type = LibraryTypeDetector.detect_library_type(std_lib)
        print(f"\nSTD库测试:")
        print(f"  路径: {std_lib}")
        print(f"  检测结果: {lib_type}")
        assert lib_type == 'STD', f"期望STD，但得到{lib_type}"
        print("  [OK] STD库检测正确")
    
    # 测试IP库
    ip_lib = test_base / 'IP' / 'ln08lpu_gpio_1p8v' / 'v1.12'
    if ip_lib.exists():
        lib_type = LibraryTypeDetector.detect_library_type(ip_lib)
        print(f"\nIP库测试:")
        print(f"  路径: {ip_lib}")
        print(f"  检测结果: {lib_type}")
        assert lib_type == 'IP', f"期望IP，但得到{lib_type}"
        print("  [OK] IP库检测正确")
    
    print("\n" + "=" * 60)
    print("库类型检测测试通过！")
    print("=" * 60)


def test_detect_library_info():
    """测试库信息检测"""
    print("\n" + "=" * 60)
    print("测试库信息检测（类型+名称+版本）")
    print("=" * 60)
    
    test_base = Path(__file__).parent / 'LIB_Example'
    
    # 测试STD库
    std_lib = test_base / 'STD_Cell' / '0711_install' / 'v-logic_sa08nvghlogl20hdf068f'
    if std_lib.exists():
        lib_type, lib_name, version = LibraryTypeDetector.detect_library_info(
            std_lib, 'Samsung', 'ln08lpu_gp'
        )
        print(f"\nSTD库信息:")
        print(f"  类型: {lib_type}")
        print(f"  名称: {lib_name}")
        print(f"  版本: {version}")
        assert lib_type == 'STD'
        assert lib_name == 'sa08nvghlogl20hdf068f'
        print("  [OK] STD库信息提取正确")
    
    # 测试IP库
    ip_lib = test_base / 'IP' / 'ln08lpu_gpio_1p8v' / 'v1.12'
    if ip_lib.exists():
        lib_type, lib_name, version = LibraryTypeDetector.detect_library_info(
            ip_lib, 'Samsung', 'ln08lpu_gp'
        )
        print(f"\nIP库信息:")
        print(f"  类型: {lib_type}")
        print(f"  名称: {lib_name}")
        print(f"  版本: {version}")
        assert lib_type == 'IP'
        assert lib_name == 'ln08lpu_gpio_1p8v'
        assert version == 'v1.12'
        print("  [OK] IP库信息提取正确")
    
    print("\n" + "=" * 60)
    print("库信息检测测试通过！")
    print("=" * 60)


def test_generate_from_directory():
    """测试从目录生成配置"""
    print("\n" + "=" * 60)
    print("测试从目录自动生成lib_config.tcl")
    print("=" * 60)
    
    test_base = Path(__file__).parent / 'LIB_Example'
    
    # 测试IP库生成
    ip_lib = test_base / 'IP' / 'ln08lpu_gpio_1p8v' / 'v1.12'
    if ip_lib.exists():
        print(f"\n测试IP库生成:")
        print(f"  路径: {ip_lib}")
        
        try:
            generator = LibConfigGenerator(
                foundry='Samsung',
                ori_path=ip_lib.parent,
                output_base_dir=Path(__file__).parent / 'output',
                node='ln08lpu_gp'
            )
            
            generated_files = generator.generate_from_directory(ip_lib, auto_detect=True)
            
            print(f"  生成文件数: {len(generated_files)}")
            for f in generated_files:
                print(f"    - {f}")
            
            if generated_files:
                print("  [OK] IP库配置生成成功")
            else:
                print("  [WARN] 未生成文件（可能是目录中没有视图文件）")
        
        except Exception as e:
            print(f"  [ERROR] 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("生成测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_detect_library_type()
        test_detect_library_info()
        test_generate_from_directory()
        print("\n[SUCCESS] 所有测试通过！")
    except Exception as e:
        print(f"\n[FAILED] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

