# edp_configkit API 文档

## 📋 概述

`edp_configkit` 提供配置文件的加载、合并和转换功能（YAML ↔ Tcl），支持变量引用功能。

**位置**: `edp_center.packages.edp_configkit`

---

## 核心函数

### `files2dict(*file_paths, mode="auto", skip_errors=False)`

将多个配置文件合并为一个字典。

**位置**: `edp_center.packages.edp_configkit.files2dict`

**参数**:
- `*file_paths` (Union[str, Path]): 配置文件路径（可变参数）
- `mode` (str): 转换模式，可选值：`"auto"`, `"str"`, `"list"`（默认：`"auto"`）
- `skip_errors` (bool): 是否跳过错误文件（默认：`False`）

**返回**:
- `Dict[str, Any]`: 合并后的配置字典

**说明**:
- 支持 YAML 和 Tcl 格式
- 后加载的配置会覆盖先加载的配置
- 自动处理数组格式的变量（`flow_name(step_name,key)`）

### `yamlfiles2dict(*yaml_files, expand_variables=True)`

将一个或多个 YAML 文件加载到 Python 字典中，支持变量引用。

**位置**: `edp_center.packages.edp_configkit.yamlfiles2dict`

**参数**:
- `*yaml_files` (str): YAML 文件路径（可变参数）
- `expand_variables` (bool): 是否展开变量引用（默认：`True`）

**返回**:
- `Dict[str, Any]`: 合并后的配置字典

**说明**:
- 支持 YAML 文件中的变量引用（`$var`, `${var}`, `$var(key)`, `$var(key1,key2)`）
- 后面的变量可以引用前面定义的变量
- 多文件加载时，后面的文件可以引用前面文件定义的变量
- 变量展开后类型为字符串

### `expand_variable_references(interp)`

在 Tcl 解释器中展开变量引用。

**位置**: `edp_center.packages.edp_configkit.expand_variable_references`

**参数**:
- `interp` (Tcl): Tcl 解释器对象

**说明**:
- 展开 Tcl 解释器中包含 `$` 的变量引用
- 使用 Tcl 的 `subst` 命令进行变量替换

**示例**:
```python
from edp_center.packages.edp_configkit import files2dict

config = files2dict(
    'common/main/config.yaml',
    'common/pv_calibre/config.yaml',
    'dongting/main/config.yaml',
    'dongting/pv_calibre/config.yaml',
    'user_config.yaml'
)
```

---

## YAML 变量引用

### 支持的变量引用格式

`yamlfiles2dict` 支持在 YAML 文件中使用变量引用：

**简单变量引用**:
```yaml
base_port: 8080
server_port: $base_port        # 引用 base_port
api_port: ${base_port}         # 使用大括号（推荐，避免歧义）
```

**嵌套字典引用**:
```yaml
database:
  host: localhost
  port: 5432
db_url: "postgres://${database(host)}:${database(port)}/mydb"  # 引用嵌套字典
```

**深层嵌套引用**:
```yaml
app:
  config:
    timeout: 30
timeout_value: $app(config,timeout)  # 多层嵌套引用
```

**字符串中的变量引用**:
```yaml
prefix: "http://"
suffix: "/api"
api_url: "${prefix}example.com${suffix}"  # 字符串拼接
```

### 使用示例

```python
from edp_center.packages.edp_configkit import yamlfiles2dict

# config.yaml 内容:
# a: 1
# b: $a
# c: ${a}
# nested:
#   key: 100
# d: $nested(key)

config = yamlfiles2dict('config.yaml')
print(config['b'])    # 输出: '1' (字符串)
print(config['c'])    # 输出: '1' (字符串)
print(config['d'])    # 输出: '100' (字符串)

# 禁用变量展开
config_no_expand = yamlfiles2dict('config.yaml', expand_variables=False)
print(config_no_expand['b'])  # 输出: '$a' (原始字符串)
```

### 注意事项

1. **变量展开后类型为字符串**：即使原值是数字，展开后也是字符串
2. **变量顺序**：后面的变量可以引用前面定义的变量
3. **多文件支持**：后面的文件可以引用前面文件定义的变量
4. **推荐使用 `${var}` 格式**：避免变量名歧义（如 `$a_suffix` 会被解析为 `$a_suffix` 而不是 `${a}_suffix`）

---

## 配置转换

### YAML → Tcl

配置文件从 YAML 格式转换为 Tcl 格式（在生成 `full.tcl` 时自动完成）。

**转换规则**:
- 数组格式：`flow_name.step_name.key: value` → `set flow_name(step_name,key) value`
- 嵌套结构：自动展开为数组格式
- 类型转换：自动处理字符串、数字、布尔值
- **变量引用**：YAML 中的变量引用会在转换为 Tcl 前展开

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
from edp_center.packages.edp_configkit import files2dict

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

