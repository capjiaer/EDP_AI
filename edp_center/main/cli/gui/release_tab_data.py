"""Data loading and scanning for Release Tab."""

from pathlib import Path
from typing import List, Dict
from datetime import datetime


class ReleaseTabDataLoader:
    """Data loader for Release Tab."""
    
    def __init__(self, release_root: Path = None):
        self.release_root = release_root
        self.releases = []  # List of release info dicts
    
    def scan_releases(self) -> List[Dict]:
        """扫描 RELEASE 目录，查找所有版本"""
        if not self.release_root or not self.release_root.exists():
            self.releases = []
            return []
        
        self.releases = []
        
        # 尝试从 RELEASE 根目录推断 project 和 version
        release_path = self.release_root
        default_project = None
        default_version = None
        
        # 检查路径中是否包含 WORK_PATH/{project}/{version}/RELEASE
        parts = release_path.parts
        if 'WORK_PATH' in parts:
            work_path_idx = parts.index('WORK_PATH')
            if work_path_idx + 2 < len(parts):
                default_project = parts[work_path_idx + 1]
                default_version = parts[work_path_idx + 2]
        
        # 扫描 RELEASE 目录结构: RELEASE/{block}/{user}/{version}/
        # 只扫描标准的三层结构，确保 version 目录下有 data/ 目录
        for block_dir in self.release_root.iterdir():
            if not block_dir.is_dir() or block_dir.name.startswith('.'):
                continue
            
            for user_dir in block_dir.iterdir():
                if not user_dir.is_dir() or user_dir.name.startswith('.'):
                    continue
                
                for version_dir in user_dir.iterdir():
                    if not version_dir.is_dir() or version_dir.name.startswith('.'):
                        continue
                    
                    # 检查是否是有效的 release 版本目录
                    # 必须符合标准 EDP 结构：{block}/{user}/{version}/data/
                    readonly_marker = version_dir / '.readonly'
                    data_dir = version_dir / 'data'
                    
                    # 只处理有 data/ 目录的版本（标准 EDP 结构）
                    if not data_dir.exists():
                        continue
                    
                    # 尝试从工作目录推断 project 和 version（如果可能）
                    project = default_project
                    version = default_version
                    
                    # 尝试从当前工作目录推断（如果用户在某个工作目录下）
                    # 注意：infer_work_path_info 需要 args 和 project_info，这里我们使用底层函数
                    # 底层函数只需要 current_dir，args 和 project_info 可以为 None
                    try:
                        from ...utils.inference.path_inference import infer_work_path_info as infer_work_path_info_func
                        # 创建一个简单的 args 对象（空对象即可）
                        class SimpleArgs:
                            pass
                        args = SimpleArgs()
                        work_path_info = infer_work_path_info_func(Path.cwd(), args, None)
                        if work_path_info:
                            project = work_path_info.get('project') or project
                            version = work_path_info.get('version') or version
                    except Exception:
                        pass
                    
                    # 获取版本信息
                    release_info = {
                        'project': project or 'unknown',
                        'version': version or 'unknown',
                        'block': block_dir.name,
                        'user': user_dir.name,
                        'release_version': version_dir.name,  # release 版本号
                        'path': version_dir,
                        'readonly': readonly_marker.exists(),
                        'created': self.get_directory_creation_time(version_dir),
                        'steps': self.get_release_steps(version_dir)
                    }
                    
                    self.releases.append(release_info)
        
        return self.releases
    
    def get_directory_creation_time(self, dir_path: Path) -> str:
        """获取目录创建时间"""
        try:
            stat = dir_path.stat()
            # 使用修改时间作为创建时间（Windows 上创建时间不可靠）
            dt = datetime.fromtimestamp(stat.st_mtime)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "Unknown"
    
    def get_release_steps(self, version_dir: Path) -> List[str]:
        """获取 release 版本包含的步骤列表"""
        steps = []
        data_dir = version_dir / 'data'
        if data_dir.exists():
            for step_dir in data_dir.iterdir():
                if step_dir.is_dir():
                    steps.append(step_dir.name)
        return sorted(steps)
    
    def auto_detect_release_root(self) -> Path:
        """自动检测 RELEASE 根目录"""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            release_dir = parent / 'RELEASE'
            if release_dir.exists() and release_dir.is_dir():
                self.release_root = release_dir
                return release_dir
        
        # 如果没找到，尝试从当前工作目录推断
        # 假设在 WORK_PATH/{project}/{version}/{block}/{user}/main 下
        try:
            parts = current.parts
            if 'WORK_PATH' in parts:
                work_path_idx = parts.index('WORK_PATH')
                if work_path_idx + 1 < len(parts):
                    work_path_root = Path(*parts[:work_path_idx + 1])
                    release_dir = work_path_root.parent / 'RELEASE'
                    if release_dir.exists():
                        self.release_root = release_dir
                        return release_dir
        except Exception:
            pass
        
        return None

