---
title: "OpenClaw源码剖析 #15 · 部署与运维：Docker 与容器化"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 16
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、部署系统定位

OpenClaw 支持多种部署方式，其中 **Docker 容器化部署**是生产环境的推荐方案。

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Deployment                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                   Multi-Stage Build                    │ │
│  │  ext-deps → build → runtime-assets → base → runtime  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │  Docker Compose │  │   Gateway       │  │   Sandbox   │ │
│  │  Gateway + CLI  │  │  容器运行       │  │  隔离代理    │ │
│  └────────────────┘  └────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、Dockerfile 结构

### 2.1 多阶段构建

> `Dockerfile`

| Stage | 说明 |
|:---|:---|
| `ext-deps` | 从选定的扩展中提取 package.json |
| `build` | 安装 Bun/pnpm 依赖，构建 dist、UI、qa:lab |
| `runtime-assets` | 裁剪 dev 依赖，移除 .d.ts/.map 文件 |
| `base-runtime` | 基于 node:24-bookworm-slim + apt 工具 |
| `runtime` | 最终镜像：非 root node 用户，healthcheck，gateway 启动 |

### 2.2 构建参数

```dockerfile
# 预安装插件依赖
ARG OPENCLAW_EXTENSIONS

# 额外 apt 包
ARG OPENCLAW_DOCKER_APT_PACKAGES

# 包含 Chromium + Xvfb（~300MB）
ARG OPENCLAW_INSTALL_BROWSER

# 包含 Docker CLI（用于 sandbox）
ARG OPENCLAW_INSTALL_DOCKER_CLI
```

### 2.3 基础镜像

```dockerfile
FROM node:24-bookworm-slim@sha256:... AS base
```

使用 SHA256 摘要固定版本保证可重现性。

---

## 三、Docker Compose 配置

> `docker-compose.yml`

### 3.1 服务定义

```yaml
services:
  openclaw-gateway:
    image: ${OPENCLAW_IMAGE:-openclaw:local}
    environment:
      HOME: /home/node
      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN:-}
      OPENCLAW_DISABLE_BONJOUR: ${OPENCLAW_DISABLE_BONJOUR:-}
      OTEL_EXPORTER_OTLP_ENDPOINT: ${OTEL_EXPORTER_OTLP_ENDPOINT:-}
      OPENCLAW_PLUGIN_STAGE_DIR: /var/lib/openclaw/plugin-runtime-deps
    volumes:
      - ${OPENCLAW_CONFIG_DIR:-${HOME:-/tmp}/.openclaw}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR:-${HOME:-/tmp}/.openclaw/workspace}:/home/node/.openclaw/workspace
      - openclaw-plugin-runtime-deps:/var/lib/openclaw/plugin-runtime-deps
    ports:
      - "${OPENCLAW_GATEWAY_PORT:-18789}:18789"
      - "${OPENCLAW_BRIDGE_PORT:-18790}:18790"
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:18789/healthz')..."]
```

### 3.2 CLI 服务

```yaml
  openclaw-cli:
    image: ${OPENCLAW_IMAGE:-openclaw:local}
    network_mode: service:openclaw-gateway
    depends_on:
      openclaw-gateway:
        condition: service_healthy
    environment:
      HOME: /home/node
```

---

## 四、环境变量

### 4.1 核心变量

| 变量 | 说明 | 默认值 |
|:---|:---|:---|
| `OPENCLAW_GATEWAY_TOKEN` | 认证 Token | 自动生成 |
| `OPENCLAW_GATEWAY_BIND` | 绑定模式 | `lan` |
| `OPENCLAW_GATEWAY_PORT` | Gateway 端口 | `18789` |
| `OPENCLAW_BRIDGE_PORT` | Bridge 端口 | `18790` |
| `OPENCLAW_DISABLE_BONJOUR` | 禁用 mDNS | `1`（自动） |
| `OPENCLAW_CONFIG_DIR` | 配置路径 | `~/.openclaw` |
| `OPENCLAW_WORKSPACE_DIR` | 工作区路径 | `~/.openclaw/workspace` |
| `OPENCLAW_IMAGE` | 使用的镜像 | `openclaw:local` |
| `OPENCLAW_EXTENSIONS` | 预装插件 | （无） |
| `OPENCLAW_SANDBOX` | 启用沙箱 | （禁用） |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP 收集器 | （无） |

### 4.2 API Keys

```bash
# 模型 Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# 会话密钥
CLAUDE_AI_SESSION_KEY=...
CLAUDE_WEB_SESSION_KEY=...

# Channel Tokens
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...
```

---

## 五、快速部署

### 5.1 自动设置

```bash
# 使用本地构建镜像
./scripts/docker/setup.sh

# 使用预构建镜像
export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
./scripts/docker/setup.sh
```

### 5.2 手动流程

```bash
# 构建镜像
docker build -t openclaw:local -f Dockerfile .

# 引导配置
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js onboard --mode local --no-install-daemon

# 启动 Gateway
docker compose up -d openclaw-gateway
```

---

## 六、Sandbox 隔离

### 6.1 启用沙箱

```bash
export OPENCLAW_SANDBOX=1
./scripts/docker/setup.sh
```

### 6.2 沙箱要求

- Docker socket 挂载
- 镜像中包含 Docker CLI
- 每个 Agent/Session 创建独立容器

### 6.3 工作区挂载

```yaml
volumes:
  - /path/to/workspace:/workspace
```

---

## 七、CI/CD Docker 工作流

### 7.1 GitHub Actions

| Workflow | 触发条件 | 说明 |
|:---|:---|:---|
| `docker-release.yml` | Tag push / 手动 | 多架构镜像发布到 GHCR |
| `live-media-runner-image.yml` | 路径变更 | Media runner 镜像构建 |
| `ci.yml` | Push/PR | 主 CI（含 Docker E2E 测试） |

### 7.2 docker-release.yml 结构

```
build-amd64 (ubuntu-24.04) → digest
build-arm64 (ubuntu-24.04-arm) → digest
                    ↓
         create-manifest (multi-arch)
                    ↓
         verify-attestations
```

### 7.3 镜像标签

| 标签 | 说明 |
|:---|:---|
| `main`、`latest`、`v{version}` | 多架构 Manifest |
| `main-amd64`、`main-arm64` | 单架构 |
| `version-amd64`、`version-arm64` | 版本单架构 |
| `main-slim`、`slim` | 精简变体 |

---

## 八、安全配置

### 8.1 非 root 运行

```dockerfile
# 创建非 root 用户
RUN useradd -m -u 1000 node
USER node
```

### 8.2 CLI 容器安全

```yaml
openclaw-cli:
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - NET_RAW
    - NET_ADMIN
```

### 8.3 OCI 注解

镜像包含 provenance 证明用于安全审计。

---

## 九、持久化

| 路径 | 机制 |
|:---|:---|
| `/home/node/.openclaw/` | Host 绑定挂载 |
| `/home/node/.openclaw/workspace/` | Host 绑定挂载 |
| `/var/lib/openclaw/plugin-runtime-deps/` | Docker 命名卷 |
| `/usr/local/bin/` | 烧入镜像 |

---

## 十、网络配置

### 10.1 主机网络

```yaml
# Host 网络模式用于 Ollama/LM Studio
extra_hosts:
  - "host.docker.internal:host-gateway"
```

### 10.2 Bonjour/mDNS

Docker 内部自动禁用（多播不可靠）。

---

## 十一、其他 Dockerfile 变体

| 文件 | 说明 |
|:---|:---|
| `Dockerfile.sandbox` | 最小化 Debian 沙箱容器 |
| `Dockerfile.sandbox-common` | 共享沙箱层（pnpm/bun/Homebrew） |
| `Dockerfile.sandbox-browser` | 浏览器自动化沙箱（Chromium、Xvfb） |
| `.github/images/live-media-runner/Dockerfile` | Ubuntu 24.04 media runner |
| `scripts/e2e/Dockerfile` | E2E 测试运行器镜像 |

---

## 下一步

篇目 15 完成，**全部 15 篇已完成**！

---

| # | 文章 | 状态 | 说明 |
|:---|:---|:---|:---|
| 01 | [整体架构概览](./01-architecture-overview.md) | ✅ 完成 | 目录结构与模块划分 |
| 02 | [Gateway 控制平面](./02-gateway-arch.md) | ✅ 完成 | API 路由与协议 |
| 03 | [Plugin SDK](./03-plugin-sdk.md) | ✅ 完成 | 扩展机制与公开 API |
| 04 | [Agent Runtime](./04-agent-runtime.md) | ✅ 完成 | 任务编排与执行 |
| 05 | [Provider 系统](./05-provider-system.md) | ✅ 完成 | 多模型统一接口 |
| 06 | [Channel 系统](./06-channel-system.md) | ✅ 完成 | 多渠道消息接入 |
| 07 | [会话与状态管理](./07-session-state.md) | ✅ 完成 | 会话生命周期 |
| 08 | [记忆系统](./08-memory-system.md) | ✅ 完成 | Memory Architecture |
| 09 | [Extension 开发：Provider 篇](./09-extension-provider.md) | ✅ 完成 | 开发新模型 Provider |
| 10 | [Extension 开发：Channel 篇](./10-extension-channel.md) | ✅ 完成 | 开发新消息渠道 |
| 11 | [Extension 开发：Skill 篇](./11-extension-skill.md) | ✅ 完成 | 开发新 Skill |
| 12 | [测试策略](./12-testing-strategy.md) | ✅ 完成 | Vitest + E2E |
| 13 | [配置系统](./13-config-system.md) | ✅ 完成 | Schema 与验证 |
| 14 | [安全机制](./14-security-auth.md) | ✅ 完成 | Auth 与权限 |
| 15 | [部署与运维](./15-deployment-docker.md) | ✅ 完成 | Docker 与容器化 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*