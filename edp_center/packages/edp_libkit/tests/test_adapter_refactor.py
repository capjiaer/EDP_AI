#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试重构后的适配器功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from edp_center.packages.edp_libkit.generator import LibConfigGenerator


def test_std_library():
    """测试STD库生成"""
    print("=" * 60)
    print("测试STD库生成")
    print("=" * 60)
    
    test_base = Path(__file__).parent / 'LIB_Example'
    std_lib = test_base / 'STD_Cell' / '0711_install' / 'v-logic_sa08nvghlogl20hdf068f'
    
    if not std_lib.exists():
        print(f"[SKIP] STD库目录不存在: {std_lib}")
        return
    
    print(f"\nSTD库路径: {std_lib}")
    
    try:
        generator = LibConfigGenerator(
            foundry='Samsung',
            ori_path=std_lib.parent,
            output_base_dir=Path(__file__).parent / 'output',
            node='ln08lpu_gp'
        )
        
        # 使用指定库类型生成
        generated_files = generator.generate_from_directory(std_lib, lib_type='STD')
        
        print(f"  生成文件数: {len(generated_files)}")
        for f in generated_files:
            print(f"    - {f}")
        
        if generated_files:
            # 检查生成的文件内容
            for f in generated_files:
                if f.exists():
                    content = f.read_text(encoding='utf-8')
                    print(f"\n  生成的文件内容预览（前500字符）:")
                    print(f"  {content[:500]}...")
                    
                    # 检查节点名称是否正确
                    if 'ln08lpu_gp' in content or 'sa08nvghlogl20hdf068f' in content:
                        print("  [OK] STD库配置生成成功，节点名称正确")
                    else:
                        print("  [WARN] 节点名称可能不正确")
        
    except Exception as e:
        print(f"  [ERROR] 生成失败: {e}")
        import traceback
        traceback.print_exc()


def test_ip_library():
    """测试IP库生成"""
    print("\n" + "=" * 60)
    print("测试IP库生成")
    print("=" * 60)
    
    test_base = Path(__file__).parent / 'LIB_Example'
    ip_lib = test_base / 'IP' / 'ln08lpu_gpio_1p8v' / 'v1.12'
    
    if not ip_lib.exists():
        print(f"[SKIP] IP库目录不存在: {ip_lib}")
        return
    
    print(f"\nIP库路径: {ip_lib}")
    
    try:
        generator = LibConfigGenerator(
            foundry='Samsung',
            ori_path=ip_lib.parent,
            output_base_dir=Path(__file__).parent / 'output',
            node='ln08lpu_gp'
        )
        
        # 使用指定库类型生成
        generated_files = generator.generate_from_directory(ip_lib, lib_type='IP')
        
        print(f"  生成文件数: {len(generated_files)}")
        for f in generated_files:
            print(f"    - {f}")
        
        if generated_files:
            # 检查生成的文件内容
            for f in generated_files:
                if f.exists():
                    content = f.read_text(encoding='utf-8')
                    print(f"\n  生成的文件内容预览（前500字符）:")
                    print(f"  {content[:500]}...")
                    
                    # 检查节点名称和库类型是否正确
                    if 'ln08lpu_gpio_1p8v' in content:
                        print("  [OK] IP库配置生成成功，库名称正确")
                    else:
                        print("  [WARN] 库名称可能不正确")
        
    except Exception as e:
        print(f"  [ERROR] 生成失败: {e}")
        import traceback
        traceback.print_exc()


def test_adapter_node_info():
    """测试适配器节点信息"""
    print("\n" + "=" * 60)
    print("测试适配器节点信息")
    print("=" * 60)
    
    try:
        from edp_center.packages.edp_libkit.foundry_adapters import AdapterFactory
        
        # 测试不同节点的适配器
        nodes_to_test = ['ln08lpu_gp', 'ln05lpe', 'ln08lpu_hp']
        
        for node in nodes_to_test:
            print(f"\n测试节点: {node}")
            try:
                adapter = AdapterFactory.create_adapter('Samsung', node)
                
                # 检查适配器是否正确加载
                if adapter._node_adapter:
                    node_key = adapter._node_adapter.node_key
                    identifiers = adapter._node_adapter.identifiers[:2]  # 只显示前2个
                    
                    print(f"  节点键: {node_key}")
                    print(f"  标识符: {identifiers}...")
                    
                    # 验证节点键是否正确
                    if node_key == node:
                        print(f"  [OK] 节点 {node} 适配器加载正确")
                    else:
                        print(f"  [ERROR] 节点键不匹配！期望 {node}，得到 {node_key}")
                else:
                    print(f"  [ERROR] 节点适配器未加载")
                    
            except Exception as e:
                print(f"  [ERROR] 加载节点适配器失败: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_libraries():
    """测试处理多个库（手动指定）"""
    print("\n" + "=" * 60)
    print("测试处理多个库（手动指定每个库）")
    print("=" * 60)
    
    test_base = Path(__file__).parent / 'LIB_Example'
    
    if not test_base.exists():
        print(f"[SKIP] 测试目录不存在: {test_base}")
        return
    
    # 定义要处理的库列表
    libraries = [
        {
            'path': test_base / 'STD_Cell' / '0711_install' / 'v-logic_sa08nvghlogl20hdf068f',
            'type': 'STD'
        },
        {
            'path': test_base / 'IP' / 'ln08lpu_gpio_1p8v' / 'v1.12',
            'type': 'IP'
        }
    ]
    
    generated_files = []
    
    for lib_config in libraries:
        lib_path = lib_config['path']
        lib_type = lib_config['type']
        
        if not lib_path.exists():
            print(f"[SKIP] 库目录不存在: {lib_path}")
            continue
        
        print(f"\n处理库: {lib_path.name} (类型: {lib_type})")
        
        try:
            generator = LibConfigGenerator(
                foundry='Samsung',
                ori_path=lib_path.parent,
                output_base_dir=Path(__file__).parent / 'output',
                node='ln08lpu_gp'
            )
            
            files = generator.generate_from_directory(lib_path, lib_type=lib_type)
            generated_files.extend(files)
            print(f"  [OK] 成功生成 {len(files)} 个配置文件")
        
        except Exception as e:
            print(f"  [ERROR] 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n总共生成 {len(generated_files)} 个配置文件")


if __name__ == '__main__':
    try:
        test_adapter_node_info()
        test_std_library()
        test_ip_library()
        test_multiple_libraries()
        print("\n" + "=" * 60)
        print("[SUCCESS] 所有测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAILED] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

