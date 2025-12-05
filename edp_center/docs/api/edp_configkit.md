# edp_configkit API 文档

## 📋 概述

`edp_configkit` 提供配置文件的加载、合并和转换功能（YAML ↔ Tcl）。

**位置**: `edp_center.packages.edp_configkit`

---

## 核心函数

### `files2dict(*file_paths)`

将多个配置文件合并为一个字典。

**位置**: `edp_center.packages.edp_configkit.configkit.configkit.files2dict`

**参数**:
- `*file_paths` (Union[str, Path]): 配置文件路径（可变参数）

**返回**:
- `Dict[str, Any]`: 合并后的配置字典

**说明**:
- 支持 YAML 和 Tcl 格式
- 后加载的配置会覆盖先加载的配置
- 自动处理数组格式的变量（`flow_name(step_name,key)`）

**示例**:
```python
from edp_center.packages.edp_configkit.configkit.configkit import files2dict

config = files2dict(
    'common/main/config.yaml',
    'common/pv_calibre/config.yaml',
    'dongting/main/config.yaml',
    'dongting/pv_calibre/config.yaml',
    'user_config.yaml'
)
```

---

## 配置转换

### YAML → Tcl

配置文件从 YAML 格式转换为 Tcl 格式（在生成 `full.tcl` 时自动完成）。

**转换规则**:
- 数组格式：`flow_name.step_name.key: value` → `set flow_name(step_name,key) value`
- 嵌套结构：自动展开为数组格式
- 类型转换：自动处理字符串、数字、布尔值

### Tcl → 字典

Tcl 配置文件直接解析为字典（用于配置合并）。

---

## 配置验证

### 变量格式验证

所有配置变量必须是数组格式（带命名空间）：
- ✅ 正确：`pv_calibre(ipmerge,cpu_num)`
- ❌ 错误：`cpu_num`（简单变量）

**验证位置**: `edp_center.main.cli.utils.full_tcl_generator.generate_full_tcl`

---

## 使用示例

```python
from edp_center.packages.edp_configkit.configkit.configkit import files2dict

# 加载并合并配置
config_files = [
    'common/main/config.yaml',
    'common/pv_calibre/config.yaml',
    'dongting/main/config.yaml',
    'dongting/pv_calibre/config.yaml',
    'user_config.yaml'
]

config = files2dict(*config_files)

# 访问配置
cpu_num = config.get('pv_calibre', {}).get('ipmerge', {}).get('cpu_num')
```

---

## 相关文档

- [架构设计文档](../architecture/architecture_overview.md)
- [WorkflowManager API](workflow_manager.md)
- [配置管理教程](../../tutorial/06_configuration.md)

