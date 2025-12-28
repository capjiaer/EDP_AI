#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP LibKit GUI - 图形用户界面

轻量级的GUI界面，让用户无需查看文档即可使用工具。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import sys
import logging
from typing import List, Optional

# 支持直接运行和作为模块导入
def _is_valid_library_directory(lib_path: Path, adapter, lib_type: str) -> bool:
    """
    检查目录是否是有效的库目录
    
    直接使用适配器的 find_view_directories 方法来检测，这样最准确。
    
    Args:
        lib_path: 要检查的目录路径
        adapter: FoundryAdapter 实例
        lib_type: 库类型（STD/IP/MEM）
        
    Returns:
        如果是有效的库目录返回 True，否则返回 False
    """
    if not lib_path.exists() or not lib_path.is_dir():
        return False
    
    try:
        # 直接使用适配器的方法来查找视图目录
        # 这是最准确的方式，因为它使用了和实际处理相同的逻辑
        view_dirs = adapter.find_view_directories(lib_path, lib_type)
        # 如果找到至少2个视图目录，认为是有效的库目录
        return len(view_dirs) >= 2
    except Exception:
        # 如果查找过程中出错，认为不是有效的库目录
        return False


def _find_library_directories(parent_path: Path, adapter, lib_type: str) -> List[Path]:
    """
    在父目录下查找所有有效的库目录
    
    Args:
        parent_path: 父目录路径
        adapter: FoundryAdapter 实例
        lib_type: 库类型（STD/IP/MEM）
        
    Returns:
        找到的库目录路径列表
    """
    library_dirs = []
    
    # 首先检查父目录本身是否直接包含视图目录（不是通过子目录找到的）
    # 获取视图类型列表
    view_types = adapter.get_standard_view_types(lib_type)
    if not view_types:
        view_types = ['gds', 'lef', 'liberty', 'verilog']
    
    # 检查父目录是否直接包含视图目录
    has_direct_views = False
    for view_type in view_types[:3]:  # 只检查前3个常见的
        if (parent_path / view_type).exists() and (parent_path / view_type).is_dir():
            has_direct_views = True
            break
    
    if has_direct_views:
        # 父目录本身是库目录
        return [parent_path]
    
    # 父目录不是库目录，检查子目录
    if parent_path.exists() and parent_path.is_dir():
        for item in parent_path.iterdir():
            if item.is_dir():
                # 检查子目录是否是库目录
                if _is_valid_library_directory(item, adapter, lib_type):
                    library_dirs.append(item)
    
    return sorted(library_dirs)

# 支持直接运行和作为模块导入
try:
    from .foundry_adapters import AdapterFactory
    from .generator import LibConfigGenerator
except ImportError:
    # 直接运行时，添加路径
    import os
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent.parent.parent
    sys.path.insert(0, str(parent_dir))
    from edp_center.packages.edp_libkit.foundry_adapters import AdapterFactory
    from edp_center.packages.edp_libkit.generator import LibConfigGenerator


class LibKitGUI:
    """EDP LibKit 图形用户界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("EDP LibKit - 库配置生成工具")
        self.root.geometry("800x700")
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建主框架
        self._create_widgets()
        
        # 初始化foundry和node列表
        self._load_foundries()
    
    def _create_widgets(self):
        """创建GUI组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 标题
        title_label = ttk.Label(main_frame, text="EDP LibKit - 库配置生成工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # Foundry选择
        ttk.Label(main_frame, text="Foundry:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.foundry_var = tk.StringVar()
        self.foundry_combo = ttk.Combobox(main_frame, textvariable=self.foundry_var, 
                                          state='readonly', width=30)
        self.foundry_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.foundry_combo.bind('<<ComboboxSelected>>', self._on_foundry_changed)
        row += 1
        
        # Node选择
        ttk.Label(main_frame, text="工艺节点:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.node_var = tk.StringVar()
        self.node_combo = ttk.Combobox(main_frame, textvariable=self.node_var, 
                                       state='readonly', width=30)
        self.node_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # 库类型选择
        ttk.Label(main_frame, text="库类型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.lib_type_var = tk.StringVar(value="STD")
        lib_type_frame = ttk.Frame(main_frame)
        lib_type_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(lib_type_frame, text="STD", variable=self.lib_type_var, 
                       value="STD").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(lib_type_frame, text="IP", variable=self.lib_type_var, 
                       value="IP").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(lib_type_frame, text="MEM", variable=self.lib_type_var, 
                       value="MEM").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # 库路径选择（单个）
        ttk.Label(main_frame, text="库路径:").grid(row=row, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        self.lib_path_var = tk.StringVar()
        self.lib_path_entry = ttk.Entry(path_frame, textvariable=self.lib_path_var, width=40)
        self.lib_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(path_frame, text="浏览...", command=self._browse_lib_path).grid(row=0, column=1)
        row += 1
        
        # 批量路径选择
        ttk.Label(main_frame, text="批量路径:").grid(row=row, column=0, sticky=tk.W, pady=5)
        batch_frame = ttk.Frame(main_frame)
        batch_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        batch_frame.columnconfigure(0, weight=1)
        
        self.batch_paths_text = scrolledtext.ScrolledText(batch_frame, height=3, width=40)
        self.batch_paths_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(batch_frame, text="从文件读取", command=self._load_paths_from_file).grid(row=0, column=1)
        row += 1
        
        ttk.Label(main_frame, text="(每行一个路径，留空则使用上面的单个路径)", 
                 font=('Arial', 8)).grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=row, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40)
        self.output_dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="浏览...", command=self._browse_output_dir).grid(row=0, column=1)
        row += 1
        
        # 版本选择
        ttk.Label(main_frame, text="版本选择:").grid(row=row, column=0, sticky=tk.W, pady=5)
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        self.version_mode_var = tk.StringVar(value="latest")
        ttk.Radiobutton(version_frame, text="最新版本", variable=self.version_mode_var, 
                       value="latest").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(version_frame, text="指定版本", variable=self.version_mode_var, 
                       value="specific").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(version_frame, text="所有版本", variable=self.version_mode_var, 
                       value="all").pack(side=tk.LEFT, padx=5)
        
        self.version_entry = ttk.Entry(version_frame, width=15)
        self.version_entry.pack(side=tk.LEFT, padx=5)
        self.version_entry.insert(0, "如: 1.00B")
        self.version_entry.config(state='disabled')
        
        self.version_mode_var.trace('w', self._on_version_mode_changed)
        row += 1
        
        # 执行按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.generate_button = ttk.Button(button_frame, text="生成配置", 
                                          command=self._generate_config, width=20)
        self.generate_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="清空", command=self._clear_all, width=15).pack(side=tk.LEFT, padx=10)
        row += 1
        
        # 日志输出区域
        ttk.Label(main_frame, text="执行日志:").grid(row=row, column=0, columnspan=3, 
                                                      sticky=tk.W, pady=(10, 5))
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
        # 配置日志输出到GUI（避免重复配置）
        if not any(isinstance(h, type(self.log_text)) for h in logging.getLogger().handlers):
            self._setup_logging()
    
    def _setup_logging(self):
        """配置日志输出到GUI"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                             datefmt='%H:%M:%S'))
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def _load_foundries(self):
        """加载支持的foundry列表"""
        try:
            foundries = AdapterFactory.get_supported_foundries()
            self.foundry_combo['values'] = foundries
            if foundries:
                self.foundry_var.set(foundries[0])
                self._on_foundry_changed()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载foundry列表: {e}")
    
    def _on_foundry_changed(self, event=None):
        """当foundry改变时，更新node列表"""
        foundry = self.foundry_var.get()
        if not foundry:
            return
        
        try:
            adapter = AdapterFactory.create_adapter(foundry)
            nodes = adapter.get_supported_nodes()
            self.node_combo['values'] = nodes
            if nodes:
                self.node_var.set(nodes[0])
        except Exception as e:
            logging.error(f"无法加载节点列表: {e}")
    
    def _on_version_mode_changed(self, *args):
        """当版本选择模式改变时"""
        mode = self.version_mode_var.get()
        if mode == 'specific':
            self.version_entry.config(state='normal')
            if self.version_entry.get() == "如: 1.00B":
                self.version_entry.delete(0, tk.END)
        else:
            self.version_entry.config(state='disabled')
            if not self.version_entry.get():
                self.version_entry.insert(0, "如: 1.00B")
    
    def _browse_lib_path(self):
        """浏览选择库路径"""
        path = filedialog.askdirectory(title="选择库目录")
        if path:
            self.lib_path_var.set(path)
    
    def _browse_output_dir(self):
        """浏览选择输出目录"""
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir_var.set(path)
    
    def _load_paths_from_file(self):
        """从文件读取路径列表"""
        file_path = filedialog.askopenfilename(
            title="选择路径列表文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    paths = [line.strip() for line in f if line.strip()]
                    self.batch_paths_text.delete('1.0', tk.END)
                    self.batch_paths_text.insert('1.0', '\n'.join(paths))
            except Exception as e:
                messagebox.showerror("错误", f"无法读取文件: {e}")
    
    def _clear_all(self):
        """清空所有输入"""
        self.lib_path_var.set("")
        self.batch_paths_text.delete('1.0', tk.END)
        self.output_dir_var.set("")
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, "如: 1.00B")
        self.version_mode_var.set("latest")
        self.log_text.delete('1.0', tk.END)
    
    def _get_lib_paths(self) -> List[str]:
        """获取库路径列表"""
        # 先检查批量路径
        batch_text = self.batch_paths_text.get('1.0', tk.END).strip()
        if batch_text:
            paths = [line.strip() for line in batch_text.split('\n') if line.strip()]
            if paths:
                return paths
        
        # 如果没有批量路径，使用单个路径
        single_path = self.lib_path_var.get().strip()
        if single_path:
            return [single_path]
        
        return []
    
    def _generate_config(self):
        """生成配置文件"""
        # 验证输入
        foundry = self.foundry_var.get()
        node = self.node_var.get()
        lib_type = self.lib_type_var.get()
        output_dir = self.output_dir_var.get().strip()
        lib_paths = self._get_lib_paths()
        
        if not foundry:
            messagebox.showerror("错误", "请选择Foundry")
            return
        
        if not node:
            messagebox.showerror("错误", "请选择工艺节点")
            return
        
        if not lib_paths:
            messagebox.showerror("错误", "请选择至少一个库路径")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        # 在新线程中执行，避免GUI冻结
        self.generate_button.config(state='disabled')
        self.log_text.delete('1.0', tk.END)
        
        thread = threading.Thread(target=self._do_generate, 
                                  args=(foundry, node, lib_type, lib_paths, output_dir))
        thread.daemon = True
        thread.start()
    
    def _do_generate(self, foundry: str, node: str, lib_type: str, 
                     lib_paths: List[str], output_dir: str):
        """实际执行生成（在后台线程中）"""
        try:
            logging.info(f"开始生成配置...")
            logging.info(f"Foundry: {foundry}, Node: {node}, 库类型: {lib_type}")
            logging.info(f"库路径数量: {len(lib_paths)}")
            logging.info(f"输出目录: {output_dir}")
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 确定版本模式
            version_mode = self.version_mode_var.get()
            version = None
            all_versions = False
            
            if version_mode == 'specific':
                version = self.version_entry.get().strip()
                if version and version != "如: 1.00B":
                    logging.info(f"使用指定版本: {version}")
                else:
                    version = None
            elif version_mode == 'all':
                all_versions = True
                logging.info("处理所有版本")
            
            # 创建生成器（ori_path可以是任意路径，因为我们现在直接指定lib_path）
            generator = LibConfigGenerator(
                foundry=foundry,
                ori_path=Path(lib_paths[0]).parent if lib_paths else Path('.'),
                output_base_dir=output_path,
                node=node
            )
            
            # 创建适配器用于检测库目录
            try:
                adapter = AdapterFactory.create_adapter(foundry, node)
            except Exception as e:
                logging.error(f"无法创建适配器: {e}")
                self.generate_button.config(state='normal')
                return
            
            # 展开安装目录（通过检测视图目录）
            expanded_lib_paths = []
            for lib_path_str in lib_paths:
                lib_path = Path(lib_path_str)
                if not lib_path.exists():
                    logging.error(f"路径不存在: {lib_path}")
                    continue
                if not lib_path.is_dir():
                    logging.error(f"路径不是目录: {lib_path}")
                    continue
                
                # 使用辅助函数查找库目录
                library_dirs = _find_library_directories(lib_path, adapter, lib_type)
                
                if len(library_dirs) > 1:
                    # 这是安装目录，包含多个库
                    logging.info(f"检测到安装目录，包含 {len(library_dirs)} 个子库:")
                    for lib_dir in library_dirs:
                        logging.info(f"  - {lib_dir.name}")
                    expanded_lib_paths.extend(library_dirs)
                elif len(library_dirs) == 1:
                    # 只有一个库目录，直接使用
                    expanded_lib_paths.append(library_dirs[0])
                else:
                    # 没有找到库目录，可能是路径本身就是一个库目录（但检查失败）
                    # 或者路径层级不对，直接使用原路径（让后续处理报错）
                    logging.warning(f"未在 {lib_path} 下找到有效的库目录，尝试直接使用该路径")
                    expanded_lib_paths.append(lib_path)
            
            if not expanded_lib_paths:
                logging.error("没有找到任何库目录")
                self.generate_button.config(state='normal')
                return
            
            if len(expanded_lib_paths) != len(lib_paths):
                logging.info(f"展开后待处理库数量: {len(expanded_lib_paths)}")
            
            success_count = 0
            error_count = 0
            
            # 处理每个库路径
            for lib_path in expanded_lib_paths:
                try:
                    logging.info(f"\n处理库: {lib_path.name}")
                    
                    if all_versions:
                        # 处理所有版本
                        generated_files = generator.generate_all_versions(lib_path, lib_type)
                    else:
                        # 处理单个版本（最新或指定）
                        generated_files = generator.generate_from_directory(
                            lib_path, lib_type, version=version
                        )
                    
                    if generated_files:
                        logging.info(f"✓ 成功生成 {len(generated_files)} 个配置文件")
                        for file_path in generated_files:
                            logging.info(f"  - {file_path}")
                        success_count += 1
                    else:
                        logging.warning(f"⚠ 未生成任何文件")
                        error_count += 1
                        
                except Exception as e:
                    logging.error(f"✗ 处理失败: {e}", exc_info=True)
                    error_count += 1
            
            # 显示完成消息
            self.root.after(0, lambda: self._show_completion(success_count, error_count))
            
        except Exception as e:
            logging.error(f"生成过程出错: {e}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("错误", f"生成失败: {e}"))
        finally:
            self.root.after(0, lambda: self.generate_button.config(state='normal'))
    
    def _show_completion(self, success_count: int, error_count: int):
        """显示完成消息"""
        message = f"生成完成！\n\n成功: {success_count} 个\n失败: {error_count} 个"
        if error_count == 0:
            messagebox.showinfo("完成", message)
        else:
            messagebox.showwarning("完成", message)


def main():
    """GUI主入口"""
    root = tk.Tk()
    app = LibKitGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

