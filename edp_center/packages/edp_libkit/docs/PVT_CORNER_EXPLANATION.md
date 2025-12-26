# PVT Corner 命名格式详解

## 概述

PVT Corner 是半导体工艺角（Process-Voltage-Temperature Corner）的缩写，用于描述芯片在不同工艺、电压、温度条件下的性能特性。三星的库文件中使用不同的命名格式来区分不同的应用场景，包括标准数字电路、Level Shifter（电平转换器）和 Power Gate（电源门控）等。

**相关文档**：
- 关于 Power Gate 的详细说明，请参考：[Power Gate 详解](POWER_GATE_EXPLANATION.md)
- 关于 Level Shifter 的详细说明，请参考：[Level Shifter 详解](LEVEL_SHIFTER_EXPLANATION.md)
- 关于 Slew Rate 的详细说明，请参考：[Slew Rate 详解](SLEW_RATE_EXPLANATION.md)

## PVT Corner 基础

### 标准 PVT Corner 组成

一个标准的 PVT corner 通常包含：
- **Process (P)**：工艺角（ff = fast-fast, ss = slow-slow, tt = typical）
- **Voltage (V)**：电压（如 0p715v = 0.715V, 0p825v = 0.825V）
- **Temperature (T)**：温度（如 125c = 125°C, n40c = -40°C）

### 示例解析

```
ffpg0p715v125c
│││││││││││││
│││││││││││└─ 125°C (温度)
││││││││││└── 125c
│││││││││└─── v (voltage)
││││││││└──── 0p715 (0.715V)
│││││││└───── p (point)
││││││└────── 0 (0)
│││││└─────── g (可能是 general 或 ground)
││││└──────── p (process)
│││└───────── f (fast)
││└────────── f (fast)
└───────────── ff = fast-fast (工艺角)
```

## 三种命名格式详解（基于实际文件）

### 1. 最简单版本：`ffpg0p715v125c` 或 `sfg0p675vn40c`

**格式**：`{process}{voltage}{temperature}`

**示例**：
- `ffpg0p715v125c` - Fast-Fast, 0.715V, 125°C
- `sfg0p675vn40c` - Slow-Fast (变体), 0.675V, -40°C
- `sspg0p585v125c` - Slow-Slow, 0.585V, 125°C
- `tt0p75v125c` - Typical, 0.75V, 125°C

**用途**：
- **标准数字电路**：用于常规的数字逻辑设计
- **通用场景**：大多数标准单元库的标准配置
- **最常用**：这是最常见的格式，覆盖了大部分设计需求

**特点**：
- 直接表示工艺、电压、温度
- 无特殊前缀或后缀
- 适用于大多数标准设计
- **注意**：`sfg` 是 `ss` 的变体格式，归类为 worst case (`sigcmax`)

### 2. 带前缀的版本：`dlvl_ffpg0p715v125c` 或 `pg_tt0p85v85c`

**格式**：`{prefix}_{process}{voltage}{temperature}`

**前缀类型**：
- **`ulvl`**：**Up Level Shifters**（向上电平转换器）
- **`dlvl`**：**Down Level Shifters**（向下电平转换器）
- **`udlvl`**：**Up Down Level Shifters**（双向电平转换器）
- **`pg`**：**Power Gate**（电源门控，用于低功耗设计）

**示例**：
- `ulvl_ffpg0p715v125c` - Up Level Shifter, Fast-Fast, 0.715V, 125°C
- `dlvl_ffpg0p715v125c` - Down Level Shifter, Fast-Fast, 0.715V, 125°C
- `dlvl_ffpg0p715v125c_i0p825v` - Down Level Shifter, Fast-Fast, 0.715V, 125°C, Input 0.825V
- `udlvl_ffpg0p715v125c` - Up Down Level Shifter, Fast-Fast, 0.715V, 125°C
- `udlvl_ffpg0p715v125c_i0p825v` - Up Down Level Shifter, Fast-Fast, 0.715V, 125°C, Input 0.825V
- `pg_ffpg0p715v125c` - Power Gate, Fast-Fast, 0.715V, 125°C
- `pg_tt0p85v85c` - Power Gate, Typical, 0.85V, 85°C
- `pg_tt0p95v125c` - Power Gate, Typical, 0.95V, 125°C
- `pg_tt0p95v85c` - Power Gate, Typical, 0.95V, 85°C
- `pg_sfg0p675vn40c` - Power Gate, Slow-Fast, 0.675V, -40°C

**用途**：
- **Up Level Shifters (`ulvl`)**：将低电压域的信号转换到高电压域（例如：0.715V → 0.9V）
- **Down Level Shifters (`dlvl`)**：将高电压域的信号转换到低电压域（例如：0.825V → 0.715V）
- **Up Down Level Shifters (`udlvl`)**：双向电平转换器，可以同时处理向上和向下的电压转换
- **Power Gate（电源门控）**：`pg` 用于电源门控场景，这是低功耗设计中的关键技术

**为什么需要？**：
- **电压域转换**：在多电压域设计中，需要 Level Shifter 在不同电压之间转换信号
- **不同转换方向**：
  - `ulvl`：向上转换（低电压 → 高电压）
  - `dlvl`：向下转换（高电压 → 低电压）
  - `udlvl`：双向转换（可以处理两个方向的转换）
- **输入电压参数**：当 Level Shifter 的输入电压与输出电压不同时，需要 `_i0p825v` 这样的后缀来指定输入电压
- **电源门控特性**：Power Gate 场景下的电路特性与正常工作模式不同，需要专门的 PVT corner
- **性能权衡**：不同的前缀表示不同的应用场景和性能特性

### 3. 带前缀和额外电压参数的版本：`dlvl_ffpg0p715v125c_i0p825v`

**格式**：`{prefix}_{process}{voltage}{temperature}_{input_voltage}`

**额外电压参数**：
- **`_i0p825v`**：Input Voltage 0.825V（输入电压）
- **`_i0p675v`**：Input Voltage 0.675V
- **`_i0p855v`**：Input Voltage 0.855V
- **`_i0p9v`**：Input Voltage 0.9V

**示例**：
- `dlvl_ffpg0p715v125c_i0p825v` - Dual Level, Fast-Fast, 0.715V, 125°C, Input 0.825V

**用途**：
- **Level Shifter**：电平转换器需要知道输入电压和输出电压
- **多电压域设计**：在不同电压域之间转换信号时，需要精确的电压特性
- **精确仿真**：需要更精确的电压特性数据

**为什么需要？**：
- **Level Shifter 特性**：电平转换器的性能取决于输入电压和输出电压的组合
- **电压转换精度**：不同的输入电压会导致不同的转换特性
- **仿真准确性**：需要针对特定的输入/输出电压组合进行精确仿真

## 实际应用场景

### 场景1：标准数字电路设计

**使用**：`ffpg0p715v125c`, `sspg0p585v125c`, `tt0p75v125c`

**原因**：
- 标准单元库的标准配置
- 覆盖大多数设计需求
- 简单直接，易于理解

### 场景2：多电压域设计（Level Shifter）

**使用**：`ulvl_ffpg0p715v125c`, `dlvl_ffpg0p715v125c`, `udlvl_ffpg0p715v125c`

**原因**：
- 需要在不同电压域之间转换信号
- **不同的 Level Shifter 类型**：
  - **`ulvl`（Up Level Shifters）**：将低电压域的信号转换到高电压域
    - 例如：从 0.715V 域转换到 0.9V 域
  - **`dlvl`（Down Level Shifters）**：将高电压域的信号转换到低电压域
    - 例如：从 0.825V 域转换到 0.715V 域
  - **`udlvl`（Up Down Level Shifters）**：双向电平转换器
    - 可以同时处理向上和向下的电压转换
- 适用于多电压域 SoC 设计

### 场景3：多电压域设计（Level Shifter，精确电压）

**使用**：`dlvl_ffpg0p715v125c_i0p825v` 或 `udlvl_ffpg0p715v125c_i0p9v`

**原因**：
- 需要在不同电压域之间转换信号，且输入电压与输出电压不同
- **Down Level Shifter 示例**：`dlvl_ffpg0p715v125c_i0p825v`
  - 输出电压（VDD）：0.715V
  - 输入电压（VDDI）：0.825V
  - 从 0.825V 域转换到 0.715V 域
- **Up Down Level Shifter 示例**：`udlvl_ffpg0p715v125c_i0p9v`
  - 输出电压（VDD）：0.715V
  - 输入电压（VDDI）：0.9V
  - 可以处理从 0.9V 到 0.715V 的转换
- 输入电压参数（`_i0p825v`）确保 Level Shifter 的精确仿真

## 命名规则总结（基于实际文件）

| 格式 | 示例 | 用途 | 特点 |
|------|------|------|------|
| 标准格式 | `ffpg0p715v125c`, `sfg0p675vn40c` | 标准数字电路 | 最常用，无前缀 |
| 前缀格式 | `ulvl_ffpg...`, `dlvl_ffpg...`, `udlvl_sspg...`, `pg_tt...` | Level Shifter / 电源管理 | 带前缀（ulvl/dlvl/udlvl 或 pg） |
| 前缀 + 输入电压格式 | `dlvl_ffpg0p715v125c_i0p825v` | Level Shifter（精确电压） | 带前缀和输入电压参数 |

**注意**：
- `sfg` 是 `ss` 的变体格式，归类为 worst case (`sigcmax`)
- **Level Shifter 类型**：
  - `ulvl` = **Up Level Shifters**（向上电平转换器）
  - `dlvl` = **Down Level Shifters**（向下电平转换器）
  - `udlvl` = **Up Down Level Shifters**（双向电平转换器）
- `pg` 是 **Power Gate**（电源门控），用于低功耗设计场景
- **不存在 `ulvt` 格式**

## 为什么三星需要这三种格式？

### 1. **设计多样性**
- 不同的应用场景需要不同的特性
- 标准格式无法满足所有需求

### 2. **工艺复杂性**
- 现代芯片设计涉及多个电压域
- 需要 Level Shifter 在不同电压域之间转换

### 3. **多电压域支持**
- 现代 SoC 设计需要多个电压域
- 不同电压域之间需要 Level Shifter 进行信号转换
- **Level Shifter 类型**：
  - `ulvl`：向上转换（低电压 → 高电压）
  - `dlvl`：向下转换（高电压 → 低电压）
  - `udlvl`：双向转换（可以处理两个方向）

### 4. **仿真精度**
- 不同的电压组合需要不同的特性数据
- 精确的仿真需要详细的电压参数

## 在 lib_config.tcl 中的体现

```tcl
# 标准格式
set LIBRARY(cell_name,ccs_lvf,sigcmin,ffpg0p715v125c,db) {...}

# Level Shifter 前缀格式
set LIBRARY(cell_name,ccs_lvf,sigcmin,ulvl_ffpg0p715v125c,db) {...}
set LIBRARY(cell_name,ccs_lvf,sigcmin,dlvl_ffpg0p715v125c,db) {...}
set LIBRARY(cell_name,ccs_lvf,sigcmax,udlvl_sspg1p0v125c,db) {...}

# Level Shifter + 输入电压格式
set LIBRARY(cell_name,ccs_lvf,sigcmin,dlvl_ffpg0p715v125c_i0p825v,db) {...}
set LIBRARY(cell_name,ccs_lvf,sigcmax,udlvl_sspg1p0v125c_i0p675v,db) {...}

# Power Gate 格式
set LIBRARY(cell_name,ccs_lvf,typical,pg_tt0p85v85c,db) {...}
set LIBRARY(cell_name,ccs_lvf,sigcmin,pg_ffpg0p715v125c,db) {...}
set LIBRARY(cell_name,ccs_lvf,sigcmax,pg_sfg0p675vn40c,db) {...}
```

## 总结

这三种命名格式反映了现代芯片设计的复杂性：
1. **标准格式**：满足大多数常规设计需求
2. **VT 前缀格式**：满足特殊功耗和性能需求
3. **VT + 输入电压格式**：满足多电压域设计和 Level Shifter 的精确需求

这种多样化的命名格式确保了库文件能够支持各种不同的设计场景，从标准数字电路到复杂的多电压域设计。

