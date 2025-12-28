# Power Gate（电源门控）详解

## 什么是 Power Gate？

**Power Gate（电源门控）**是一种低功耗设计技术，通过在不需要时切断某个电路模块的电源供应，从而显著降低静态功耗（Leakage Power）。

## 基本概念

### 工作原理

```
正常模式（Power On）：
VDD ──[Power Gate Switch]──> 功能模块 ──> GND
      ↑
      控制信号（Enable）

关闭模式（Power Off）：
VDD ──[Power Gate Switch]──X──> 功能模块 ──> GND
      ↑
      控制信号（Disable）
```

### 关键组件

1. **Power Gate Switch（电源门控开关）**
   - 通常是一个大的 PMOS 或 NMOS 晶体管
   - 控制电源到功能模块的连接
   - 当开关关闭时，功能模块完全断电

2. **功能模块（Function Block）**
   - 需要被电源门控的电路模块
   - 例如：CPU 核心、GPU、DSP、外设模块等

3. **控制逻辑（Control Logic）**
   - 决定何时开启/关闭 Power Gate
   - 通常由电源管理单元（PMU）控制

## 为什么需要 Power Gate？

### 1. **降低静态功耗**

**问题**：
- 现代芯片的静态功耗（Leakage Power）占总功耗的很大比例
- 即使电路不工作，由于漏电流，仍然消耗功率

**解决方案**：
- Power Gate 可以完全切断电源，消除漏电流
- 静态功耗可以降低到接近零

### 2. **延长电池寿命**

**应用场景**：
- 移动设备（手机、平板、IoT 设备）
- 电池供电设备
- 需要长时间待机的设备

**效果**：
- 在待机模式下，关闭不需要的模块
- 显著延长电池寿命

### 3. **热管理**

**问题**：
- 芯片发热会影响性能和可靠性

**解决方案**：
- 关闭不使用的模块，减少发热
- 改善热管理

## Power Gate 的设计挑战

### 1. **状态保存和恢复**

**问题**：
- 当模块断电时，所有状态都会丢失
- 恢复时需要重新初始化

**解决方案**：
- **Retention Register（保持寄存器）**：保存关键状态
- **State Save/Restore**：在断电前保存状态，恢复时加载

### 2. **时序问题**

**问题**：
- Power Gate 开关的开启/关闭需要时间
- 可能影响时序

**解决方案**：
- **Isolation Cell（隔离单元）**：防止未定义信号传播
- **Power Sequence Control**：控制电源开启/关闭的顺序

### 3. **电压和电流冲击**

**问题**：
- 突然开启/关闭电源可能产生电压和电流冲击
- 可能影响其他模块

**解决方案**：
- **Gradual Power On/Off**：逐步开启/关闭电源
- **Decoupling Capacitor**：去耦电容平滑电压

## Power Gate Corner 的作用

### 为什么需要专门的 PVT Corner？

Power Gate 场景下的电路特性与正常工作模式不同：

1. **电压特性不同**
   - Power Gate 开关的导通电阻会影响电压
   - 功能模块的实际工作电压可能与标称电压不同

2. **时序特性不同**
   - Power Gate 开关的延迟会影响时序
   - 需要考虑开关开启/关闭的时序

3. **功耗特性不同**
   - Power Gate 开关本身也有功耗
   - 需要考虑开关的功耗

### Power Gate Corner 的命名格式

根据三星的命名规范，Power Gate Corner 使用 `pg_` 前缀：

```
pg_{process}{voltage}{temperature}
```

**示例**：
- `pg_ffpg0p715v125c` - Power Gate, Fast-Fast, 0.715V, 125°C
- `pg_tt0p85v85c` - Power Gate, Typical, 0.85V, 85°C
- `pg_sfg0p675vn40c` - Power Gate, Slow-Fast, 0.675V, -40°C

### Power Gate Corner 的类型

根据表格 "Table 4-3 Power Gate Corners"，Power Gate Corner 包括：

| Process | 说明 | 示例 |
|---------|------|------|
| `ffpg` | Fast-Fast Process Gate | `pg_ffpg0p715v125c` |
| `fsg` | Fast-Slow Gate | `pg_fsg0p675vn40c` |
| `sfg` | Slow-Fast Gate | `pg_sfg0p675vn40c` |
| `sspg` | Slow-Slow Process Gate | `pg_sspg0p585v125c` |
| `tt` | Typical | `pg_tt0p85v85c` |

## 在 lib_config.tcl 中的体现

```tcl
# Power Gate Corner 示例
set LIBRARY(cell_name,ccs_lvf,sigcmin,pg_ffpg0p715v125c,db) {
    /path/to/cell_name_pg_ffpg0p715v125c.db
}

set LIBRARY(cell_name,ccs_lvf,typical,pg_tt0p85v85c,db) {
    /path/to/cell_name_pg_tt0p85v85c.db
}

set LIBRARY(cell_name,ccs_lvf,sigcmax,pg_sfg0p675vn40c,db) {
    /path/to/cell_name_pg_sfg0p675vn40c.db
}
```

## 实际应用场景

### 场景1：移动 SoC

**设计**：
- CPU 核心：工作时开启，待机时关闭
- GPU：玩游戏时开启，其他时候关闭
- DSP：处理音频/视频时开启，其他时候关闭

**Power Gate Corner**：
- 用于仿真 Power Gate 开关对时序和功耗的影响
- 确保在 Power Gate 场景下，电路仍能正常工作

### 场景2：IoT 设备

**设计**：
- 传感器模块：采集数据时开启，其他时候关闭
- 通信模块：发送数据时开启，其他时候关闭

**Power Gate Corner**：
- 用于优化功耗
- 确保在极低功耗模式下，电路仍能正常工作

## 总结

**Power Gate（电源门控）**是现代低功耗设计中的关键技术：

1. **目的**：通过切断不需要的模块的电源，降低静态功耗
2. **应用**：移动设备、IoT 设备、电池供电设备
3. **挑战**：状态保存、时序问题、电压冲击
4. **Power Gate Corner**：专门用于仿真 Power Gate 场景下的电路特性
5. **命名格式**：`pg_{process}{voltage}{temperature}`

Power Gate Corner 确保了在电源门控场景下，电路仍能正常工作，并且功耗分析更加准确。

