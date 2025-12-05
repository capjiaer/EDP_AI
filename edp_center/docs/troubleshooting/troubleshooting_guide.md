# 故障排查指南

本文档提供系统化的故障排查流程和常见问题的解决方案。

## 📋 目录

- [故障排查流程](#故障排查流程)
- [常见问题](#常见问题)
- [错误代码参考](#错误代码参考)
- [日志分析](#日志分析)
- [性能问题](#性能问题)
- [获取帮助](#获取帮助)

---

## 故障排查流程

### 1. 收集信息

在开始排查之前，收集以下信息：

- **错误消息**：完整的错误消息和堆栈跟踪
- **环境信息**：
  - Python 版本
  - 操作系统
  - EDP_AI 版本
- **复现步骤**：详细的操作步骤
- **相关文件**：配置文件、脚本文件等
- **日志文件**：相关日志文件

### 2. 检查常见问题

参考 [常见问题](#常见问题) 部分，查看是否有类似问题。

### 3. 查看日志

检查日志文件获取更多信息：

```bash
# 查看运行日志
cat logs/pnr_innovus.place/edp_run_*.log

# 查看错误日志
grep -i error logs/**/*.log
```

### 4. 验证配置

检查配置文件是否正确：

```bash
# 检查配置文件语法
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# 检查配置路径
edp -info --check-config
```

### 5. 简化问题

尝试简化问题：

- 使用最小复现示例
- 禁用不必要的功能
- 检查是否有其他因素影响

### 6. 搜索已知问题

- 搜索 GitHub Issues
- 查看文档和 FAQ
- 搜索错误消息

### 7. 获取帮助

如果问题仍未解决，参考 [获取帮助](#获取帮助) 部分。

---

## 常见问题

### 安装和配置

#### Q1: `edp` 命令找不到

**症状：**
```bash
$ edp --help
bash: edp: command not found
```

**原因：**
- `edp_center/bin` 目录未添加到 PATH

**解决方案：**

1. **检查 PATH**
   ```bash
   echo $PATH | grep edp_center
   ```

2. **添加到 PATH**
   ```bash
   # Bash/Zsh
   export PATH="$PATH:/path/to/EDP_AI/edp_center/bin"
   echo 'export PATH="$PATH:/path/to/EDP_AI/edp_center/bin"' >> ~/.bashrc
   
   # Csh/Tcsh
   setenv PATH "${PATH}:/path/to/EDP_AI/edp_center/bin"
   echo 'setenv PATH "${PATH}:/path/to/EDP_AI/edp_center/bin"' >> ~/.cshrc
   ```

3. **使用安装脚本**
   ```bash
   cd /path/to/EDP_AI/edp_center/bin
   source install.sh
   ```

#### Q2: 配置文件加载失败

**症状：**
```
ERROR: Failed to load config file: config.yaml
YAMLError: ...
```

**原因：**
- YAML 语法错误
- 文件路径错误
- 文件权限问题

**解决方案：**

1. **检查 YAML 语法**
   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **检查文件路径**
   ```bash
   ls -la config.yaml
   ```

3. **检查文件权限**
   ```bash
   chmod 644 config.yaml
   ```

#### Q3: 项目初始化失败

**症状：**
```
ERROR: Project initialization failed
FileNotFoundError: ...
```

**原因：**
- 工作路径不存在
- 权限不足
- 配置文件错误

**解决方案：**

1. **检查工作路径**
   ```bash
   ls -la WORK_PATH/
   ```

2. **检查权限**
   ```bash
   ls -ld WORK_PATH/
   chmod 755 WORK_PATH/
   ```

3. **检查配置文件**
   ```bash
   cat WORK_PATH/config.yaml
   ```

---

### 脚本处理

#### Q4: `#import source` 指令无法找到文件

**症状：**
```
WARNING: File not found: helper.tcl
```

**原因：**
- 文件路径错误
- 搜索路径配置错误
- 文件不存在

**解决方案：**

1. **检查文件是否存在**
   ```bash
   find . -name "helper.tcl"
   ```

2. **检查搜索路径**
   ```bash
   edp -info --show-search-paths
   ```

3. **添加搜索路径**
   ```bash
   edp -run step_name --search-paths /path/to/helpers
   ```

#### Q5: Hooks 文件未生效

**症状：**
- Hooks 文件存在但未执行
- Hooks 代码未插入到脚本中

**原因：**
- Hooks 文件位置错误
- Hooks 文件格式错误
- Hooks 文件为空

**解决方案：**

1. **检查 Hooks 文件位置**
   ```
   hooks/
   └── pnr_innovus.place/
       ├── step.pre
       ├── step.post
       └── innovus_config_design.tcl.pre
   ```

2. **检查文件格式**
   ```bash
   cat hooks/pnr_innovus.place/step.pre
   ```

3. **检查文件是否为空**
   ```bash
   wc -l hooks/pnr_innovus.place/step.pre
   ```

---

### 工作流执行

#### Q6: 步骤执行失败

**症状：**
```
ERROR: Step execution failed
Command failed with exit code 1
```

**原因：**
- 命令执行错误
- 依赖未满足
- 资源不足

**解决方案：**

1. **检查命令**
   ```bash
   cat runs/pnr_innovus.place/full.tcl
   ```

2. **检查依赖**
   ```bash
   edp -info --show-dependencies pnr_innovus.place
   ```

3. **检查日志**
   ```bash
   tail -100 logs/pnr_innovus.place/edp_run_*.log
   ```

#### Q7: 依赖关系错误

**症状：**
```
ERROR: Dependency not satisfied: pnr_innovus.init
```

**原因：**
- 前置步骤未执行
- 依赖配置错误
- 步骤状态文件损坏

**解决方案：**

1. **检查前置步骤状态**
   ```bash
   edp -info --step-status pnr_innovus.init
   ```

2. **检查依赖配置**
   ```bash
   cat config/SAMSUNG/S8/common/pnr_innovus/dependency.yaml
   ```

3. **重新执行前置步骤**
   ```bash
   edp -run pnr_innovus.init
   ```

---

### 性能问题

#### Q8: 脚本处理速度慢

**症状：**
- 脚本处理时间过长
- 大型项目处理缓慢

**原因：**
- 文件搜索未缓存
- 配置文件过多
- 递归搜索深度过大

**解决方案：**

1. **检查文件搜索**
   ```bash
   # 启用调试模式查看搜索路径
   edp -run step_name --debug
   ```

2. **优化搜索路径**
   ```bash
   # 使用更具体的搜索路径
   edp -run step_name --search-paths /specific/path
   ```

3. **减少配置文件数量**
   - 合并配置文件
   - 移除不必要的配置

#### Q9: 内存占用过高

**症状：**
- 内存使用持续增长
- 大型项目内存不足

**原因：**
- 文件缓存未清理
- 配置合并占用内存
- 脚本内容过大

**解决方案：**

1. **清理缓存**
   ```bash
   # 删除临时文件
   rm -rf runs/**/full.tcl
   ```

2. **优化配置**
   - 减少配置层级
   - 移除不必要的配置项

---

## 错误代码参考

### 配置错误 (1000-1999)

| 错误代码 | 描述 | 解决方案 |
|---------|------|---------|
| 1001 | 配置文件未找到 | 检查文件路径和权限 |
| 1002 | YAML 语法错误 | 验证 YAML 语法 |
| 1003 | 配置项缺失 | 检查必需配置项 |
| 1004 | 配置值无效 | 检查配置值格式和范围 |

### 文件错误 (2000-2999)

| 错误代码 | 描述 | 解决方案 |
|---------|------|---------|
| 2001 | 文件未找到 | 检查文件路径和搜索路径 |
| 2002 | 文件权限不足 | 检查文件权限 |
| 2003 | 文件读取失败 | 检查文件格式和编码 |
| 2004 | 文件写入失败 | 检查目录权限和磁盘空间 |

### 脚本处理错误 (3000-3999)

| 错误代码 | 描述 | 解决方案 |
|---------|------|---------|
| 3001 | #import 指令错误 | 检查指令语法和文件路径 |
| 3002 | Hooks 处理失败 | 检查 Hooks 文件格式 |
| 3003 | Sub_steps 处理失败 | 检查 dependency.yaml 配置 |
| 3004 | 脚本生成失败 | 检查脚本内容和格式 |

### 工作流错误 (4000-4999)

| 错误代码 | 描述 | 解决方案 |
|---------|------|---------|
| 4001 | 依赖未满足 | 执行前置步骤 |
| 4002 | 步骤执行失败 | 检查命令和日志 |
| 4003 | 状态文件损坏 | 清理状态文件并重新执行 |
| 4004 | 并发执行冲突 | 检查资源锁定 |

---

## 日志分析

### 日志位置

```
WORK_PATH/{project}/{version}/{block}/{user}/{branch}/
├── logs/
│   └── {flow}.{step}/
│       ├── edp_run_YYYYMMDD_HHMMSS.log
│       └── old_logs/
└── runs/
    └── {flow}.{step}/
        └── full.tcl
```

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志分析技巧

1. **查找错误**
   ```bash
   grep -i error logs/**/*.log
   ```

2. **查找警告**
   ```bash
   grep -i warning logs/**/*.log
   ```

3. **查看时间线**
   ```bash
   grep "\[INFO\]" logs/**/*.log | tail -50
   ```

4. **分析性能**
   ```bash
   grep "elapsed" logs/**/*.log
   ```

---

## 性能问题

### 性能指标

- **脚本处理时间**: < 5 秒（小型项目）
- **配置加载时间**: < 1 秒
- **文件搜索时间**: < 2 秒（首次）
- **内存占用**: < 500 MB（小型项目）

### 性能优化建议

1. **文件搜索缓存**
   - 启用文件搜索缓存
   - 减少搜索路径数量

2. **配置优化**
   - 合并配置文件
   - 减少配置层级

3. **脚本优化**
   - 减少 #import 指令嵌套
   - 优化 Hooks 文件大小

---

## 获取帮助

### 文档资源

- [教程文档](../../tutorial/)
- [API 文档](../api/)
- [FAQ](../../tutorial/08_faq.md)

### 社区支持

- **GitHub Issues**: 报告问题和功能请求
- **GitHub Discussions**: 讨论和问答

### 报告问题

在报告问题时，请提供：

1. **错误消息**：完整的错误消息和堆栈跟踪
2. **环境信息**：Python 版本、操作系统、EDP_AI 版本
3. **复现步骤**：详细的操作步骤
4. **相关文件**：配置文件、脚本文件（如果可能）
5. **日志文件**：相关日志文件

---

**最后更新**: 2025-01-XX

