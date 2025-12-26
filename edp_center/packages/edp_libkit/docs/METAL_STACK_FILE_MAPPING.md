# Metal Stack 与文件对应关系

本文档说明 Metal Stack 与相关文件的对应关系。

## 核心理解

> **Metal Stack 确定 → TF文件确定 → GDS层映射文件确定**
> 
> 三者是**一一对应**的关系！

---

## 文件对应关系

### 示例：Metal Stack = `12M_3Mx_6Dx_1Gx_2Iz_LB`

**对应的文件：**

```
Metal Stack: 12M_3Mx_6Dx_1Gx_2Iz_LB
    ↓
TF文件: sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
    ↓
GDS层映射: gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB
          gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB
```

**目录结构：**
```
ndm/
├── tf/
│   └── sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf  ← TF文件
└── scripts/
    ├── gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB         ← GDS输入映射
    └── gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB        ← GDS输出映射
```

---

## 不同 Metal Stack 的文件对应

### Metal Stack 1: `12M_3Mx_6Dx_1Gx_2Iz_LB`

**对应文件：**
- ✅ `tf/sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf`
- ✅ `scripts/gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB`
- ✅ `scripts/gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB`

---

### Metal Stack 2: `13M_3Mx_6Dx_2Hx_2Iz_LB`

**对应文件：**
- ✅ `tf/sa08nvmhlogl22hdf068a_13M_3Mx_6Dx_2Hx_2Iz_LB.tf`
- ✅ `scripts/gds_in_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB`
- ✅ `scripts/gds_out_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB`

---

### Metal Stack 3: `11M_3Mx_6Dx_1Gx_1Iz_LB`

**对应文件：**
- ✅ `tf/sa08nvmhlogl22hdf068a_11M_3Mx_6Dx_1Gx_1Iz_LB.tf`
- ✅ `scripts/gds_in_layer_map.11M_3Mx_6Dx_1Gx_1Iz_LB`
- ✅ `scripts/gds_out_layer_map.11M_3Mx_6Dx_1Gx_1Iz_LB`

---

## 关键要点

### 1. 一一对应关系

**Metal Stack → TF文件 → GDS层映射文件**

- ✅ 一旦Metal Stack确定，对应的TF文件就确定了
- ✅ 对应的GDS层映射文件也确定了
- ✅ 它们必须**匹配使用**，不能混用

---

### 2. 不能混用

**错误示例：**
```tcl
# ❌ 错误：混用不同Metal Stack的文件
set_app_options -name lib.setting.technology_file \
    {/path/to/tf/sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf}

# 但使用13M的GDS层映射
source /path/to/scripts/gds_in_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB
```

**正确示例：**
```tcl
# ✅ 正确：使用相同Metal Stack的文件
set_app_options -name lib.setting.technology_file \
    {/path/to/tf/sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf}

# 使用对应的12M GDS层映射
source /path/to/scripts/gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB
source /path/to/scripts/gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB
```

---

### 3. 实际应用

**在项目配置中：**

```yaml
# 项目配置
metal_stack: "12M_3Mx_6Dx_1Gx_2Iz_LB"

# 自动对应的文件
tf_file: "sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf"
gds_in_layer_map: "gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB"
gds_out_layer_map: "gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB"
```

**工具可以自动匹配：**
- 给定Metal Stack，自动找到对应的TF文件
- 自动找到对应的GDS层映射文件
- 确保文件匹配，避免错误

---

## 总结

### 对应关系表

| Metal Stack | TF文件 | GDS输入映射 | GDS输出映射 |
|------------|--------|------------|------------|
| `12M_3Mx_6Dx_1Gx_2Iz_LB` | `*_12M_3Mx_6Dx_1Gx_2Iz_LB.tf` | `gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB` | `gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB` |
| `13M_3Mx_6Dx_2Hx_2Iz_LB` | `*_13M_3Mx_6Dx_2Hx_2Iz_LB.tf` | `gds_in_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB` | `gds_out_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB` |
| `11M_3Mx_6Dx_1Gx_1Iz_LB` | `*_11M_3Mx_6Dx_1Gx_1Iz_LB.tf` | `gds_in_layer_map.11M_3Mx_6Dx_1Gx_1Iz_LB` | `gds_out_layer_map.11M_3Mx_6Dx_1Gx_1Iz_LB` |

### 关键理解

1. ✅ **Metal Stack确定 → 所有相关文件都确定**
2. ✅ **必须匹配使用**，不能混用不同Metal Stack的文件
3. ✅ **工具可以自动匹配**，根据Metal Stack找到对应文件

**实际建议：**
- 在项目配置中，只需要指定Metal Stack
- 工具自动找到对应的TF文件和GDS层映射文件
- 确保文件匹配，避免配置错误

