# ClawShell 2.0 — DEEP

> **一云多端分布式神经架构**  
> 类章鱼分布式神经系统：1 个云枢（主脑）+ N 个端脑（副脑）

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-38%2F38-brightgreen)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-orange)](https://github.com/jorinyang/ClawShell-DEEP/releases)

---

## 项目定位

**ClawShell 本质上是一个适用于类 OpenClaw 架构的增强型外骨骼功能插件。**

ClawShell 2.0 在 1.0 基础之上实现云-端协作，采用章鱼式分布式神经系统架构设计。系统以**工程控制论**为指导思想，核心是信息反馈、动态调控和系统整体思维。

- **云枢（Cortex）**——主脑，部署于云端服务器。负责架构规划、深度思考、洞察分析、复盘总结、整理优化、成果广播、终端管理。共识信息及复用能力部署到云端，保持自我成长及迭代高可用性，一端成长、多端共进。
- **端脑（Ganglion）**——副脑，安装于终端设备。自适应不同类 OpenClaw 架构并完成接入与基础配置，模块化接入各种工具/插件能力，协同智能体调度控制其能力完成具体事务。端脑可独立运行，接入云枢后实现信息同步及进化增强。

### 架构全景

```
┌─────────────────────────────────────────────────────────┐
│                  云枢 Cortex (主脑) x1                     │
│  core.py  insight.py  terminal_manager.py  broadcast.py │
│  adapters/ (阿里云OSS . MemOS Cloud . GitHub)           │
└───────────────────┬─────────────────────────────────────┘
                    │  Neural Bus (WebSocket + EventBus)
┌───────────────────┼─────────────────────────────────────┐
│              端脑 Ganglion (副脑) xN                       │
│  perception.py  adaptation.py  plugin_manager.py        │
│  adapters/ (8种 OpenClaw 架构适配)                       │
└─────────────────────────────────────────────────────────┘
```

## 核心能力

### 自感知（Self-Perception）
自动发现设备性能、网络环境、云端凭证、互联网状态。支持 8 种类 OpenClaw 架构变体的自动识别与嗅探。涵盖四维感知：系统资源（CPU/内存/磁盘/进程）、网络环境（主机名/IP/端口/服务）、云端凭证（API Key 有效性/权限边界）、互联网连通性。

### 自适应（Self-Adaptation）
双层自适应机制：环境改造（主动调整环境配置）+ 自我改造（降级非核心功能、切换备用服务）。三层修复策略：自愈层（秒级快速恢复）-> 自动修复层（分钟级自动修复）-> 手动层（人工介入）。支持 5 种运行策略动态切换：默认/应急/节能/激进/保守。

### 自组织（Self-Organization）
任务驱动的动态协作机制。基于工程控制论 PID 反馈控制闭环：设定目标->执行动作->获取反馈->比较偏差->调整控制。具备洞察分析、错误风暴检测、模式识别、知识提炼、周期性汇总等能力。

### 集群协作（Swarm Collaboration）
基于生态位匹配的任务分配算法（能力匹配 40% + 当前负载 30% + 信任评分 30%）。端脑热插拔，信任评分动态评估，端脑离线自动检测。

### 端云同步
端脑在任意行动执行前主动拉取云端信息作为行动参考。云枢离线/无法获取信息时，端脑仍可自主执行。云枢洞察和结果通过 EventBus 机制向终端广播，实现一端成长、多端共进。

## 设计原则

| 原则 | 说明 |
|------|------|
| **异构同效** | 不同架构、不同技术栈模块，在同一机制下发挥同等效能 |
| **无侵入** | 桥接脚本注入，不修改目标系统核心代码 |
| **低耦合** | 模块间通过 EventBus + Pydantic 标准化 Schema 通信，不直接调用 |
| **高鲁棒** | 多层级错误恢复（自愈->自动修复->手动）、守护进程保活、自动降级 |
| **高泛用** | 感知层抽象、适配器模式、标准化接口 |
| **高协同** | EventBus + 生态位匹配 + 集群协作 |
| **可移植** | pip install -e . 跨平台安装（Windows/Linux/macOS） |
| **幂等性** | 重复安装/注册不对已有配置产生副作用 |
| **端云版本解耦** | 云枢和端脑独立配置，独立演进，互不影响 |

## 环境要求

| 项目 | 最低要求 |
|------|----------|
| Python | 3.10 及以上 |
| 操作系统 | Windows / Linux / macOS |
| 网络 | 端脑需能访问云枢（离线模式可不联网） |
| 内存 | 512 MB 以上 |
| 磁盘 | 100 MB 以上 |

## 环境依赖

核心依赖（自动安装）：

| 包名 | 版本 | 用途 |
|------|------|------|
| pydantic | >=2.5.0 | 数据模型与验证 |
| pyyaml | >=6.0 | YAML 配置文件解析 |
| websockets | >=12.0 | WebSocket 端云通信 |
| aiohttp | >=3.9.0 | 异步 HTTP 客户端 |
| requests | >=2.31.0 | HTTP 请求 |
| psutil | >=5.9.0 | 系统资源监控 |
| loguru | >=0.7.0 | 日志系统 |
| httpx | >=0.27.0 | 现代 HTTP 客户端 |
| typer | >=0.12.0 | CLI 命令行框架 |

开发依赖：

| 包名 | 版本 | 用途 |
|------|------|------|
| pytest | >=8.0.0 | 测试框架 |
| pytest-asyncio | >=0.23.0 | 异步测试支持 |
| pytest-cov | >=4.1.0 | 测试覆盖率 |
| ruff | >=0.3.0 | 代码检查与格式化 |
| mypy | >=1.8.0 | 静态类型检查 |

## 支持的 OpenClaw 架构

端脑可自动发现并接入以下类 OpenClaw 架构变体：

| 架构 | 配置目录 | 支持程度 |
|------|----------|----------|
| **OpenClaw** | ~/.openclaw | 完整支持（AGENTS.md + SOUL.md + Skills + Tools） |
| **Hermes** | ~/.hermes | 完整支持（agents.md + soul.md + Skills + Tools） |
| **Work Buddy** | ~/.workbuddy | 支持（WORK_BUDDY.md + Skills） |
| **EasyClaw** | ~/.easyclaw | 支持（EASYCLAW.md + Skills） |
| QClaw | ~/.qclaw | 框架就绪，待扩展配置 |
| CoPaw | ~/.copaw | 框架就绪，待扩展配置 |
| HiClaw | ~/.hiclaw | 框架就绪，待扩展配置 |
| Wukong | ~/.wukong | 框架就绪，待扩展配置 |

## 快速安装

### 方式一：一键安装

```bash
git clone https://github.com/jorinyang/ClawShell-DEEP.git
cd ClawShell-DEEP
python scripts/install.py
```

### 方式二：手动安装

```bash
git clone https://github.com/jorinyang/ClawShell-DEEP.git
cd ClawShell-DEEP
pip install -e .
```

### 生成配置文件

```bash
clawshell init --mode ganglion
clawshell init --mode cortex
```

### 启动服务

```bash
# 启动云枢（主脑，部署于服务器）
clawshell cortex --host 0.0.0.0 --port 9000

# 启动端脑（副脑，连接云枢）
clawshell ganglion --cortex-host <服务器IP> --cortex-port 9000

# 离线模式（不连接云枢，独立运行）
clawshell ganglion --offline
```

### 运行测试

```bash
pytest tests/ -v
# 预期输出：38 passed in ~15s
```

## 环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| ALIBABA_CLOUD_ACCESS_KEY_ID | 条件必需 | 阿里云 AccessKey ID |
| ALIBABA_CLOUD_ACCESS_KEY_SECRET | 条件必需 | 阿里云 AccessKey Secret |
| GITHUB_TOKEN | 条件必需 | GitHub Personal Access Token（需 repo 权限） |
| MEMOS_CLOUD_API_KEY | 条件必需 | MemOS Cloud API Key |
| CLAWSHELL_CORTEX_HOST | 否 | 云枢服务器地址 |
| CLAWSHELL_CORTEX_PORT | 否 | 云枢服务端口（默认 9000） |
| CLAWSHELL_OFFLINE | 否 | 设为 true 启用离线模式 |
| CLAWSHELL_CONFIG_DIR | 否 | 配置文件目录（默认 config/） |

> 条件必需：仅在使用对应功能时需要配置。离线模式或本地开发可不配置。

## 部署基础设施

| 组件 | 平台 | 用途 |
|------|------|------|
| 云枢服务 | 阿里云 ECS | 核心计算与推理服务 |
| 对象存储 | 阿里云 OSS | 配置文件、洞察结果、知识库存储 |
| 代码仓库 | GitHub | 版本控制与端脑更新分发 |
| 记忆云 | MemOS Cloud | 向量化记忆存储与语义检索 |

## 内置插件

| 插件 | 类型 | 说明 |
|------|------|------|
| **N8N** | 服务 | 工作流自动化引擎（默认端点：localhost:5678） |
| **MemOS** | 服务 | 记忆云服务（api.memos.cloud） |
| **ComfyUI** | 工具 | AI 图像生成（默认端点：localhost:8188） |
| **Ollama** | 模型 | 本地大语言模型推理（默认端点：localhost:11434） |
| **OpenClaw Skills** | 技能 | 目标架构的技能目录 |

支持通过 YAML 配置文件扩展自定义插件。

## 版本统计

| 指标 | 数量 |
|------|------|
| 源文件 | 28 |
| 代码行数 | 2,500+ |
| 枚举类型 | 17 |
| Pydantic 数据模型 | 22 |
| 运行策略 | 5 |
| 支持的架构变体 | 8 |
| 内置插件 | 5 |
| 测试用例 | 38 |
| 修复层级 | 3 |
| 感知维度 | 6 |

## 其他说明

### 设计哲学

本项目以钱学森《工程控制论》为理论指导，将"信息反馈、动态调控、系统整体思维"融入软件架构设计中。每一个能力模块都遵循"设定目标->执行动作->获取反馈->比较偏差->调整控制"的反馈控制环。

### 与 OpenClaw 的关系

ClawShell 定位为 OpenClaw 的外骨骼增强层，以**无侵入**方式叠加新能力：不修改 OpenClaw 核心代码、不依赖 OpenClaw 内部实现、通过标准化接口与 OpenClaw 交互、与 OpenClaw 版本解耦，各自独立演进。

### 命名体系

项目命名灵感来源于神经生物学：
- **Cortex**（皮层）——大脑的高级认知中枢，对应云枢的深度思考与规划能力
- **Ganglion**（神经节）——分布于全身的神经节点，对应端脑的分布式感知与执行能力
- **Neural Bus**（神经总线）——神经信号传递通道，对应端云之间的实时通信

### 安全说明

- 云服务凭证通过环境变量注入，不会写入代码或配置文件
- 端脑与云枢之间的 WebSocket 通信建议配合 TLS/SSL 使用
- 信任评分机制确保陌生端脑需经过行为评估才能获得高权限

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

MIT License - Copyright (c) 2026 ClawShell Team

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

---

*ClawShell 2.0 — 遵循工程控制论，构建自进化外骨骼*
