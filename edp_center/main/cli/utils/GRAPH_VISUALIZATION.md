# 依赖关系可视化功能使用说明

## 功能概述

依赖关系可视化功能可以帮助你直观地查看工作流中步骤之间的依赖关系，支持多种输出格式。

## 基本用法

### 1. 文本树形图（默认）

```bash
# 显示所有步骤的依赖关系（文本格式）
edp -graph -prj dongting --foundry SAMSUNG --node S8

# 保存到文件
edp -graph -prj dongting --foundry SAMSUNG --node S8 --output graph.txt
```

### 2. Graphviz 图片格式

```bash
# 生成 PNG 图片
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format png --output graph.png

# 生成 SVG 图片
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format svg --output graph.svg

# 生成 DOT 格式（可以手动编辑）
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format dot --output graph.dot
```

**注意**：生成图片需要安装 `graphviz` 库：
```bash
pip install graphviz
# 还需要安装系统级的 Graphviz 工具
# Ubuntu/Debian: sudo apt-get install graphviz
# macOS: brew install graphviz
# Windows: 下载安装 https://graphviz.org/download/
```

### 3. Mermaid 图表格式

```bash
# 生成 Mermaid 图表（可以在 Markdown 中显示）
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format mermaid --output graph.md
```

生成的 Mermaid 图表可以直接在支持 Mermaid 的 Markdown 查看器中显示（如 GitHub、GitLab、Typora 等）。

### 4. Web 交互式可视化（推荐）

```bash
# 生成交互式 HTML 文件
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format web --output graph.html

# 自动打开浏览器
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format web --output graph.html --open-browser
```

Web 可视化支持：
- 拖拽节点
- 缩放和平移
- 鼠标悬停查看详细信息
- 力导向图自动布局

## 高级用法

### 聚焦特定步骤

只显示与指定步骤相关的依赖关系：

```bash
# 只显示 pv_calibre.ipmerge 及其相关步骤
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --focus-step pv_calibre.ipmerge --format web
```

### 限制深度

只显示指定深度的依赖关系：

```bash
# 只显示 2 层深度的依赖关系
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --depth 2 --format web
```

### 只显示特定 Flow

```bash
# 只显示 pv_calibre flow 的步骤
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --flow pv_calibre --format web
```

### 自定义布局（仅图片格式）

```bash
# 使用不同的布局引擎
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format png --layout fdp --output graph.png
```

可用的布局引擎：
- `dot`（默认）：层次化布局，适合有向图
- `neato`：弹簧模型布局
- `fdp`：力导向布局
- `sfdp`：大型图的力导向布局
- `twopi`：径向布局
- `circo`：圆形布局

### 自定义标题（仅 Web 格式）

```bash
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format web --title "项目依赖关系图" --output graph.html
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-graph` | 启用依赖关系可视化 | - |
| `--format` | 输出格式：text, dot, png, svg, pdf, mermaid, web | text |
| `--output` | 输出文件路径 | 控制台输出或默认文件名 |
| `--focus-step` | 聚焦的步骤名称 | 显示所有步骤 |
| `--depth` | 深度限制 | 无限制 |
| `--flow` | 只显示指定 flow 的步骤 | 显示所有 flow |
| `--layout` | Graphviz 布局引擎（仅图片格式） | dot |
| `--title` | 图表标题（仅 Web 格式） | "EDP 依赖关系图" |
| `--open-browser` | 自动打开浏览器（仅 Web 格式） | false |

## 使用示例

### 示例 1：快速查看依赖关系

```bash
# 在项目目录下运行，自动推断参数
cd /path/to/work/dongting/P85/block1/user1/branch1
edp -graph --format text
```

### 示例 2：生成文档用的图表

```bash
# 生成 Mermaid 图表，插入到文档中
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format mermaid --output docs/dependency_graph.md
```

### 示例 3：分析特定步骤的影响范围

```bash
# 查看修改 pnr_innovus.place 会影响哪些步骤
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --focus-step pnr_innovus.place --format web --open-browser
```

### 示例 4：生成高质量图片用于报告

```bash
# 生成 SVG 格式（矢量图，可缩放）
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format svg --layout dot --output report/dependency_graph.svg
```

## 输出格式对比

| 格式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| text | 快速、无需依赖 | 不够直观 | 快速查看、终端使用 |
| dot | 可编辑、可转换 | 需要 Graphviz | 需要自定义编辑 |
| png/svg/pdf | 高质量、可打印 | 需要 Graphviz | 报告、文档 |
| mermaid | Markdown 兼容 | 功能有限 | 文档、Wiki |
| web | 交互式、最直观 | 需要浏览器 | 分析、演示 |

## 故障排除

### 问题：生成图片失败

**原因**：未安装 Graphviz 或 Python graphviz 库

**解决**：
```bash
# 安装 Python 库
pip install graphviz

# 安装系统工具（Ubuntu/Debian）
sudo apt-get install graphviz

# 安装系统工具（macOS）
brew install graphviz
```

### 问题：Web 可视化无法打开

**原因**：浏览器不支持或文件路径问题

**解决**：
- 使用 `--open-browser` 自动打开
- 或手动在浏览器中打开生成的 HTML 文件

### 问题：找不到步骤

**原因**：项目参数不正确

**解决**：
- 确保 `--project`, `--foundry`, `--node` 参数正确
- 或在项目目录下运行，让系统自动推断

## 技术细节

### 数据提取

可视化器会从 `Graph` 对象中提取：
- 步骤信息（名称、命令、输入输出文件）
- 依赖关系（前置步骤、后续步骤）
- 文件匹配关系（通过输入输出文件自动建立依赖）

### 布局算法

- **文本格式**：树形结构，从根节点开始
- **Graphviz**：使用 DOT 布局引擎
- **Web 格式**：使用 D3.js 力导向图算法

### 性能考虑

- 对于大型图（>100 个步骤），建议使用 `--focus-step` 或 `--depth` 限制范围
- Web 格式在浏览器中渲染，性能取决于浏览器和图的复杂度

