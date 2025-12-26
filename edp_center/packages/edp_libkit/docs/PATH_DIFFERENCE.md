# lib-path 参数不同路径的区别

## 问题说明

当 `--lib-path` 指定不同的目录层级时，生成的结果会有显著区别。

## 测试场景

### 场景1：指定父目录
```bash
--lib-path C:\...\STD_Cell\0711_install
```

### 场景2：指定具体库目录
```bash
--lib-path C:\...\STD_Cell\0711_install\v-logic_sa08nvghlogl20hdf068f
```

## 实际结果对比

### 场景1的结果（父目录）

**库名**：`0711_install`（使用目录名）

**输出路径**：
```
Samsung/STD/0711_install/2.00A/lib_config.tcl
```

**包含的文件**：
- ✅ `v-logic_sa08nvghlogl20hdf068f` 库的所有文件
- ✅ `v-logic_sa08nvghlogl20hsf068f` 库的所有文件
- ✅ 其他子目录中的文件

**TCL条目示例**：
```tcl
set LIBRARY(0711_install,gds,gds) {
  .../v-logic_sa08nvghlogl20hdf068f/.../file1.gds
  .../v-logic_sa08nvghlogl20hdf068f/.../file2.gds
  .../v-logic_sa08nvghlogl20hsf068f/.../file3.gds
}
```

**特点**：
- 🔍 **递归扫描**：会递归查找所有子目录中的视图文件
- 📦 **聚合结果**：多个库的文件被合并到一个配置文件中
- ⚠️ **库名不准确**：库名是父目录名，不是实际的库名

### 场景2的结果（具体库目录）

**库名**：`sa08nvghlogl20hdf068f`（去掉v-logic_前缀）

**输出路径**：
```
Samsung/STD/sa08nvghlogl20hdf068f/2.00A/lib_config.tcl
```

**包含的文件**：
- ✅ 只包含 `v-logic_sa08nvghlogl20hdf068f` 库的文件
- ❌ 不包含其他库的文件

**TCL条目示例**：
```tcl
set LIBRARY(sa08nvghlogl20hdf068f,gds,gds) {
  .../v-logic_sa08nvghlogl20hdf068f/.../file1.gds
  .../v-logic_sa08nvghlogl20hdf068f/.../file2.gds
}
```

**特点**：
- 🎯 **精确匹配**：只处理指定的库目录
- ✅ **库名准确**：使用实际的库名称
- 📁 **结构清晰**：每个库生成独立的配置文件

## 为什么会这样？

### `find_view_directories` 的实现

适配器使用 `os.walk()` 递归查找视图目录：

```python
def _find_std_view_directories(self, lib_path: Path) -> Dict[str, Path]:
    view_dirs = {}
    for root, dirs, files in os.walk(lib_path):  # 递归遍历
        # 查找 gds/, lef/, liberty/ 等目录
        ...
```

**影响**：
- 如果指定父目录，`os.walk()` 会遍历所有子目录
- 找到的所有视图文件都会被收集
- 结果是把多个库的文件合并在一起

## 推荐做法

### ✅ 推荐：指定具体库目录

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp
```

**优点**：
- 库名准确
- 每个库独立配置
- 结构清晰
- 易于管理

### ⚠️ 不推荐：指定父目录

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/STD_Cell/0711_install \
  --lib-type STD \
  --node ln08lpu_gp
```

**缺点**：
- 库名不准确（使用父目录名）
- 多个库的文件混在一起
- 难以区分不同库的文件
- 可能导致配置混乱

## 如果需要处理多个库

### 方法1：循环调用（推荐）

```bash
# 处理每个库
for lib_dir in /path/to/STD_Cell/0711_install/v-logic_*; do
    edp-libkit gen-lib \
      --foundry Samsung \
      --lib-path "$lib_dir" \
      --lib-type STD \
      --node ln08lpu_gp
done
```

### 方法2：使用脚本

```python
import subprocess
from pathlib import Path

lib_base = Path('/path/to/STD_Cell/0711_install')
for lib_dir in lib_base.glob('v-logic_*'):
    subprocess.run([
        'edp-libkit', 'gen-lib',
        '--foundry', 'Samsung',
        '--lib-path', str(lib_dir),
        '--lib-type', 'STD',
        '--node', 'ln08lpu_gp'
    ])
```

## 总结

| 特性 | 父目录 | 具体库目录 |
|------|--------|------------|
| 库名 | 父目录名（不准确） | 实际库名（准确） |
| 文件范围 | 所有子库 | 单个库 |
| 输出文件 | 1个（聚合） | 每个库1个 |
| 推荐度 | ⚠️ 不推荐 | ✅ 推荐 |

**建议**：始终指定具体的库目录，而不是父目录。

