# 不安装直接运行指南

## ✅ 可以不用安装！

有两种方法可以直接运行，不需要 `pip install`：

---

## 方法 1：使用 Python 模块方式（推荐）

### Bash 用户：

```bash
# 1. 进入 edp_libkit 的父目录
cd /path/to/production

# 2. 设置 PYTHONPATH（让 Python 能找到 edp_libkit）
export PYTHONPATH=/path/to/production:$PYTHONPATH

# 3. 直接运行
python -m edp_libkit.cli gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v
```

### Tcsh/Csh 用户：

```tcsh
# 1. 进入 edp_libkit 的父目录
cd /path/to/production

# 2. 设置 PYTHONPATH（tcsh 语法）
setenv PYTHONPATH /path/to/production:$PYTHONPATH

# 3. 直接运行
python -m edp_libkit.cli gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v
```

### 或者一行命令（Bash）：

```bash
PYTHONPATH=/path/to/production python -m edp_libkit.cli gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori
```

### 或者一行命令（Tcsh）：

```tcsh
env PYTHONPATH=/path/to/production python -m edp_libkit.cli gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori
```

---

## 方法 2：直接运行 cli.py（需要小修改）

### Bash 用户：

```bash
# 1. 进入 edp_libkit 目录
cd /path/to/production/edp_libkit

# 2. 设置 PYTHONPATH
export PYTHONPATH=/path/to/production:$PYTHONPATH

# 3. 直接运行
python cli.py gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v
```

### Tcsh/Csh 用户：

```tcsh
# 1. 进入 edp_libkit 目录
cd /path/to/production/edp_libkit

# 2. 设置 PYTHONPATH（tcsh 语法）
setenv PYTHONPATH /path/to/production:$PYTHONPATH

# 3. 直接运行
python cli.py gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v
```

---

## 📝 完整示例

假设你把 `edp_libkit` 放到了 `/home/user/edp_libkit/`：

### Bash：

```bash
# 方法 1：模块方式（推荐）
cd /home/user
export PYTHONPATH=/home/user:$PYTHONPATH
python -m edp_libkit.cli gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v

# 方法 2：直接运行
cd /home/user/edp_libkit
export PYTHONPATH=/home/user:$PYTHONPATH
python cli.py gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v
```

### Tcsh：

```tcsh
# 方法 1：模块方式（推荐）
cd /home/user
setenv PYTHONPATH /home/user:$PYTHONPATH
python -m edp_libkit.cli gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v

# 方法 2：直接运行
cd /home/user/edp_libkit
setenv PYTHONPATH /home/user:$PYTHONPATH
python cli.py gen-lib \
    --foundry Samsung \
    -o /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    -v
```

---

## 🎯 文件过滤工具（tests/）

`tests/` 目录下的脚本可以直接运行，不需要设置 PYTHONPATH：

```bash
cd /path/to/production/edp_libkit/tests
python get_dir_structure_filtered.py \
    /tech_1/designkit/Samsung/LN08LPU_GP/ori \
    output.txt \
    --filter pr_innovus
```

---

## ⚠️ 注意事项

1. **PYTHONPATH 设置**
   - **Bash**: 使用 `export PYTHONPATH=...`
   - **Tcsh**: 使用 `setenv PYTHONPATH ...`
   - 必须指向 `edp_libkit` 的**父目录**
   - 例如：如果 `edp_libkit` 在 `/home/user/edp_libkit/`，则 `PYTHONPATH=/home/user`

2. **依赖检查**
   - 仍然需要 `pyyaml`：`pip install pyyaml`（只需要安装这个依赖，不需要安装包本身）

3. **路径问题**
   - 确保目录结构正确：`edp_libkit/` 目录下有 `__init__.py`, `cli.py` 等文件

4. **Shell 差异**
   - Bash: `export VAR=value`
   - Tcsh: `setenv VAR value`
   - 一行命令：Bash 用 `VAR=value command`，Tcsh 用 `env VAR=value command`

---

## 🔍 快速测试

### Bash：

```bash
# 测试是否能导入
cd /path/to/production
export PYTHONPATH=/path/to/production:$PYTHONPATH
python -c "import edp_libkit; print('OK')"

# 测试运行
python -m edp_libkit.cli --help
```

### Tcsh：

```tcsh
# 测试是否能导入
cd /path/to/production
setenv PYTHONPATH /path/to/production:$PYTHONPATH
python -c "import edp_libkit; print('OK')"

# 测试运行
python -m edp_libkit.cli --help
```

---

## 💡 创建快捷脚本（可选）

### Bash 脚本：

```bash
# 创建 run_edp_libkit.sh
cat > /path/to/production/run_edp_libkit.sh << 'EOF'
#!/bin/bash
export PYTHONPATH="$(dirname "$0"):$PYTHONPATH"
python -m edp_libkit.cli "$@"
EOF

chmod +x /path/to/production/run_edp_libkit.sh

# 使用
./run_edp_libkit.sh gen-lib --foundry Samsung -o /path/to/ori
```

### Tcsh 脚本：

```tcsh
# 创建 run_edp_libkit.csh
cat > /path/to/production/run_edp_libkit.csh << 'EOF'
#!/bin/tcsh
setenv PYTHONPATH `dirname $0`:$PYTHONPATH
python -m edp_libkit.cli $argv
EOF

chmod +x /path/to/production/run_edp_libkit.csh

# 使用
./run_edp_libkit.csh gen-lib --foundry Samsung -o /path/to/ori
```

---

## ✅ 总结

**不需要安装！** 只需要：
1. 设置 `PYTHONPATH` 指向父目录
2. 使用 `python -m edp_libkit.cli` 运行
3. 确保安装了 `pyyaml` 依赖

就这么简单！🚀

