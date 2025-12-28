#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LibGenerator - lib_config.tcl 生成器

负责生成库级别的 lib_config.tcl 文件。
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .lib_info import LibInfo


class LibGenerator:
    """lib_config.tcl 生成器"""
    
    def __init__(self, array_name: str = 'LIBRARY'):
        """
        初始化生成器
        
        Args:
            array_name: lib_config.tcl中的数组变量名（默认：LIBRARY，可以是MEM_LIBRARY等）
        """
        self.array_name = array_name
    
    # 视图类型的格式定义
    VIEW_FORMATS = {
        'gds': {
            'format': 'multi_file',  # 多文件格式
            'key_format': '(cell_name, gds, gds)',
        },
        'lef': {
            'format': 'multi_file',
            'key_format': '(cell_name, lef, lef)',
        },
        'ccs_lvf': {
            'format': 'single_file',  # 单文件格式，每个文件一个条目
            'key_format': '(cell_name, ccs_lvf, normal, filename)',
            'extract_pvt': True,  # 需要从文件名提取PVT信息
        },
        'liberty': {
            'format': 'single_file',
            'key_format': '(cell_name, ccs_lvf, normal, filename)',
            'extract_pvt': True,
        },
        'cdl': {
            'format': 'multi_file',
            'key_format': '(cell_name, cdl, cdl)',
        },
        'verilog': {
            'format': 'multi_file',
            'key_format': '(cell_name, verilog, verilog)',
        },
        'netlists': {
            'format': 'multi_file',
            'key_format': '(cell_name, cdl, cdl)',  # netlists通常包含cdl文件
        },
    }
    
    def generate(self, lib_info: LibInfo, view_files: Dict[str, List[Path]], 
                 output_path: Path, adapter: Optional[object] = None) -> None:
        """
        生成 lib_config.tcl 文件
        
        Args:
            lib_info: 库信息
            view_files: {view_type: [file_paths]} 字典
            output_path: 输出文件路径
            adapter: Foundry适配器（用于SMIC格式的特殊处理）
        """
        entries = []
        
        # 添加文件头注释
        entries.append(f"# Library: {lib_info.lib_name}")
        if lib_info.version:
            entries.append(f"# Version: {lib_info.version}")
        entries.append(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        entries.append("")
        
        # 检查是否是SMIC格式（通过adapter类型判断）
        is_smic_format = adapter and adapter.__class__.__name__ == 'SMICAdapter'
        
        if is_smic_format:
            # SMIC格式：使用MEM_LIBRARY和特殊的格式
            entries.extend(self._generate_smic_format(lib_info, view_files, adapter))
        else:
            # Samsung格式：标准格式
            # 为每个视图类型生成条目
            for view_type, files in view_files.items():
                if not files:
                    continue
                
                # 判断格式类型：如果是单文件格式（liberty相关目录）
                # 检查view_type是否是liberty相关的目录（ccs_lvf, ccs_power, logic_synth等）
                is_single_file_format = view_type in ['ccs_lvf', 'ccs_power', 'logic_synth', 'liberty']
                
                if is_single_file_format:
                    # 单文件格式：每个文件一个条目，使用实际的view_type（目录名）和rc_corner
                    entries.extend(self._generate_single_file_entries_samsung(
                        lib_info.lib_name, view_type, files, adapter
                    ))
                else:
                    # 多文件格式：合并所有文件路径
                    entries.extend(self._generate_multi_file_entry(
                        lib_info.lib_name, view_type, files
                    ))
        
        # 写入文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('\n'.join(entries) + '\n', encoding='utf-8')
    
    def _generate_multi_file_entry(self, cell_name: str, view_type: str, 
                                   files: List[Path]) -> List[str]:
        """
        生成多文件格式的条目
        
        例如：
        set LIBRARY(cell_name,gds,gds) {/path/to/file1.gds /path/to/file2.gds}
        """
        # 规范化路径（转换为绝对路径，使用正斜杠）
        file_paths = [self._normalize_path(f) for f in files]
        
        # 生成条目
        key = f"{cell_name},{view_type},{view_type}"
        value = ' '.join(file_paths)
        
        return [f"set {self.array_name}({key}) {{{value}}}"]
    
    def _generate_single_file_entries_samsung(self, cell_name: str, view_type: str,
                                               files: List[Path], adapter: object) -> List[str]:
        """
        生成Samsung格式的单文件条目
        
        格式：set LIBRARY(cell_name,view_type,rc_corner,pvt_corner,file_type) {file_path}
        
        其中：
        - cell_name: 库名称
        - view_type: 实际的目录名（如 ccs_lvf, ccs_power, logic_synth）
        - rc_corner: 从PVT/PVVT corner提取的rc_corner（sigcmin, sigcmax, typical）
        - pvt_corner: PVT或PVVT corner名称
          - 普通库：PVT格式（如 ffpg0p825vn40c, tt0p75v125c）
          - Level Shifter (dual rail)：PVVT格式（如 ffpg0p8v0p9v125c, tt0p9v1p0v85c）
        - file_type: 文件类型（lib, db）
        
        注意：对于dual rail的level shifter，pvt_corner包含两个电压（PVVT），
        但格式保持不变，rc_corner仍然从Process corner（ff/ss/tt）提取。
        """
        entries = []
        
        for file_path in files:
            filename = file_path.name
            file_path_normalized = self._normalize_path(file_path)
            
            # 提取PVT corner和文件类型
            pvt_corner = None
            file_type = None
            
            # 去掉压缩扩展名（.gz, .bz2 等）
            base_name = filename
            for comp_ext in ['.gz', '.bz2', '.xz', '.z']:
                if base_name.endswith(comp_ext):
                    base_name = base_name[:-len(comp_ext)]
                    break
            
            # 提取文件类型（标准扩展名：db, lib, gds, lef 等）
            # 注意：不要提取完整的扩展名（如 db_ccs_tn_lvf_dths），只提取标准类型
            file_type = None
            name_without_ext = base_name
            
            # 标准文件类型列表（按优先级排序）
            standard_types = ['.db', '.lib', '.gds', '.lef', '.v', '.cdl', '.sp', '.spice', '.ibs']
            
            # 检查是否以标准扩展名结尾
            for std_ext in standard_types:
                if base_name.endswith(std_ext):
                    file_type = std_ext[1:]  # 去掉点号
                    name_without_ext = base_name[:-len(std_ext)]
                    break
            
            # 如果没有找到标准扩展名，尝试从最后一个点提取
            if not file_type:
                if '.' in base_name:
                    last_ext = base_name.split('.')[-1]
                    # 如果最后一个扩展名是标准类型，使用它
                    if last_ext in ['db', 'lib', 'gds', 'lef', 'v', 'cdl', 'sp', 'spice', 'ibs']:
                        file_type = last_ext
                        name_without_ext = '.'.join(base_name.split('.')[:-1])
                    else:
                        # 否则，尝试从文件名中提取标准类型
                        # 例如：xxx.db_ccs_tn_lvf_dths -> db
                        for std_type in ['db', 'lib']:
                            if f'.{std_type}' in base_name or f'_{std_type}' in base_name:
                                file_type = std_type
                                # 找到标准类型后，去掉它及其后面的内容
                                if f'.{std_type}' in base_name:
                                    name_without_ext = base_name[:base_name.index(f'.{std_type}')]
                                else:
                                    name_without_ext = base_name[:base_name.index(f'_{std_type}')]
                                break
                        if not file_type:
                            file_type = last_ext
                            name_without_ext = '.'.join(base_name.split('.')[:-1])
                else:
                    file_type = base_name
                    name_without_ext = base_name
            
            # 从文件名中提取PVT corner（去掉库名前缀）
            if name_without_ext.startswith(cell_name + '_'):
                pvt_corner = name_without_ext[len(cell_name) + 1:]  # 去掉 "cell_name_"
            else:
                # 如果格式不匹配，尝试其他方式
                if '_' in name_without_ext:
                    pvt_corner = name_without_ext.split('_')[-1]
                else:
                    pvt_corner = name_without_ext
            
            # 如果提取失败，使用默认值
            if not pvt_corner:
                pvt_corner = filename
            if not file_type:
                # 从扩展名推断文件类型
                if filename.endswith('.db'):
                    file_type = 'db'
                elif filename.endswith('.lib') or filename.endswith('.lib.gz'):
                    file_type = 'lib'
                else:
                    file_type = 'unknown'
            
            # 从adapter提取rc_corner
            rc_corner = 'typical'  # 默认值
            if adapter and hasattr(adapter, 'extract_rc_corner'):
                rc_corner = adapter.extract_rc_corner(pvt_corner)
            
            # 生成条目
            # 格式：LIBRARY(cell_name,view_type,rc_corner,pvt_corner,file_type)
            key = f"{cell_name},{view_type},{rc_corner},{pvt_corner},{file_type}"
            entries.append(f"set {self.array_name}({key}) {{{file_path_normalized}}}")
        
        return entries
    
    def _generate_single_file_entries(self, cell_name: str, view_type: str,
                                      files: List[Path], view_config: Dict) -> List[str]:
        """
        生成单文件格式的条目
        
        实际格式：
        set LIBRARY(cell_name,ccs_lvf,cell_name,category,pvt_corner,file_type) {/path/to/file.lib.gz}
        
        例如：
        # normal 类别
        set LIBRARY(sa08nvghlogl22hsp068f,ccs_lvf,sa08nvghlogl22hsp068f,normal,ffpg0p825v125c,lib) {
            /tech_1/designkit/Samsung/LN08LPU_GP/library/.../sa08nvghlogl22hsp068f_ffpg0p825v125c.lib.gz
        }
        
        # udlvl 类别
        set LIBRARY(sa08nvghlogl22hsp068f,ccs_lvf,sa08nvghlogl22hsp068f,udlvl,ffp-0p9v125c,lib) {
            /tech_1/designkit/Samsung/LN08LPU_GP/library/.../sa08nvghlogl22hsp068f_udlvl_ffp-0p9v125c.lib.gz
        }
        """
        entries = []
        
        # 已知的类别标识列表（可根据实际情况扩展）
        CATEGORY_KEYWORDS = ['udlvl', 'normal']  # 可以添加更多类别
        
        for file_path in files:
            filename = file_path.name
            file_path_normalized = self._normalize_path(file_path)
            
            # 提取 category、PVT corner 和文件类型
            category = 'normal'  # 默认值
            pvt_corner = None
            file_type = None
            
            if view_config.get('extract_pvt'):
                # 去掉压缩扩展名（.gz, .bz2 等）
                base_name = filename
                for comp_ext in ['.gz', '.bz2', '.xz', '.z']:
                    if base_name.endswith(comp_ext):
                        base_name = base_name[:-len(comp_ext)]
                        break
                
                # 提取文件类型（最后一个扩展名，去掉点）
                if '.' in base_name:
                    file_type = base_name.split('.')[-1]  # lib, db 等
                    name_without_ext = '.'.join(base_name.split('.')[:-1])
                else:
                    file_type = base_name
                    name_without_ext = base_name
                
                # 检查文件名中是否包含类别标识（如 udlvl）
                # 文件名格式可能是：
                # 1. {cell_name}_{category}_{pvt_corner}.{ext}  (如 sa08nvghlogl22hsp068f_udlvl_ffp-0p9v125c.lib.gz)
                # 2. {cell_name}_{pvt_corner}.{ext}  (如 sa08nvghlogl22hsp068f_ffpg0p825v125c.lib.gz)
                
                if name_without_ext.startswith(cell_name + '_'):
                    remaining = name_without_ext[len(cell_name) + 1:]  # 去掉 "cell_name_"
                    
                    # 检查是否包含类别标识
                    found_category = False
                    for cat_keyword in CATEGORY_KEYWORDS:
                        if cat_keyword != 'normal' and remaining.startswith(cat_keyword + '_'):
                            category = cat_keyword
                            # 提取 PVT corner（去掉 category_）
                            pvt_corner = remaining[len(cat_keyword) + 1:]
                            found_category = True
                            break
                    
                    # 如果没有找到特殊类别，默认为 normal，剩余部分就是 PVT corner
                    if not found_category:
                        category = 'normal'
                        pvt_corner = remaining
                else:
                    # 如果格式不匹配，尝试其他方式
                    # 假设 PVT corner 在最后一个下划线之后
                    if '_' in name_without_ext:
                        parts = name_without_ext.split('_')
                        # 检查倒数第二部分是否是类别标识
                        if len(parts) >= 3 and parts[-2] in CATEGORY_KEYWORDS:
                            category = parts[-2]
                            pvt_corner = parts[-1]
                        else:
                            pvt_corner = parts[-1]
                    else:
                        pvt_corner = name_without_ext
            
            # 如果提取失败，使用默认值
            if not pvt_corner:
                pvt_corner = filename
            if not file_type:
                # 从扩展名推断文件类型
                if filename.endswith('.db'):
                    file_type = 'db'
                elif filename.endswith('.lib') or filename.endswith('.lib.gz'):
                    file_type = 'lib'
                else:
                    file_type = 'unknown'
            
            # 生成条目
            # 格式：LIBRARY(cell_name,view_type,cell_name,category,pvt_corner,file_type)
            key = f"{cell_name},{view_type},{cell_name},{category},{pvt_corner},{file_type}"
            entries.append(f"set {self.array_name}({key}) {{{file_path_normalized}}}")
        
        return entries
    
    def _generate_smic_format(self, lib_info: LibInfo, view_files: Dict[str, any], 
                              adapter: object) -> List[str]:
        """
        生成SMIC格式的lib_config.tcl条目
        
        SMIC格式：
        - set LIBRARY(cell_name,rc_corner,libcorner,file_type) {path}
        
        注意：infoMap 映射在工具内部处理，不需要写入文件
        
        Args:
            lib_info: 库信息
            view_files: {view_type: files_or_structure} 字典
                - 对于SMIC，view_files可能包含特殊结构：
                  - 'root': Path (根目录)
                  - 'pvt_dirs': {pvt_name: Path} (PVT子目录)
            adapter: SMICAdapter实例
        """
        entries = []
        cell_name = lib_info.lib_name
        
        # 处理根目录下的文件
        if 'root' in view_files:
            root_path = view_files['root']
            if isinstance(root_path, Path):
                # 处理根目录下的文件
                for file_path in root_path.iterdir():
                    if file_path.is_file():
                        file_name = file_path.name
                        file_path_normalized = self._normalize_path(file_path)
                        
                        # Handle .plef files -> lef
                        if file_name.endswith('.plef'):
                            entries.append(f"set {self.array_name}({cell_name},lef) {{{file_path_normalized}}}")
                        
                        # Handle .cir files -> cdl
                        elif file_name.endswith('.cir'):
                            entries.append(f"set {self.array_name}({cell_name},cdl) {{{file_path_normalized}}}")
                        
                        # Handle .gds files -> gds
                        elif file_name.endswith('.gds'):
                            entries.append(f"set {self.array_name}({cell_name},gds) {{{file_path_normalized}}}")
        
        # 处理PVT子目录下的文件
        if 'pvt_dirs' in view_files:
            pvt_dirs = view_files['pvt_dirs']
            if isinstance(pvt_dirs, dict):
                for pvt_name, pvt_dir in pvt_dirs.items():
                    # 提取rc_corner和libcorner
                    rc_corner = adapter.extract_rc_corner(pvt_name)
                    libcorner = adapter.map_pvt_to_libcorner(pvt_name)
                    
                    # 处理该PVT目录下的文件
                    for file_path in pvt_dir.iterdir():
                        if file_path.is_file():
                            file_name = file_path.name
                            file_path_normalized = self._normalize_path(file_path)
                            
                            # Handle .lib files
                            if file_name.endswith('.lib'):
                                entries.append(
                                    f"set {self.array_name}({cell_name},{rc_corner},{libcorner},lib) "
                                    f"{{{file_path_normalized}}}"
                                )
                            
                            # Handle .db files
                            elif file_name.endswith('.db'):
                                entries.append(
                                    f"set {self.array_name}({cell_name},{rc_corner},{libcorner},db) "
                                    f"{{{file_path_normalized}}}"
                                )
        
        # 注意：infoMap 映射在工具内部处理，不需要写入 lib_config.tcl
        
        return entries
    
    def _normalize_path(self, file_path: Path) -> str:
        """
        规范化文件路径
        
        转换为绝对路径，并使用正斜杠（Tcl兼容）
        """
        abs_path = file_path.resolve()
        # 转换为正斜杠（Tcl使用正斜杠）
        return str(abs_path).replace('\\', '/')

