# edp_dirkit 测试

## 测试覆盖

### 已实现的测试

1. **test_project_finder.py** - 项目查找功能测试
   - ✅ 单个匹配查找
   - ✅ 多个匹配查找
   - ✅ 项目不存在处理
   - ✅ 获取项目信息
   - ✅ 列出所有项目
   - ✅ 按 foundry/node 过滤

## 运行测试

### 使用 pytest（推荐）

```bash
# 运行所有测试
pytest edp_center/packages/edp_dirkit/tests/ -v

# 运行特定测试文件
pytest edp_center/packages/edp_dirkit/tests/test_project_finder.py -v
```

### 使用 unittest

```bash
# 运行所有测试
python -m unittest discover edp_center/packages/edp_dirkit/tests/ -v
```

### 使用测试运行脚本

```bash
python edp_center/packages/edp_dirkit/tests/run_tests.py
```

## 测试覆盖率

当前测试覆盖率：**~20%**

### 待补充的测试

- [ ] `work_path_initializer.py` - 工作路径初始化测试
- [ ] `initializer.py` - 项目初始化测试
- [ ] `path_detector.py` - 路径检测测试
- [ ] `branch_linker.py` - 分支链接测试
- [ ] `branch_source.py` - 分支源测试

## 测试最佳实践

1. **使用临时目录**：每个测试使用 `tempfile.mkdtemp()` 创建临时目录
2. **清理资源**：在 `tearDown` 中清理临时文件
3. **测试边界情况**：包括路径不存在、配置缺失等情况
4. **测试错误处理**：验证异常和错误信息

