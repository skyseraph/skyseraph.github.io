---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ now.Format "2006-01-02T15:04:05+08:00" }}
# 事件类型（event）：model 模型发布 / product 产品更新 / paper 论文研究 / funding 融资收购 / policy 政策监管 / agent 智能体
event: "model"
# 封面图：支持外链，或走 imageBase CDN 的相对路径（static/images/xxx.jpg）
cover: ""
# 视频：B 站 / YouTube 视频 ID（与 cover 同时存在时，卡片优先展示视频）
video: ""
# 来源链接
source: ""
sourceName: ""
# 一句话摘要，会显示在卡片和详情页顶部
summary: ""
ainewstags: []
featured: false
draft: true
---

## 事件概要

## 为什么重要

## 延伸阅读
