# SkySeraph

> AI for All — SkySeraph 的个人技术博客 / Personal Tech Blog

🌐 **[skyseraph.github.io](https://skyseraph.github.io)**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-deployed-brightgreen?logo=github)](https://skyseraph.github.io)
[![Hugo](https://img.shields.io/badge/Hugo-static%20site-FF4088?logo=hugo)](https://gohugo.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Content: CC BY-NC-SA 4.0](https://img.shields.io/badge/Content-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

## 技术栈 / Tech Stack

| | |
|---|---|
| 框架 / Framework | [Hugo](https://gohugo.io/) |
| 主题 / Theme | 自研 `skyseraph` theme |
| 部署 / Deploy | GitHub Pages |
| 图床 / CDN | jsDelivr（`static/images/`） |
| 评论 / Comments | [Giscus](https://giscus.app/)（GitHub Discussions） |

## 内容结构 / Content Structure

```
content/
├── posts/        # 技术文章 / Articles
├── series/       # 专栏系列 / Series
├── projects/     # 作品展示 / Projects
├── about.md      # 关于 / About
└── links.md      # 友链 / Links
```

## 本地开发 / Local Development

```bash
# 启动开发服务器 / Start dev server
hugo server -D

# 构建 / Build
hugo
```

## 写作工作流 / Writing Workflow

**新建文章 / New post**

```bash
hugo new posts/your-post-title.md
```

**粘贴图片 / Paste image**（VS Code + [Paste Image](https://marketplace.visualstudio.com/items?itemName=mushan.vscode-paste-image)）

```
Ctrl+Alt+V  →  自动保存到 static/images/ / Auto-saved to static/images/
```

**替换图片为 CDN URL / Replace images with CDN URLs**

```bash
node scripts/img-to-cdn.js
```

**提交推送 / Commit & push**

```bash
git add .
git commit -m "post: 文章标题"
git push
```

GitHub Actions 自动构建并部署 / Auto build and deploy via GitHub Actions.

## 目录说明 / Directory

```
.
├── content/          # 内容文件 / Content
├── static/
│   └── images/       # 图片资源 / Images (jsDelivr CDN)
├── themes/skyseraph/ # 自研主题 / Custom theme
├── scripts/
│   └── img-to-cdn.js # 图片路径替换脚本 / Image CDN replace script
└── hugo.toml         # 站点配置 / Site config
```

## License

- 主题代码 / Theme code: [MIT](LICENSE)
- 博客内容 / Blog content: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
