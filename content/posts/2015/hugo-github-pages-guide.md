---
title: "Hugo 博客搭建指南：从零到 GitHub Pages"
date: 2015-12-01
categories: ["技术"]
tags: ["博客"]
toc: true
---

> 作者：skyseraph  
> 日期：2015-12-01  
> 原文链接：[Hugo 博客搭建指南](https://skyseraph.github.io/posts/2015/hugo-github-pages-guide/)  

---

## 前言

本文记录如何使用 Hugo 搭建个人技术博客并部署到 GitHub Pages，全程只需要 Markdown 写作，推送代码后自动构建发布。

## 为什么选择 Hugo

- 构建速度极快，千篇文章秒级完成
- 单二进制文件，无依赖
- 主题生态丰富
- 原生支持 GitHub Actions 部署

## 安装 Hugo

```bash
# macOS
brew install hugo

# Windows
winget install Hugo.Hugo.Extended

# 验证
hugo version
```

## 创建站点

```bash
hugo new site myblog
cd myblog
```

## 目录结构

```
myblog/
├── content/        # Markdown 文章
├── themes/         # 主题
├── static/         # 静态资源
├── layouts/        # 模板覆盖
└── hugo.toml       # 配置文件
```

## 写作流程

新建文章：

```bash
hugo new posts/my-first-post.md
```

文章 Front Matter 示例：

```yaml
---
title: "文章标题"
date: 2024-01-15
tags: ["tag1", "tag2"]
categories: ["分类"]
toc: true
---
```

## 本地预览

```bash
hugo server -D
```

访问 `http://localhost:1313` 即可预览。

## 部署到 GitHub Pages

推送到 `main` 分支后，GitHub Actions 自动构建并部署，详见 `.github/workflows/deploy.yml`。

## 总结

Hugo + GitHub Pages + GitHub Actions 是目前最简洁的静态博客方案之一，写作体验极佳。
