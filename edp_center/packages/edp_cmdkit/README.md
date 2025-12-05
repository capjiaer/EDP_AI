# EDP CmdKit

EDP CmdKit 是一个用于处理 Tcl 命令脚本的工具库，支持 `#import` 指令来导入和展开其他 Tcl 文件。

## 功能特性

- **`#import source <file>`**: 生成 `source` 语句来引用文件（推荐使用）
- **注意**：已移除 `#import util` 机制，统一使用 `#import source`

## 安装

```bash
pip install -e .
```

## 快速开始

### 基本用法

```python
from edp_cmdkit import CmdProcessor

# 创建处理器
processor = CmdProcessor()

# 方式 1：写入文件（推荐）
processor.process_file(
    input_file='my_script.tcl',
    output_file='output.tcl',  # 输入输出在一起
    search_paths=['cmds', 'util']  # 搜索路径列表
    # 返回值：None（内容已写入文件）
)

# 方式 2：直接获取内容
content = processor.process_file(
    input_file='my_script.tcl',
    search_paths=['cmds', 'util']
    # 返回值：处理后的内容字符串
)
print(content)

# 方式 3：使用默认配置（更简洁）
processor = CmdProcessor(
    default_search_paths=['cmds', 'util'],  # 默认搜索路径
    default_recursive=True
)

# 调用时更简洁
processor.process_file(
    input_file='my_script.tcl',
    output_file='output.tcl'
    # search_paths 和 recursive 使用默认值
)
```

### 示例

假设你有以下文件：

**my_example.tcl**:
```tcl
puts 1; #logic example
#import source xxx.tcl
puts 2; #Logic example
```

**xxx.tcl**:
```tcl
puts "xxx"
```

处理后的结果：

```tcl
puts 1; #logic example
source /path/to/xxx.tcl
puts 2; #Logic example
```

**注意**：`#import source` 会生成 `source` 语句，文件内容在运行时加载。

## 命令行接口

```bash
# 处理文件并输出到控制台
edp-cmdkit process cmds_example/my_example.tcl

# 处理文件并保存到输出文件
edp-cmdkit process cmds_example/my_example.tcl -o output.tcl

# 指定搜索目录列表（推荐方式）
edp-cmdkit process cmds_example/my_example.tcl -d cmds_example -d helpers/ -o output.tcl

# 添加默认 source 语句（方式 1：提供 foundry 和 node）
edp-cmdkit process my_script.tcl -d cmds -o output.tcl \
  --edp-center edp_center \
  --foundry SAMSUNG \
  --node S8 \
  --project dongting \
  --flow-name pv_calibre \
  --prepend-default-sources

# 添加默认 source 语句（方式 2：只提供 project，自动查找 foundry 和 node）
edp-cmdkit process my_script.tcl -d cmds -o output.tcl \
  --edp-center edp_center \
  --project dongting \
  --flow-name pv_calibre \
  --prepend-default-sources

# 添加默认 source 语句（方式 3：从脚本路径自动推断所有信息，最便捷）
edp-cmdkit process edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pv_calibre/steps/my_script.tcl \
  -d cmds -o output.tcl \
  --edp-center edp_center \
  --prepend-default-sources
```

## API 参考

### CmdProcessor

#### `__init__(base_dir=None)`

初始化处理器。

- `base_dir`: 基础目录，用于解析相对路径。如果为 None，使用当前工作目录。

#### `__init__(base_dir=None, default_search_paths=None, default_recursive=True)`

初始化处理器。

- `base_dir`: 基础目录，用于解析相对路径。如果为 None，使用当前工作目录
- `default_search_paths`: 默认搜索路径列表，用于查找被导入的文件。如果为 None，使用空列表
- `default_recursive`: 默认是否递归查找子目录。默认为 True

**示例**:
```python
processor = CmdProcessor(
    default_search_paths=['cmds', 'util'],  # 设置默认搜索路径
    default_recursive=True
)
```

#### `process_file(input_file, output_file=None, search_paths=None, recursive=None)`

处理 Tcl 文件，解析 `#import` 指令并生成最终脚本。

这是推荐的使用方式：**输入文件 -> 在指定目录中查找 util 文件替换 -> 输出文件**

**参数顺序优化**：输入输出在一起，配置参数在后。

- `input_file`: 输入的 Tcl 文件路径（str 或 Path 对象）
- `output_file`: 输出文件路径（str 或 Path 对象）。如果为 None，返回处理后的内容字符串
- `search_paths`: 搜索路径列表，用于查找被导入的文件。
                  - 如果为 None，使用默认搜索路径或文件所在目录和 base_dir
                  - 查找顺序：1) 相对当前文件 2) search_paths 中的路径 3) 文件所在目录和 base_dir
- `recursive`: 是否在搜索路径中递归查找子目录。
               - 如果为 None，使用默认值（初始化时设置的 default_recursive）
- `search_paths`: 搜索路径列表（通过 `-d/--search-paths` 指定）

**返回值**:
- 如果 `output_file` 为 None，返回处理后的内容字符串
- 如果 `output_file` 不为 None，返回 None（内容已写入文件）

**示例**:
```python
processor = CmdProcessor()

# 方式 1：写入文件（推荐）
processor.process_file(
    input_file='my_script.tcl',
    output_file='output.tcl',  # 输入输出在一起
    search_paths=['cmds', 'util']
)

# 方式 2：获取内容
content = processor.process_file(
    input_file='my_script.tcl',
    search_paths=['cmds', 'util']
)

# 方式 3：使用默认配置
processor = CmdProcessor(default_search_paths=['cmds', 'util'])
processor.process_file(
    input_file='my_script.tcl',
    output_file='output.tcl'
    # search_paths 使用默认值
)
```

## `#import` 指令

### `#import source <file>`（推荐使用）

生成 `source` 语句来引用文件。

**示例**:
```tcl
#import source config/settings.tcl
```

处理后的结果：
```tcl
source /absolute/path/to/config/settings.tcl
```

**注意**：已移除 `#import util` 机制，统一使用 `#import source`。

## 文件查找规则

1. 如果是绝对路径，直接检查文件是否存在
2. 如果是相对路径，首先相对于当前文件所在目录查找
3. 如果未找到，在 `search_paths` 中查找（按顺序）
4. 如果仍未找到，在 `base_dir` 中查找

## 默认 Source 语句

CmdKit 支持自动生成默认的 source 语句，用于加载 edp_center 中的 packages。

### 使用方式

```python
from edp_cmdkit import CmdProcessor

processor = CmdProcessor()

# 方式 1：提供 foundry 和 node
result = processor.process_file(
    input_file='my_script.tcl',
    output_file='output.tcl',
    search_paths=['cmds', 'helpers'],
    edp_center_path='edp_center',
    foundry='SAMSUNG',             # 代工厂
    node='S8',                     # 工艺节点
    project='dongting',            # 项目名称（可选）
    flow_name='pv_calibre',        # 流程名称（可选）
    prepend_default_sources=True
)

# 方式 2：只提供 project，自动查找 foundry 和 node（推荐）
result = processor.process_file(
    input_file='my_script.tcl',
    output_file='output.tcl',
    search_paths=['cmds', 'helpers'],
    edp_center_path='edp_center',
    project='dongting',            # 只需提供项目名称，自动查找 foundry 和 node
    flow_name='pv_calibre',
    prepend_default_sources=True
)

# 方式 3：从脚本路径自动推断所有信息（最便捷）
# 脚本路径格式：
# edp_center/flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/steps/<script>
# edp_center/flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/steps/<script>
# 注意：请使用 steps/ 目录（旧结构 scripts/ 已不再支持）
result = processor.process_file(
    input_file='edp_center/flow/initialize/SAMSUNG/S8/common/cmds/pv_calibre/steps/my_script.tcl',
    output_file='output.tcl',
    search_paths=['cmds', 'helpers'],
    edp_center_path='edp_center',
    prepend_default_sources=True  # 自动从路径推断 foundry, node, project, flow_name
)
```

### 生成的 Source 顺序

按照以下优先级顺序生成 source 语句（所有 `.tcl` 文件）：

1. `flow/common/packages/tcl/default/*`
2. `flow/common/packages/tcl/<flow_name>/*`
3. `flow/initialize/<FOUNDRY>/<NODE>/common/packages/tcl/default/*`
4. `flow/initialize/<FOUNDRY>/<NODE>/common/packages/tcl/<flow_name>/*`
5. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/packages/tcl/default/*`
6. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/packages/tcl/<flow_name>/*`

这些 source 语句会自动添加到处理后的文件头部。

### 单独使用 PackageLoader

```python
from edp_cmdkit import PackageLoader

loader = PackageLoader('edp_center')

# 方式 1：提供 foundry 和 node
sources = loader.generate_default_sources(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow_name='pv_calibre'
)

# 方式 2：只提供 project，自动查找 foundry 和 node（推荐）
sources = loader.generate_default_sources(
    project='dongting',  # 自动查找 foundry 和 node
    flow_name='pv_calibre'
)
print(sources)
```

## 注意事项

- 处理器会自动检测并防止循环引用
- 被 source 的文件也会被递归处理，可以包含 `#import source` 指令
- `#import` 指令必须在一行的开头（可以有前导空格）
- 指令格式：`#import source <file>`
- 默认 source 语句会按照文件名排序，确保顺序一致
- **注意**：已移除 `#import util` 机制，统一使用 `#import source`

## 开发

```bash
# 运行测试
python -m pytest tests/

# 格式化代码
black edp_cmdkit/

# 类型检查
mypy edp_cmdkit/
```

