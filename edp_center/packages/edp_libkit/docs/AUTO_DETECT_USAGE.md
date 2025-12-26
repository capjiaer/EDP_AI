# ⚠️ 自动检测功能已废弃

## 重要提示

**自动检测库类型功能已被移除**。现在要求用户通过 `--lib-type` 参数明确指定库类型（STD/IP/MEM）。

## 为什么移除自动检测？

1. **目录命名不统一**：不是所有STD库都以 `v-logic_` 开头
2. **更可靠**：明确指定避免了误识别
3. **更灵活**：支持任意目录结构，不依赖命名约定

## 新的使用方式

### ✅ 推荐方式：明确指定库类型

```bash
# 处理STD库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output

# 处理IP库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type IP \
  --node ln08lpu_gp \
  --output-dir /path/to/output

# 处理MEM库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type MEM \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

## 相关文档

- [使用指南](USAGE.md) - 详细的使用说明
- [快速开始](../QUICK_START.md) - 快速开始指南
- [架构设计](ARCHITECTURE.md) - 架构设计文档
