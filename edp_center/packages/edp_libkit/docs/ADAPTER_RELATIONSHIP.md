# Adapter 文件关系说明

## 三个文件的关系

```
┌─────────────────────────────────────────────────────────────┐
│              interface.py                                  │
│                                                             │
│  BaseFoundryAdapter (抽象基类)                              │
│  - 定义接口                                                 │
│  - find_view_directories() [抽象方法]                      │
│  - extract_lib_info() [抽象方法]                           │
│  - get_view_file_pattern() [默认实现]                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ 继承
               │
       ┌───────┴────────┐
       │                │
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────────────┐
│ foundry_     │  │ node_adapter.py      │
│ adapter.py   │  │                      │
│              │  │                      │
│ FoundryAdapter│  │ BaseNodeAdapter      │
│              │  │                      │
│ - 代理模式   │  │ - 实际执行者         │
│ - 统一入口   │  │ - 实现所有功能       │
│              │  │ - YAML配置驱动        │
│              │  │                      │
│ 内部持有：   │  │                      │
│ _node_adapter│  │                      │
│ (BaseNode    │  │                      │
│  Adapter)    │  │                      │
└──────────────┘  └──────────────────────┘
       │                │
       │                │
       └───────┬────────┘
               │
               │ 委托/代理
               │
               ▼
       实际执行工作
```

## 详细说明

### 1. interface.py - 接口定义层

**作用**：定义适配器接口（抽象基类）

**内容**：
```python
class BaseFoundryAdapter(ABC):
    """Foundry适配器基类"""
    
    @abstractmethod
    def find_view_directories(...) -> Dict[str, Path]:
        """查找视图目录 - 抽象方法，必须实现"""
        pass
    
    @abstractmethod
    def extract_lib_info(...) -> LibInfo:
        """提取库信息 - 抽象方法，必须实现"""
        pass
    
    def get_view_file_pattern(...) -> str:
        """获取文件模式 - 默认实现"""
        return patterns.get(view_type, '*')
```

**特点**：
- ✅ 使用 `ABC`（抽象基类）定义接口
- ✅ 抽象方法必须被子类实现
- ✅ 提供默认实现（`get_view_file_pattern`）

### 2. foundry_adapter.py - 代理层

**作用**：统一入口，代理/委托给节点适配器

**内容**：
```python
class FoundryAdapter(BaseFoundryAdapter):
    """统一的foundry适配器"""
    
    def __init__(self, foundry: str, node: Optional[str] = None):
        self.foundry = foundry
        self.node = node
        self._node_adapter = None  # 内部持有节点适配器
        
        if self.node:
            self._load_node_adapter()  # 动态加载节点适配器
    
    def _load_node_adapter(self):
        """动态加载节点适配器"""
        if self.foundry in ['samsung', 'smic', 'tsmc']:
            from .node_adapter import BaseNodeAdapter
            self._node_adapter = BaseNodeAdapter(self.foundry, self.node)
    
    def find_view_directories(self, lib_path, lib_type, version):
        """查找视图目录 - 委托给节点适配器"""
        if self._node_adapter:
            return self._node_adapter.find_view_directories(lib_path, lib_type, version)
        else:
            raise RuntimeError("无法加载节点适配器")
    
    def extract_lib_info(self, lib_path):
        """提取库信息 - 委托给节点适配器"""
        if self._node_adapter:
            return self._node_adapter.extract_lib_info(lib_path)
        else:
            return LibInfo(...)  # 默认实现
```

**特点**：
- ✅ **代理模式**：所有方法都委托给 `_node_adapter` 执行
- ✅ **统一入口**：外部代码只需要知道 `FoundryAdapter`
- ✅ **动态加载**：根据 foundry 和 node 动态加载对应的节点适配器
- ✅ **向后兼容**：支持从节点目录加载自定义适配器

### 3. node_adapter.py - 实现层

**作用**：实际执行工作的适配器

**内容**：
```python
class BaseNodeAdapter(BaseFoundryAdapter):
    """通用节点适配器基类"""
    
    def __init__(self, foundry: str, node_key: str):
        self.foundry = foundry
        self.node_key = node_key
        self._load_node_config()  # 从YAML加载配置
    
    def find_view_directories(self, lib_path, lib_type, version):
        """查找视图目录 - 实际实现"""
        # 根据 lib_type 使用不同的查找逻辑
        if lib_type == 'STD':
            return self._find_std_view_directories(lib_path, version)
        elif lib_type == 'IP':
            return self._find_ip_view_directories(lib_path, version)
        elif lib_type == 'MEM':
            return self._find_mem_view_directories(lib_path, version)
    
    def extract_lib_info(self, lib_path):
        """提取库信息 - 实际实现"""
        # 从路径提取库名称、版本等信息
        lib_name = self._extract_lib_name(lib_path)
        version = self._extract_version(lib_path)
        return LibInfo(...)
    
    def get_view_file_pattern(self, view_type):
        """获取文件模式 - 从YAML配置读取"""
        return self.view_file_patterns.get(view_type, ['*'])
```

**特点**：
- ✅ **实际实现**：包含所有核心功能的实现
- ✅ **配置驱动**：从YAML配置文件加载节点配置
- ✅ **通用实现**：所有foundry共享同一个实现，通过 `foundry` 参数区分

## 工作流程

### 示例：查找视图目录

```
1. 用户调用：
   adapter = FoundryAdapter('samsung', 'ln08lpu_gp')
   adapter.find_view_directories(lib_path, 'STD', version='2.00A')

2. FoundryAdapter.find_view_directories() 被调用
   └─> 检查 self._node_adapter 是否存在
       └─> 如果存在，委托给 self._node_adapter.find_view_directories()

3. BaseNodeAdapter.find_view_directories() 被调用
   └─> 根据 lib_type='STD'，调用 self._find_std_view_directories()
       └─> 从YAML配置读取 standard_view_types['STD']
       └─> 递归查找视图目录
       └─> 返回结果

4. 结果返回给用户
```

## 为什么这样设计？

### 1. 分离关注点

- **interface.py**：定义接口，不关心实现细节
- **foundry_adapter.py**：统一入口，不关心具体实现
- **node_adapter.py**：实际实现，不关心如何被调用

### 2. 代理模式的优势

- **统一接口**：外部代码只需要知道 `FoundryAdapter`
- **灵活扩展**：可以动态加载不同的节点适配器
- **向后兼容**：支持自定义适配器（从节点目录加载）

### 3. 配置驱动

- **易于维护**：添加新节点只需创建YAML配置文件
- **统一实现**：所有foundry共享同一个实现
- **易于扩展**：通过配置区分不同foundry的特殊处理

## 继承关系

```
BaseFoundryAdapter (抽象基类)
    │
    ├── FoundryAdapter (代理层)
    │   └── 内部持有 BaseNodeAdapter 实例
    │   └── 所有方法委托给 _node_adapter
    │
    └── BaseNodeAdapter (实现层)
        └── 实现所有核心功能
        └── 从YAML配置加载节点配置
```

## 总结

**三个文件的关系**：

1. **interface.py** - 接口定义（抽象基类）
   - 定义适配器必须实现的接口
   - 提供默认实现（可选）

2. **foundry_adapter.py** - 代理层（统一入口）
   - 继承自 `BaseFoundryAdapter`
   - 内部持有 `BaseNodeAdapter` 实例
   - 所有方法委托给节点适配器执行

3. **node_adapter.py** - 实现层（实际执行）
   - 继承自 `BaseFoundryAdapter`
   - 实现所有核心功能
   - 从YAML配置加载节点配置

**设计模式**：
- ✅ **代理模式（Proxy Pattern）**：`FoundryAdapter` 代理 `BaseNodeAdapter`
- ✅ **委托模式（Delegation Pattern）**：方法调用委托给内部对象
- ✅ **模板方法模式（Template Method Pattern）**：`BaseFoundryAdapter` 定义接口，子类实现

