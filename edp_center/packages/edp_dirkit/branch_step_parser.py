#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分支步骤解析模块
"""

from typing import Tuple


class BranchStepParser:
    """分支步骤解析器"""
    
    @staticmethod
    def parse_from_branch_step(from_branch_step: str, 
                               current_user: str) -> Tuple[str, str, str]:
        """
        解析 from_branch_step 参数
        
        支持的格式（注意：step_name 格式为 'tool.step'，如 'pnr_innovus.init'，
                      对应目录结构 runs/tool/step/）：
        1. 'branch_name.step_name' - 从当前用户的指定分支复制
           例如：'branch1.pnr_innovus.init'
           解析为：user=current_user, branch=branch1, step=pnr_innovus.init
           对应目录：runs/pnr_innovus/init/
        2. 'user_name.branch_name.step_name' - 从指定用户的指定分支复制
           例如：'zhangsan.branch1.pnr_innovus.init'
           解析为：user=zhangsan, branch=branch1, step=pnr_innovus.init
           对应目录：runs/pnr_innovus/init/
        
        解析规则：
        - 步骤名称（step_name）格式为 'tool.step'（如 pnr_innovus.init）
        - 对应目录结构：runs/tool/step/（如 runs/pnr_innovus/init/）
        - 统计点号数量：
          - 如果只有1个点号：格式是 branch_name.step_name（step_name 不含点号，这是错误的，因为 step_name 必须包含工具和步骤）
          - 如果有2个点号：格式是 branch_name.tool.step（如 branch1.pnr_innovus.init）
          - 如果有3个或更多点号：格式是 user_name.branch_name.tool.step（如 zhangsan.branch1.pnr_innovus.init）
        - 简单规则：从左往右找到第一个点号，分离出第一部分。如果剩余部分还有点号，
          则尝试将剩余部分的第一个点号作为 branch_name 和 step_name 的分界。
        
        Args:
            from_branch_step: 源分支步骤字符串
            current_user: 当前用户名
            
        Returns:
            (source_user, source_branch, step_name) 元组
            
        Raises:
            ValueError: 如果格式不正确
        """
        # 统计点号数量
        dot_count = from_branch_step.count('.')
        
        if dot_count == 0:
            raise ValueError(
                f"from_branch_step 格式不正确: {from_branch_step}\n"
                f"必须包含至少一个点号，格式: 'branch_name.step_name' 或 'user_name.branch_name.step_name'"
            )
        
        # 从左往右找第一个点号
        first_dot_idx = from_branch_step.find('.')
        first_part = from_branch_step[:first_dot_idx]
        remaining = from_branch_step[first_dot_idx + 1:]
        
        if dot_count == 1:
            # 只有一个点号：格式是 branch_name.step_name
            source_user = current_user
            source_branch = first_part
            step_name = remaining
        else:
            # 有多个点号：需要判断是 branch_name.step_name 还是 user_name.branch_name.step_name
            # 规则：如果 remaining 中还有至少一个点号，尝试将第一个点号作为 branch_name 和 step_name 的分界
            second_dot_idx = remaining.find('.')
            
            if second_dot_idx == -1:
                # 这不应该发生，因为 dot_count >= 2
                raise ValueError(f"格式解析错误: {from_branch_step}")
            
            # 尝试两种格式：
            # 1. branch_name.step_name（remaining 的第一个点号是 step_name 内部）
            # 2. user_name.branch_name.step_name（remaining 的第一个点号是 branch_name 和 step_name 的分界）
            
            # 由于我们无法准确判断，我们采用启发式方法：
            # 如果 dot_count == 2，尝试解析为 user_name.branch_name.step_name
            # 如果 dot_count >= 3，第一个点号前是 user_name，剩余部分的第一个点号前是 branch_name，后面是 step_name
            
            if dot_count == 2:
                # 两个点号：默认按 branch_name.step_name 解析（step_name 含1个点号）
                # 例如：branch1.pnr_innovus.init -> branch=branch1, step=pnr_innovus.init
                source_user = current_user
                source_branch = first_part
                step_name = remaining
            else:
                # 三个或更多点号：格式是 user_name.branch_name.step_name（step_name 含多个点号）
                # 例如：zhangsan.branch1.pnr_innovus.init -> user=zhangsan, branch=branch1, step=pnr_innovus.init
                source_user = first_part
                source_branch = remaining[:second_dot_idx]
                step_name = remaining[second_dot_idx + 1:]
        
        return source_user, source_branch, step_name

