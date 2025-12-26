# 明天工作计划 - MEM 和 IP 库支持

## 当前状态

### ✅ STD库（已完成）
- 完整支持Samsung 8nm STD库
- 版本选择功能正常
- 视图文件查找正常
- 生成的 `lib_config.tcl` 格式正确

### ⏳ IP库（待测试和完善）
- 基础框架已存在
- 已有测试示例：`tests/LIB_Example/IP/ln08lpu_gpio_1p8v/v1.12/`
- 需要验证：
  - 版本提取逻辑（IP库版本在目录名中，如 `v1.12`）
  - `FE-Common` 和 `BE-Common` 目录的查找
  - 视图文件识别（GDS, LEF, LIBERTY等）
  - 生成的 `lib_config.tcl` 格式

### ⏳ MEM库（待测试和完善）
- 基础框架已存在
- 需要实际MEM库示例进行测试
- 需要验证：
  - 目录结构识别
  - 版本提取逻辑
  - 视图文件查找（GDS, LEF, LIBERTY等）
  - 生成的 `lib_config.tcl` 格式

## IP库当前实现

### 目录结构
```
IP/
└── ln08lpu_gpio_1p8v/
    └── v1.12/
        ├── FE-Common/
        │   ├── LEF/
        │   ├── LIBERTY/
        │   └── IBIS/
        └── BE-Common/
            ├── GDS/
            └── LEF/
```

### 需要验证的功能

1. **版本提取**
   - IP库版本在目录名中（如 `v1.12`）
   - 需要验证 `extract_lib_info` 是否正确提取

2. **视图目录查找**
   - `_find_ip_view_directories` 方法需要验证
   - 需要查找 `FE-Common` 和 `BE-Common` 下的视图

3. **文件收集**
   - 需要验证各种视图文件的收集逻辑
   - GDS, LEF, LIBERTY等文件格式

## MEM库当前实现

### 预期目录结构
```
MEM/
└── sram_xxx/
    ├── gds/
    ├── lef/
    └── liberty/
```

### 需要验证的功能

1. **目录结构识别**
   - MEM库的目录结构可能不同
   - 需要根据实际MEM库调整

2. **版本提取**
   - MEM库的版本信息可能在不同位置
   - 需要验证提取逻辑

3. **视图目录查找**
   - `_find_mem_view_directories` 方法需要验证
   - 需要根据实际结构调整

## 测试计划

### IP库测试

1. **基本功能测试**
   ```bash
   edp-libkit gen-lib \
     --foundry Samsung \
     --lib-path tests/LIB_Example/IP/ln08lpu_gpio_1p8v/v1.12 \
     --lib-type IP \
     --node ln08lpu_gp \
     --output-dir tests/output_ip
   ```

2. **验证生成的文件**
   - 检查 `lib_config.tcl` 格式
   - 验证文件路径是否正确
   - 验证版本信息是否正确

3. **版本选择测试**
   - 如果有多个版本，测试版本选择功能
   - 测试 `--all-versions` 功能

### MEM库测试

1. **准备测试数据**
   - 需要实际的MEM库示例
   - 如果没有，需要创建模拟结构

2. **基本功能测试**
   ```bash
   edp-libkit gen-lib \
     --foundry Samsung \
     --lib-path /path/to/mem_lib \
     --lib-type MEM \
     --node ln08lpu_gp \
     --output-dir tests/output_mem
   ```

3. **验证生成的文件**
   - 检查 `lib_config.tcl` 格式
   - 验证文件路径是否正确

## 可能遇到的问题

1. **IP库版本提取**
   - IP库版本在目录名中（`v1.12`）
   - 需要确保 `extract_lib_info` 正确处理

2. **视图目录结构**
   - IP库有 `FE-Common` 和 `BE-Common`
   - 需要确保查找逻辑正确

3. **MEM库结构**
   - MEM库结构可能与STD/IP不同
   - 需要根据实际情况调整

4. **文件格式**
   - 不同库类型的文件格式可能不同
   - 需要验证 `lib_config.tcl` 格式是否正确

## 完成标准

- ✅ IP库可以正常生成 `lib_config.tcl`
- ✅ MEM库可以正常生成 `lib_config.tcl`
- ✅ 版本选择功能在IP和MEM库中正常工作
- ✅ 生成的配置文件格式正确
- ✅ 所有测试通过

## 相关文件

### 需要检查的文件
- `foundry_adapters/samsung/base_node_adapter.py`
  - `_find_ip_view_directories` 方法
  - `_find_mem_view_directories` 方法
  - `extract_lib_info` 方法（IP库版本提取）

### 测试文件
- `tests/LIB_Example/IP/` - IP库示例
- `tests/LIB_Example/MEM/` - MEM库示例（可能需要创建）

