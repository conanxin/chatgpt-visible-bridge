# Architecture

## 通俗架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         用户 / 本地 Agent                                │
│  (Telegram Bot / Hermes / OpenClaw / 手敲 CLI)                          │
└──────────────────────────┬────────────────────────────────────────────────┘
                           │
                           │  ① 创建任务
                           │     /cgpt "请帮我分析这个架构"
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         本地 Task Queue                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐             │
│  │  inbox/  │──▶│ active/  │──▶│ outbox/  │   │ failed/  │             │
│  │(pending) │   │(processing)│ │(completed)│   │(blocked) │             │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘             │
│       │              │              │                                    │
│       └──────────────┴──────────────┘                                  │
│                         纯 JSON 文件，无数据库                           │
└──────────────────────────┬─────────────────────────────────────────────┘
                           │
                           │  ② 用户手动运行 Worker
                           │     cgpt-worker-once --mock
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         One-Shot Worker                                  │
│  - 从 inbox 取最早任务 → 移到 active                                     │
│  - 发送给 Adapter（默认 Mock）                                           │
│  - 拿到结果 → 写 report.md + result.json                               │
│  - 把任务移到 outbox 或 failed                                          │
│  - 处理完一个（或 drain 全部）后**立即退出**，不常驻                    │
└──────────────────────────┬─────────────────────────────────────────────┘
                           │
                           │  ③ Adapter 处理
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Adapter 层                                       │
│  ┌────────────────────────┐  ┌─────────────────────────────────────────┐   │
│  │   MockAdapter         │  │   LiveAdapter (placeholder)           │   │
│  │   (默认，MVP 可用)    │  │   (blocked，未来接 codex-chatgpt-control)│   │
│  │   - 返回结构化建议    │  │   - 必须可见、可中断、可报告 blocker    │   │
│  │   - 不访问网络        │  │   - 本阶段不操作真实 ChatGPT Web        │   │
│  └────────────────────────┘  └─────────────────────────────────────────┘   │
└──────────────────────────┬─────────────────────────────────────────────┘
                           │
                           │  ④ 结果写入本地
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         结果产出                                         │
│  ┌──────────────┐   ┌──────────────┐                                   │
│  │  reports/    │   │  outbox/     │                                   │
│  │  .md 报告    │   │  .json 结果  │                                   │
│  │  (人可读)    │   │  (结构化)    │                                   │
│  └──────────────┘   └──────────────┘                                   │
│       │                    │                                           │
│       └────────────┬───────┘                                           │
│                    │  ⑤ 查询结果                                        │
│                    ▼                                                   │
│  Telegram / CLI: cgpt-task-result <id> 或 /cgpt result <id>            │
└─────────────────────────────────────────────────────────────────────────┘
```

## 完整数据流

```
Telegram 或本地 agent 创建任务
         ↓
    写入 inbox/<task_id>.json
         ↓
用户手动运行 cgpt-worker-once --mock
         ↓
    Worker 读取 inbox → 移到 active
         ↓
    Adapter 处理（Mock 返回结构化建议）
         ↓
    Worker 写入：
        - reports/<task_id>.md    （人可读报告）
        - outbox/<task_id>.json   （结构化结果）
         ↓
    任务从 active 移到 outbox（成功）或 failed（失败）
         ↓
用户通过 CLI 或 Telegram 查询结果
         ↓
    /cgpt result <task_id> → 读取 reports/ + outbox/
         ↓
    结果展示给用户，只咨询，不执行
```

## 核心设计原则

| 原则 | 说明 |
|------|------|
| **Explicit over implicit** | 用户必须手动运行 worker，不会自动触发 |
| **Consult-only by default** | 结果永远是建议，不自动执行 ChatGPT 生成的命令 |
| **Auditability** | 每一步都留下文件（task → report → result → log）|
| **Minimal dependencies** | Python 标准库 + argparse，无重型框架 |
| **Visible & Interruptible** | Live adapter 未来必须可见、可中断、可报告 blocker |
| **Future-proof** | Live adapter 是插件接口，可随时替换 |

## 目录结构（Runtime）

```
~/.openclaw/workspace/chatgpt-visible-bridge/
├── inbox/      # Pending tasks（待处理）
├── active/     # 正在处理中的任务（最多 1 个）
├── outbox/     # 已完成的结果（result.json + task 记录）
├── failed/     # 失败或阻塞的任务记录
├── reports/    # 人可读的 Markdown 报告
└── logs/       # Worker 执行日志
```

可通过 `CGW_HOME` 环境变量覆盖默认路径。

## 组件说明

### 1. Task Queue（基于文件）

- 无数据库，纯 JSON + Markdown。
- `inbox/` 按文件创建时间排序，FIFO 处理。
- `active/` 只放一个任务，防止并发冲突。
- 任务移动是原子文件操作（`rename`）。

### 2. Worker（三种模式）

| 模式 | 命令 | 行为 | 推荐度 |
|------|------|------|--------|
| **once** | `cgpt-worker-once --mock` | 处理一个任务后退出 | ⭐ 默认推荐 |
| **drain** | `cgpt-worker-drain --mock` | 处理所有 pending 任务后退出 | 可选 |
| **watch** | （未来） | 常驻监听 inbox（非 MVP 默认） | 暂不实现 |

### 3. Adapter 层（CGW-3A）

- **MockAdapter**：默认，返回结构化 mock 回复，不访问网络。
- **CodexChatGPTControlAdapter**：CGW-3A 骨架。返回 `blocked`（`browser_bridge_unavailable`）。CGW-3B 将在兼容浏览器桥 host 中实现真实 live smoke。

Adapter 通过 `--adapter` 参数选择：
```bash
cgpt-worker-once --adapter mock
cgpt-worker-once --adapter codex-chatgpt-control
```

### 4. CLI / Telegram 接口

- CLI 是核心入口，Telegram 是可选查询层。
- Telegram bot 只读写本地文件，不执行命令。
