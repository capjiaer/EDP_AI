# JavaScript 库文件

本目录存放教程 HTML 所需的 JavaScript 库文件，用于离线环境（无法访问 CDN 时）。

## 需要的库文件

1. **marked.min.js** - Markdown 解析库
   - 版本: 11.1.1
   - CDN: https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js

2. **purify.min.js** - HTML 清理库（DOMPurify）
   - 版本: 3.0.6
   - CDN: https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js

## 下载方法

### 方法 1: 使用 wget/curl（Linux/Mac）

```bash
# 进入 libs 目录
cd /path/to/EDP_AI/edp_center/tutorial/libs

# 下载 marked.js
wget https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js

# 下载 DOMPurify
wget https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js
```

### 方法 2: 使用 curl

```bash
cd /path/to/EDP_AI/edp_center/tutorial/libs

curl -o marked.min.js https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js
curl -o purify.min.js https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js
```

### 方法 3: 使用浏览器下载

1. 打开浏览器，访问以下 URL：
   - https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js
   - https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js

2. 保存文件到 `edp_center/tutorial/libs/` 目录

## 验证

下载完成后，确保以下文件存在：

```bash
ls -lh edp_center/tutorial/libs/
# 应该看到：
# marked.min.js
# purify.min.js
```

## 工作原理

- 如果 `libs/` 目录中存在这些文件，HTML 会使用本地文件（离线可用）
- 如果不存在，HTML 会回退到使用 CDN（需要网络连接）

## 注意事项

- 这些库文件需要由 PM 下载并提交到代码库
- 文件大小约 100-200 KB，不会显著增加代码库大小
- 建议将这些文件添加到版本控制中，确保所有用户都能离线使用教程

