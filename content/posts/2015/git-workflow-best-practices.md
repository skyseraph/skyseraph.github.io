---
title: "Git 工作流最佳实践"
date: 2015-12-01
categories: ["技术"]
tags: ["Git", "工程效率"]
toc: true
---

> 作者：skyseraph  
> 日期：2015-12-01  
> 原文链接：[Git 工作流最佳实践](https://skyseraph.github.io/posts/2015/git-workflow-best-practices/)  

---

## 分支策略

推荐使用 Git Flow 或简化版的 GitHub Flow：

```
main        # 生产分支，始终可部署
develop     # 开发分支
feature/*   # 功能分支
hotfix/*    # 紧急修复
```

## 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新增用户登录功能
fix: 修复首页加载闪烁问题
docs: 更新 README
refactor: 重构认证模块
chore: 升级依赖版本
```

## 常用命令速查

```bash
# 查看简洁日志
git log --oneline --graph --all

# 交互式暂存
git add -p

# 修改最近一次提交
git commit --amend --no-edit

# 撤销工作区修改
git restore <file>

# 储藏当前修改
git stash push -m "描述"
git stash pop
```

## .gitignore 模板

```gitignore
# Hugo
public/
resources/
.hugo_build.lock

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
```

## 小结

好的 Git 习惯能大幅降低协作成本，提交信息写清楚，未来的自己会感谢你。
