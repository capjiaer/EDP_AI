# EDP 快速开始指南

## 新开 bash 后，首次使用 edp 的步骤

### 方法 1: 一键安装（最简单，推荐）

**只需要一行命令：**

```bash
# 使用绝对路径，source 安装脚本
source /path/to/EDP_AI/edp_center/bin/install.sh
```

或者：

```bash
# 使用相对路径（需要先进入项目目录）
cd /path/to/EDP_AI
source edp_center/bin/install.sh
```

**就这么简单！** 脚本会自动完成：
- ✅ 设置 PATH（添加到 ~/.bashrc）

**安装完成后，直接使用：**

```bash
edp --help
```

### 方法 2: 分步设置（如果需要手动控制）

#### 步骤 1: 确保 edp 命令可用

```bash
# 检查 edp 是否在 PATH 中
which edp

# 如果显示路径，说明已配置好，可以直接使用
# 如果显示 "command not found"，需要添加到 PATH
```

如果 `edp` 不在 PATH 中：

```bash
# 使用绝对路径执行设置脚本
bash /path/to/EDP_AI/edp_center/bin/setup_path.sh

# 重新加载配置
source ~/.bashrc

# 验证
which edp
```

#### 步骤 2: 验证一切正常

```bash
# 测试 edp 命令
edp --help
```

## 常见问题

### Q: 为什么 `edp` 命令找不到？

A: 需要将 `edp_center/bin` 添加到 PATH：
```bash
bash edp_center/bin/setup_path.sh
source ~/.bashrc
```


## 推荐的工作流程

1. **首次使用**：
   ```bash
   # 设置 PATH（如果还没设置）
   bash edp_center/bin/setup_path.sh
   source ~/.bashrc
   ```

2. **日常使用**：
   ```bash
   # 直接使用 edp 命令
   edp --help
   edp -init --project dongting
   edp -run pv_calibre.ipmerge
   ```

