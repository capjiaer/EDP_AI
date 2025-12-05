# 公共逻辑提取建议

## 📋 分析结果

通过代码审查，发现以下重复逻辑可以提取为公共模块：

---

## 🔍 发现的重复逻辑

### 1. **项目参数推断逻辑** ⭐ 高优先级

**重复位置**：
- `workflow_web/workflow_loader.py` - `_infer_project_params()`
- `workflow_web/step_executor.py` - `_prepare_execution_args()`
- `cli.py` - 参数推断逻辑
- `graph_handler.py` - 参数推断逻辑

**重复模式**：
```python
# 模式 1: 创建 Namespace 并设置默认值
args = Namespace()
args.work_path = Path.cwd()
args.project = None
args.foundry = None
args.node = None
args.version = None
args.block = None
args.user = None

# 模式 2: 调用推断函数
success = infer_params_from_version_file(args, manager)
if not success:
    raise ValueError("无法推断项目参数")

# 模式 3: 获取 foundry 和 node
project_info = manager.work_path_initializer.get_project_info(
    project, None, None
)
foundry = project_info.get('foundry')
node = project_info.get('node')
```

**建议提取**：
```python
# edp_center/main/cli/utils/param_inference.py

def create_default_args(work_path: Optional[Path] = None) -> Namespace:
    """创建默认参数对象"""
    args = Namespace()
    args.work_path = str(work_path) if work_path else str(Path.cwd())
    args.project = None
    args.foundry = None
    args.node = None
    args.version = None
    args.block = None
    args.user = None
    return args

def infer_all_params(manager: WorkflowManager, 
                     current_dir: Optional[Path] = None,
                     args: Optional[Namespace] = None) -> Dict[str, Any]:
    """
    推断所有项目参数（project, version, block, user, foundry, node）
    
    Returns:
        {
            'project': str,
            'version': str,
            'block': str,
            'user': str,
            'foundry': str,
            'node': str,
            'work_path': Path
        }
    
    Raises:
        ValueError: 如果无法推断必要参数
    """
    if args is None:
        args = create_default_args(current_dir)
    
    # 推断 work_path, project, version, block, user
    success = infer_params_from_version_file(args, manager, current_dir)
    if not success:
        raise ValueError("无法推断项目参数")
    
    # 推断 foundry 和 node
    project_info = manager.work_path_initializer.get_project_info(
        args.project, None, None
    )
    foundry = project_info.get('foundry')
    node = project_info.get('node')
    
    if not foundry or not node:
        raise ValueError("无法推断 foundry 和 node")
    
    return {
        'project': args.project,
        'version': getattr(args, 'version', None),
        'block': args.block,
        'user': args.user,
        'foundry': foundry,
        'node': node,
        'work_path': Path(args.work_path)
    }
```

**使用示例**：
```python
# 重构前
args = Namespace()
args.work_path = Path.cwd()
args.project = None
# ... 更多设置
success = infer_params_from_version_file(args, manager)
if not success:
    raise ValueError("无法推断项目参数")
project_info = manager.work_path_initializer.get_project_info(...)
foundry = project_info.get('foundry')
node = project_info.get('node')

# 重构后
from ..utils.param_inference import infer_all_params
params = infer_all_params(manager)
project, foundry, node = params['project'], params['foundry'], params['node']
```

---

### 2. **路径格式转换** ⭐ 中优先级

**重复位置**：
- `generator.py` - `str(path).replace('\\', '/')` (多处)
- `source_generator.py` - `str(target_file).replace('\\', '/')`
- `source_prepend_processor.py` - `str(rel_path).replace('\\', '/')` (多处)
- `proc_processor.py` - 可能也需要

**重复模式**：
```python
# 将 Windows 路径转换为 Tcl 兼容格式
tcl_path = str(file_path).replace('\\', '/')
```

**建议提取**：
```python
# edp_center/packages/edp_common/path_utils.py

def to_tcl_path(path: Union[str, Path]) -> str:
    """
    将路径转换为 Tcl 兼容格式（使用正斜杠）
    
    Args:
        path: 路径（字符串或 Path 对象）
    
    Returns:
        Tcl 兼容的路径字符串（使用正斜杠）
    
    Example:
        >>> to_tcl_path(Path('C:/Users/test/file.tcl'))
        'C:/Users/test/file.tcl'
        >>> to_tcl_path('C:\\Users\\test\\file.tcl')
        'C:/Users/test/file.tcl'
    """
    if isinstance(path, Path):
        return str(path).replace('\\', '/')
    return str(path).replace('\\', '/')
```

**使用示例**：
```python
# 重构前
tcl_path = str(sub_step_file).replace('\\', '/')

# 重构后
from edp_center.packages.edp_common.path_utils import to_tcl_path
tcl_path = to_tcl_path(sub_step_file)
```

---

### 3. **参数验证模式** ⭐ 中优先级

**重复位置**：
- `config_handler.py` - `get_project_info()` 调用
- `workflow_handler.py` - `get_project_info()` 调用
- `graph_handler.py` - `get_project_info()` 调用

**重复模式**：
```python
project_info = manager.work_path_initializer.get_project_info(
    args.project, args.foundry, args.node
)
foundry = project_info['foundry']
node = project_info['node']
```

**建议提取**：
```python
# edp_center/main/cli/utils/param_inference.py

def get_foundry_node(manager: WorkflowManager, 
                     project: Optional[str] = None,
                     foundry: Optional[str] = None,
                     node: Optional[str] = None) -> Tuple[str, str]:
    """
    获取 foundry 和 node（从参数或推断）
    
    Args:
        manager: WorkflowManager 实例
        project: 项目名称（可选）
        foundry: 代工厂名称（可选，如果提供则直接返回）
        node: 工艺节点（可选，如果提供则直接返回）
    
    Returns:
        (foundry, node) 元组
    
    Raises:
        ValueError: 如果无法获取 foundry 或 node
    """
    if foundry and node:
        return foundry, node
    
    if not project:
        raise ValueError("需要提供 project 参数以推断 foundry 和 node")
    
    project_info = manager.work_path_initializer.get_project_info(
        project, foundry, node
    )
    
    foundry = project_info.get('foundry')
    node = project_info.get('node')
    
    if not foundry or not node:
        raise ValueError(f"无法获取项目 {project} 的 foundry 和 node")
    
    return foundry, node
```

**使用示例**：
```python
# 重构前
project_info = manager.work_path_initializer.get_project_info(
    args.project, args.foundry, args.node
)
foundry = project_info['foundry']
node = project_info['node']

# 重构后
from ..utils.param_inference import get_foundry_node
foundry, node = get_foundry_node(manager, args.project, args.foundry, args.node)
```

---

### 4. **日志文件命名** ⭐ 低优先级

**重复位置**：
- `log_handler.py` - `create_log_file()`
- 可能在其他地方也有类似逻辑

**当前实现**：
```python
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f'{step_name.replace(".", "_")}_{timestamp}.log'
```

**建议提取**：
```python
# edp_center/packages/edp_common/path_utils.py

def sanitize_filename(name: str, max_length: int = 255) -> str:
    """
    清理文件名，移除或替换不安全的字符
    
    Args:
        name: 原始文件名
        max_length: 最大长度
    
    Returns:
        清理后的文件名
    """
    # 替换点号为下划线（用于步骤名称）
    name = name.replace('.', '_')
    # 移除其他不安全字符
    import re
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 限制长度
    if len(name) > max_length:
        name = name[:max_length]
    return name

def generate_log_filename(base_name: str, 
                         extension: str = '.log',
                         timestamp_format: str = '%Y%m%d_%H%M%S') -> str:
    """
    生成日志文件名
    
    Args:
        base_name: 基础名称（如步骤名称）
        extension: 文件扩展名（默认 .log）
        timestamp_format: 时间戳格式
    
    Returns:
        完整的日志文件名
    """
    from datetime import datetime
    timestamp = datetime.now().strftime(timestamp_format)
    safe_name = sanitize_filename(base_name)
    return f'{safe_name}_{timestamp}{extension}'
```

---

### 5. **目录创建模式** ⭐ 低优先级

**重复位置**：
- `log_handler.py` - `create_log_file()` 中的 `log_dir.mkdir(exist_ok=True)`
- `release_file_operations.py` - `target_base.mkdir(parents=True, exist_ok=True)`
- 其他多处

**建议提取**：
```python
# edp_center/packages/edp_common/path_utils.py

def ensure_dir(path: Union[str, Path], parents: bool = True) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        parents: 是否创建父目录
    
    Returns:
        Path 对象
    """
    path = Path(path)
    path.mkdir(parents=parents, exist_ok=True)
    return path
```

---

## 📦 建议创建的公共模块

### 1. `edp_center/main/cli/utils/param_inference.py`

**职责**：
- 统一的参数推断逻辑
- 创建默认参数对象
- 获取 foundry/node

**函数**：
- `create_default_args()` - 创建默认参数
- `infer_all_params()` - 推断所有参数
- `get_foundry_node()` - 获取 foundry/node

### 2. `edp_center/packages/edp_common/path_utils.py`

**职责**：
- 路径格式转换
- 文件名清理
- 目录操作

**函数**：
- `to_tcl_path()` - 转换为 Tcl 路径
- `sanitize_filename()` - 清理文件名
- `generate_log_filename()` - 生成日志文件名
- `ensure_dir()` - 确保目录存在

---

## 🎯 实施优先级

### 高优先级（立即实施）
1. **项目参数推断逻辑** - 重复最多，影响最大
   - 创建 `param_inference.py`
   - 重构 `workflow_loader.py`、`step_executor.py`、`graph_handler.py`

### 中优先级（近期实施）
2. **路径格式转换** - 简单但重复多
   - 创建 `path_utils.py`
   - 重构所有使用 `.replace('\\', '/')` 的地方

3. **参数验证模式** - 与参数推断相关
   - 添加到 `param_inference.py`

### 低优先级（可选）
4. **日志文件命名** - 重复较少
5. **目录创建模式** - 简单，影响小

---

## 📝 实施步骤

### 步骤 1：创建公共模块
1. 创建 `edp_center/main/cli/utils/param_inference.py`
2. 创建 `edp_center/packages/edp_common/path_utils.py`

### 步骤 2：重构使用处
1. 重构 `workflow_web/workflow_loader.py`
2. 重构 `workflow_web/step_executor.py`
3. 重构 `commands/config_handler.py`
4. 重构 `commands/workflow_handler.py`
5. 重构 `commands/graph_handler.py`
6. 重构所有路径转换的地方

### 步骤 3：测试
1. 运行现有测试
2. 添加新模块的单元测试
3. 端到端测试

---

## ✅ 预期效果

1. **代码减少**：预计减少 200-300 行重复代码
2. **可维护性提升**：参数推断逻辑集中管理，修改更容易
3. **一致性提升**：所有地方使用相同的推断逻辑
4. **可测试性提升**：可以单独测试公共逻辑

---

## 🔄 向后兼容

所有提取的函数都保持向后兼容：
- 不改变现有函数签名
- 新函数作为辅助函数，不强制使用
- 可以逐步迁移，不需要一次性重构所有地方

