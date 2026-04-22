# skyseraph.github.io

> AI for All — SkySeraph 的个人技术博客

🌐 **[skyseraph.github.io](https://skyseraph.github.io)**

---

## 技术栈

| | |
|---|---|
| 框架 | [Hugo](https://gohugo.io/) |
| 主题 | 自研 `skyseraph` theme |
| 部署 | GitHub Pages |
| 图床 | jsDelivr CDN（`static/images/`） |
| 评论 | [Giscus](https://giscus.app/)（基于 GitHub Discussions） |

## 内容结构

```
content/
├── posts/        # 技术文章
├── series/       # 专栏系列
├── projects/     # 作品展示
├── about.md      # 关于页
└── links.md      # 友链
```

## 本地开发

```bash
# 启动开发服务器
hugo server -D

# 构建
hugo
```

## 写作工作流

**新建文章**

```bash
hugo new posts/your-post-title.md
```

**粘贴图片**（VS Code + [Paste Image](https://marketplace.visualstudio.com/items?itemName=mushan.vscode-paste-image) 插件）

```
Ctrl+Alt+V  →  自动保存到 static/images/ 并插入本地路径
```

**发布前替换图片为 CDN URL**

```bash
node scripts/img-to-cdn.js
```

**提交推送**

```bash
git add .
git commit -m "post: 文章标题"
git push
```

GitHub Actions 自动构建并部署到 GitHub Pages。

## 目录说明

```
.
├── content/          # 内容文件
├── static/
│   └── images/       # 图片资源（jsDelivr CDN 分发）
├── themes/skyseraph/ # 自研主题
├── scripts/
│   └── img-to-cdn.js # 本地图片路径 → CDN URL 替换脚本
└── hugo.toml         # 站点配置
```

## License

内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议，主题代码采用 [MIT](LICENSE) 协议。
