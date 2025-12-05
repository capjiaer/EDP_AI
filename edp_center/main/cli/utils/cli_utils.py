#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI 工具函数
"""

import os
import stat
from pathlib import Path

# 从 edp_dirkit 导入 get_current_user，避免重复实现
try:
    from edp_center.packages.edp_dirkit import get_current_user
except ImportError:
    # 如果无法导入，使用本地实现（向后兼容）
    def get_current_user() -> str:
        """获取当前用户名"""
        import getpass
        
        # 尝试多个环境变量
        for env_var in ['USER', 'USERNAME', 'LOGNAME']:
            user = os.environ.get(env_var)
            if user:
                return user
        
        # 如果都获取不到，尝试系统默认
        try:
            return getpass.getuser()
        except Exception:
            return "unknown_user"


def set_user_directory_permissions(user_path: Path, username: str) -> bool:
    """
    设置用户目录权限，确保只有对应的用户可以修改
    
    在 Unix/Linux 系统上，设置目录权限为 755 (rwxr-xr-x)：
    - 所有者（对应的 user）：rwx (读、写、执行)
    - 同组用户：r-x (读、执行，不可写)
    - 其他用户：r-x (读、执行，不可写)
    
    这样其他用户可以读取该用户的目录，但不能修改。
    
    在 Windows 系统上，提示用户手动设置权限。
    
    Args:
        user_path: 用户目录路径
        username: 用户名
        
    Returns:
        成功返回 True，失败返回 False
    """
    if os.name == 'nt':  # Windows 系统
        # Windows 系统上，目录权限由文件系统 ACL 管理，通常不需要手动设置
        # 默认情况下，用户只能访问自己的目录，这是 Windows 的正常行为
        # 如果需要共享访问，可以在 Windows 资源管理器中手动设置权限
        return False
    
    try:
        import pwd
        import grp
        
        # 获取用户和组信息
        try:
            user_info = pwd.getpwnam(username)
            uid = user_info.pw_uid
            gid = user_info.pw_gid
        except KeyError:
            # 如果找不到用户，使用当前用户
            user_info = pwd.getpwuid(os.getuid())
            uid = user_info.pw_uid
            gid = user_info.pw_gid
        
        # 设置所有者和组
        os.chown(user_path, uid, gid)
        
        # 设置权限为 755 (rwxr-xr-x)
        # stat.S_IRWXU: 所有者读写执行 (0o700)
        # stat.S_IRGRP: 组读 (0o040)
        # stat.S_IXGRP: 组执行 (0o010)
        # stat.S_IROTH: 其他读 (0o004)
        # stat.S_IXOTH: 其他执行 (0o001)
        # 总计: 0o755
        mode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        user_path.chmod(mode)
        
        return True
    except ImportError:
        # 如果没有 pwd 或 grp 模块（Windows），跳过
        print(f"⚠️  无法设置权限（缺少 pwd/grp 模块），请手动设置 {user_path} 的权限", file=os.sys.stderr)
        return False
    except Exception as e:
        print(f"⚠️  设置权限失败: {e}", file=os.sys.stderr)
        return False

