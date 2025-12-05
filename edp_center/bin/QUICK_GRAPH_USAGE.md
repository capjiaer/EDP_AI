# 依赖关系可视化 - 快速使用指南

## 🚀 最简单的使用方式

### 方式 1：使用现有项目配置（推荐）

根据你的项目配置，可以直接使用：

```bash
# 1. 文本格式（最简单，直接看）
edp -graph -prj dongting --foundry SAMSUNG --node S8

# 2. Web 交互式（最直观，推荐！）
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format web --open-browser

# 3. 生成图片
edp -graph -prj dongting --foundry SAMSUNG --node S8 --format png --output graph.png
```

### 方式 2：在项目目录下运行（自动推断参数）

如果你在项目工作目录下，系统会自动推断参数：

```bash
# 进入项目目录
cd /path/to/work/dongting/P85/block1/user1/branch1

# 直接运行（系统会自动推断 project, foundry, node）
edp -graph --format web --open-browser
```

## 📋 常用命令示例

### 1. 快速查看（文本树形图）
```bash
edp -graph -prj dongting --foundry SAMSUNG --node S8
```

输出示例：
```
└── pnr_innovus.place
    └── pnr_innovus.postroute
        └── pv_calibre.ipmerge
            └── pv_calibre.dummy
                └── pv_calibre.colorrtg
```

### 2. Web 交互式可视化（最推荐！）
```bash
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format web --output graph.html --open-browser
```

这会：
- 生成一个 HTML 文件
- 自动在浏览器中打开
- 支持拖拽、缩放、悬停查看详情

### 3. 只查看特定 flow
```bash
# 只看 pv_calibre flow
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --flow pv_calibre --format web --open-browser
```

### 4. 聚焦特定步骤（看影响范围）
```bash
# 查看 pv_calibre.ipmerge 的依赖关系
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --focus-step pv_calibre.ipmerge --format web --open-browser
```

### 5. 生成图片用于文档
```bash
# SVG 格式（矢量图，可缩放）
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format svg --output dependency.svg

# PNG 格式（位图）
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format png --output dependency.png
```

**注意**：生成图片需要安装 Graphviz：
```bash
pip install graphviz
# 还需要系统级工具（Ubuntu: sudo apt-get install graphviz）
```

### 6. Mermaid 格式（用于 Markdown）
```bash
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --format mermaid --output graph.md
```

生成的 Mermaid 图表可以直接在 GitHub、GitLab 等平台显示。

## 🎯 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-graph` | 启用可视化 | 必需 |
| `-prj` | 项目名称 | `-prj dongting` |
| `--foundry` | 代工厂 | `--foundry SAMSUNG` |
| `--node` | 工艺节点 | `--node S8` |
| `--format` | 输出格式 | `--format web` |
| `--output` | 输出文件 | `--output graph.html` |
| `--open-browser` | 自动打开浏览器 | `--open-browser` |
| `--flow` | 只显示指定 flow | `--flow pv_calibre` |
| `--focus-step` | 聚焦步骤 | `--focus-step pv_calibre.ipmerge` |
| `--depth` | 深度限制 | `--depth 2` |

## 💡 推荐使用流程

1. **第一次使用**：先用文本格式快速看看
   ```bash
   edp -graph -prj dongting --foundry SAMSUNG --node S8
   ```

2. **详细分析**：用 Web 格式交互式查看
   ```bash
   edp -graph -prj dongting --foundry SAMSUNG --node S8 \
       --format web --open-browser
   ```

3. **生成文档**：用图片或 Mermaid 格式
   ```bash
   edp -graph -prj dongting --foundry SAMSUNG --node S8 \
       --format svg --output docs/dependency.svg
   ```

## ❓ 常见问题

### Q: 提示"缺少必需参数"怎么办？

**A**: 有两种方式：
1. 手动指定参数：`-prj dongting --foundry SAMSUNG --node S8`
2. 在项目目录下运行，系统会自动推断

### Q: 生成图片失败？

**A**: 需要安装 Graphviz：
```bash
pip install graphviz
# Ubuntu/Debian: sudo apt-get install graphviz
# macOS: brew install graphviz
```

### Q: Web 格式打不开？

**A**: 
- 使用 `--open-browser` 自动打开
- 或手动在浏览器中打开生成的 HTML 文件

### Q: 图太大看不清？

**A**: 使用 `--focus-step` 或 `--depth` 限制范围：
```bash
# 只看特定步骤
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --focus-step pv_calibre.ipmerge --format web

# 限制深度
edp -graph -prj dongting --foundry SAMSUNG --node S8 \
    --depth 2 --format web
```

## 🎨 输出格式对比

- **text**：最快，终端直接看，无需依赖
- **web**：最直观，交互式，推荐日常使用
- **png/svg**：适合报告和文档
- **mermaid**：适合 Markdown 文档

现在就试试吧！🎉

