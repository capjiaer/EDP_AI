# 🎨 依赖关系可视化 - 快速开始

## 最简单的使用方式

### 方式 1：直接使用（推荐）

```bash
# 1. 进入 edp_center/bin 目录
cd /path/to/EDP_AI/edp_center/bin

# 2. 运行（使用你的项目配置）
./edp -graph -prj dongting --foundry SAMSUNG --node S8 --format web --open-browser
```

### 方式 2：如果 edp 命令已经在 PATH 中

```bash
# 直接运行
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format web --open-browser
```

## 🚀 三种最简单的用法

### 1️⃣ 文本格式（最快，直接看）

```bash
edp -graph -prj dongting --foundry SAMSUNG --node S8
```

**输出**：在终端显示树形依赖关系

### 2️⃣ Web 交互式（最推荐！）

```bash
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format web --output graph.html --open-browser
```

**效果**：
- ✅ 生成 HTML 文件
- ✅ 自动打开浏览器
- ✅ 可以拖拽节点
- ✅ 可以缩放
- ✅ 鼠标悬停查看详情

### 3️⃣ 生成图片

```bash
# PNG 图片
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format png --output graph.png

# SVG 矢量图（推荐，可缩放）
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format svg --output graph.svg
```

**注意**：生成图片需要先安装：
```bash
pip install graphviz
# Ubuntu: sudo apt-get install graphviz
# macOS: brew install graphviz
```

## 📝 完整命令示例

### 在项目目录下（推荐，最简单）

```bash
# 查看所有步骤的依赖关系
edp -graph --format web --open-browser

# 只看特定 flow
edp -graph --flow pv_calibre --format web --open-browser

# 聚焦特定步骤（看影响范围）
edp -graph --focus-step pv_calibre.ipmerge --format web --open-browser

# 限制深度（只看 2 层）
edp -graph --depth 2 --format web --open-browser

# 文本格式（最快）
edp -graph
```

### 不在项目目录下（需要指定参数）

```bash
# 查看所有步骤的依赖关系
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format web --open-browser

# 只看特定 flow
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --flow pv_calibre --format web --open-browser

# 聚焦特定步骤
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --focus-step pv_calibre.ipmerge --format web --open-browser
```

## 🎯 参数速查

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `-graph` | ✅ | 启用可视化 | - |
| `-prj` | ⚠️ | 项目名（在项目目录下可自动推断） | `-prj dongting` |
| `--foundry` | ⚠️ | 代工厂（在项目目录下可自动推断） | `--foundry SAMSUNG` |
| `--node` | ⚠️ | 工艺节点（在项目目录下可自动推断） | `--node S8` |
| `--format` | ❌ | 格式：text/web/png/svg/mermaid | `--format web` |
| `--output` | ❌ | 输出文件 | `--output graph.html` |
| `--open-browser` | ❌ | 自动打开浏览器 | `--open-browser` |
| `--flow` | ❌ | 只显示指定 flow | `--flow pv_calibre` |
| `--focus-step` | ❌ | 聚焦步骤 | `--focus-step pv_calibre.ipmerge` |
| `--depth` | ❌ | 深度限制 | `--depth 2` |

**注意**：如果在项目目录下运行，`-prj`、`--foundry`、`--node` 都可以自动推断，不需要手动指定！

## 💡 推荐使用流程

1. **第一次用**：先试试文本格式，看看效果
   ```bash
   edp -graph -prj dongting --foundry SAMSUNG --node S8
   ```

2. **详细分析**：用 Web 格式，交互式查看
   ```bash
   edp -graph -prj dongting --foundry SAMSUNG --node S8 \
       --format web --open-browser
   ```

3. **生成文档**：用图片格式
   ```bash
   edp -graph -prj dongting --foundry SAMSUNG --node S8 \
       --format svg --output dependency.svg
   ```

## ❓ 常见问题

### Q: 提示"缺少必需参数"？

**A**: 确保提供了这三个参数：
- `-prj dongting`（项目名）
- `--foundry SAMSUNG`（代工厂）
- `--node S8`（工艺节点）

### Q: 找不到 edp 命令？

**A**: 
1. 进入 `edp_center/bin` 目录，使用 `./edp`
2. 或者运行 `source edp_env.sh`（bash）或 `source edp_env.csh`（csh）

### Q: 生成图片失败？

**A**: 需要安装 Graphviz：
```bash
pip install graphviz
# 还需要系统工具（见上面的安装命令）
```

### Q: Web 格式打不开？

**A**: 
- 使用 `--open-browser` 自动打开
- 或手动打开生成的 HTML 文件

## 🎉 现在就试试！

### 最简单的命令（在项目目录下）：

```bash
# 1. 进入项目目录
cd /path/to/work/dongting/P85/block1/user1/branch1

# 2. 运行（不需要任何参数！）
edp -graph --format web --open-browser
```

就这么简单！系统会自动推断所有参数，生成一个交互式的依赖关系图，在浏览器中打开，你可以：
- 🖱️ 拖拽节点
- 🔍 缩放查看
- 📊 悬停查看详细信息
- 🔗 查看依赖关系

### 或者更简单（文本格式）：

```bash
cd /path/to/work/dongting/P85/block1/user1/branch1
edp -graph
```

直接在终端显示依赖关系树！

享受可视化带来的便利吧！✨

