# edp_cmdkit 测试

## 测试覆盖

### 已实现的测试

1. **test_file_finder.py** - 文件查找功能测试
   - ✅ 绝对路径查找
   - ✅ 相对路径查找
   - ✅ 搜索路径查找
   - ✅ 递归查找
   - ✅ 文件不存在处理

2. **test_source_generator.py** - Source 语句生成测试
   - ✅ 生成 source 语句
   - ✅ 文件不存在异常处理
   - ✅ 错误信息详细性

3. **test_hooks_handler.py** - Hooks 处理测试
   - ✅ Hook 文件空检查
   - 注意：已移除 #import util 机制，util hooks 相关测试已删除

4. **test_cmd_processor.py** - CmdProcessor 核心功能测试
   - ✅ #import source 处理
   - ✅ 多个 import 处理
   - ✅ 嵌套 import 处理
   - ✅ 输出文件处理
   - 注意：已移除 #import util 机制，相关测试已更新

## 运行测试

### 使用 pytest（推荐）

```bash
# 运行所有测试
pytest edp_center/packages/edp_cmdkit/tests/ -v

# 运行特定测试文件
pytest edp_center/packages/edp_cmdkit/tests/test_file_finder.py -v

# 运行特定测试方法
pytest edp_center/packages/edp_cmdkit/tests/test_file_finder.py::TestFileFinder::test_find_absolute_path -v
```

### 使用 unittest

```bash
# 运行所有测试
python -m unittest discover edp_center/packages/edp_cmdkit/tests/ -v

# 运行特定测试文件
python -m unittest edp_center.packages.edp_cmdkit.tests.test_file_finder -v
```

### 使用测试运行脚本

```bash
python edp_center/packages/edp_cmdkit/tests/run_tests.py
```

## 测试覆盖率

当前测试覆盖率：**~60%**

### 已实现的测试

5. **test_sub_steps_handler.py** - Sub_steps 处理测试
   - ✅ 生成 sub_step pre proc
   - ✅ 从 dependency.yaml 读取 sub_steps（字典/列表格式）
   - ✅ 项目覆盖 common 的 sub_steps
   - ✅ sub_step.pre/replace hooks
   - ✅ 生成 sub_steps source 和调用

6. **test_package_loader.py** - 包加载器测试
   - ✅ 初始化（有效/无效路径）
   - ✅ 查找项目信息
   - ✅ 解析脚本路径（common/project）
   - ✅ 获取 util 搜索路径

7. **test_content_assembler.py** - 内容组装测试 ✅ **新增**
   - ✅ 整合 step.pre/post hooks
   - ✅ 验证 sub_steps 之间的 #import 指令
   - ✅ 空 hooks 处理
   - ✅ 文件不存在异常处理

### 待补充的测试

- [ ] `debug_mode_handler.py` - Debug 模式测试
- [ ] `debug_execution_plan.py` - Debug 执行计划测试
- [ ] `CmdProcessor` 的 hooks 集成测试
- [ ] `CmdProcessor` 的 sub_steps 集成测试

## 测试最佳实践

1. **使用临时目录**：每个测试使用 `tempfile.mkdtemp()` 创建临时目录
2. **清理资源**：在 `tearDown` 中清理临时文件
3. **测试边界情况**：包括文件不存在、空文件等情况
4. **测试错误处理**：验证异常和错误信息

