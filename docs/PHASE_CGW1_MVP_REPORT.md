# Phase CGW-1 MVP Report

## 1. 项目目标

创建 `chatgpt-visible-bridge`（CGW）—— 一个手动、可审计、一次性的 ChatGPT Web 桥接工作流。

**核心目标：**
- Telegram / 本地 Agent 创建 `/cgpt` 任务 → 写入本地 `inbox/` 任务队列
- 用户需要时手动运行一次性 worker → 处理任务 → 生成报告和结果
- 结果存入 `reports/`（人可读）和 `outbox/`（结构化 JSON）
- Telegram / CLI 可查询结果，只咨询，不执行

**明确声明这不是什么：**
- 不是 OpenAI API wrapper
- 不是无人值守浏览器机器人
- 不是自动执行 ChatGPT 命令的工具
- 不是常驻 daemon

## 2. 当前实现能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 文件队列系统 | ✅ | inbox/active/outbox/failed/reports/logs |
| Task JSON 定义 | ✅ | 含 id, source, type, status, prompt, policy, mode, reply_to |
| Result JSON 定义 | ✅ | 含 id, status, summary, report_path, adapter, stop_reason, suggested_next_action |
| MockAdapter | ✅ | 默认可用，结构化响应，含 smoke test prompt |
| LiveAdapter placeholder | ✅ | 返回 blocked，预留浏览器桥接口 |
| Worker once | ✅ | 处理一个任务后退出 |
| Worker drain | ✅ | 处理所有 pending 后退出 |
| Worker watch | ❌ | 未来可选，非 MVP |
| CLI 命令 | ✅ | create-task, task-status, worker-once, worker-drain, task-result, task-show |
| 报告生成 | ✅ | Markdown 格式，含原始 prompt + 响应 + 建议 |
| 目录自动创建 | ✅ | 首次运行时自动创建 CGW_HOME |
| 环境变量覆盖 | ✅ | CGW_HOME 可自定义 |
| 测试 | ✅ | 24 项测试全部通过 |
| Git 初始化 | ✅ | 已提交 |
| 文档 | ✅ | 8 份文档完整 |
| 示例 | ✅ | task, result, telegram 命令示例 |
| LICENSE | ✅ | MIT |

## 3. 目录结构

```
/home/conanxin/chatgpt-visible-bridge/
├── README.md                           # 项目概述
├── LICENSE                             # MIT License
├── .gitignore                          # 排除凭证和运行时数据
├── .env.example                        # 环境变量示例（无真实值）
├── pyproject.toml                      # Python 包配置和 CLI 入口
│
├── chatgpt_visible_bridge/             # 核心代码
│   ├── __init__.py                     # 版本号 v0.1.0
│   ├── schema.py                       # Task/Result 数据模型和 JSON 序列化
│   ├── workspace.py                    # 文件系统工作目录管理
│   ├── adapter.py                      # Adapter 接口 + MockAdapter + LiveAdapter
│   ├── worker.py                       # One-shot worker 逻辑
│   └── cli.py                          # CLI 命令解析和执行
│
├── docs/                               # 文档
│   ├── ARCHITECTURE.md                 # 通俗架构图和数据流
│   ├── TASK_CONTRACT.md                # Task/Result JSON 合约
│   ├── TELEGRAM_WORKFLOW.md            # Telegram 命令设计
│   ├── WORKER_MODES.md                 # Once/Drain/Watch 模式说明
│   ├── SECURITY_BOUNDARY.md            # 安全边界和威胁模型
│   ├── OPEN_SOURCE_RELEASE.md          # 发布计划和路线图
│   ├── PHASE_LOG.md                    # 开发阶段日志
│   └── RELEASE_NOTES_v0.1.0.md         # 本次发布说明
│
├── examples/                           # 示例
│   ├── task.example.json
│   ├── result.example.json
│   └── telegram-commands.md
│
└── tests/                              # 测试
    ├── test_schema.py                  # 数据模型序列化测试
    ├── test_workspace.py               # 工作目录管理测试
    ├── test_worker.py                  # Worker 生命周期测试
    └── test_cli.py                     # CLI 冒烟测试
```

## 4. CLI 命令说明

| 命令 | 用途 | 示例 |
|------|------|------|
| `cgpt-create-task` | 在 inbox 创建任务 | `cgpt-create-task --prompt "分析架构"` |
| `cgpt-task-status` | 查看队列状态 | `cgpt-task-status` |
| `cgpt-worker-once` | 处理一个任务后退出 | `cgpt-worker-once --mock` |
| `cgpt-worker-drain` | 处理所有任务后退出 | `cgpt-worker-drain --mock` |
| `cgpt-task-result` | 查看结果和报告 | `cgpt-task-result <task_id>` |
| `cgpt-task-show` | 查看原始 prompt 和包装后的 prompt | `cgpt-task-show <task_id>` |

## 5. Task / Result Schema

### Task JSON 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 16 字符 hex 唯一标识 |
| `source` | string | ✅ | 来源：cli, telegram, agent |
| `type` | string | ✅ | 类型：chat, analysis, code_review, planning, generic |
| `status` | string | ✅ | 状态：pending, active, completed, failed, blocked |
| `prompt` | string | ✅ | 用户请求内容 |
| `created_at` | string | ✅ | ISO 8601 时间戳 |
| `mode` | string | ✅ | consult_only 或 execute |
| `policy` | object | ✅ | consult_only, allow_execute, allow_upload_files |
| `reply_to` | string | ❌ | Telegram message_id 等回复引用 |

### Result JSON 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 对应 Task ID |
| `status` | string | ✅ | success, failed, blocked |
| `summary` | string | ✅ | 响应摘要或完整文本 |
| `completed_at` | string | ✅ | ISO 8601 时间戳 |
| `adapter` | string | ✅ | mock 或 live |
| `report_path` | string | ❌ | Markdown 报告路径 |
| `stop_reason` | string | ❌ | 停止原因 |
| `suggested_next_action` | string | ❌ | 建议的下一步 |

## 6. Mock Smoke 测试结果

### 验证命令执行记录

```bash
# 创建 smoke test 任务
$ python3 -m chatgpt_visible_bridge.cli create-task --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"
Task created: 3521a3e4d8bb41cb
  Path: /tmp/cgw-verify/inbox/3521a3e4d8bb41cb.json

# 查看队列状态
$ python3 -m chatgpt_visible_bridge.cli task-status
Inbox (pending):   1
Active:            0
Outbox (completed): 0
Failed:            0

# 运行 worker
$ python3 -m chatgpt_visible_bridge.cli worker-once --mock
Processed task: 3521a3e4d8bb41cb
  Status: success
  Adapter: mock
  Report: /tmp/cgw-verify/reports/3521a3e4d8bb41cb.md

# 查看结果
$ python3 -m chatgpt_visible_bridge.cli task-result 3521a3e4d8bb41cb
Result JSON:
{
  "id": "3521a3e4d8bb41cb",
  "status": "success",
  "summary": "VISIBLE_CHATGPT_BRIDGE_OK",
  ...
}
```

### 报告内容验证

```markdown
# ChatGPT Visible Bridge Report
**Task ID:** 3521a3e4d8bb41cb
**Status:** success
**Adapter:** mock
**Mode:** consult_only
...

---

## Response Summary

VISIBLE_CHATGPT_BRIDGE_OK

**Stop Reason:** smoke_test_prompt
```

✅ **报告中包含 `VISIBLE_CHATGPT_BRIDGE_OK`**

### 测试全部通过

```
pytest tests/ -v
============================== 24 passed in 0.19s
```

## 7. 本地 Git Commit Hash

```
a4e6e45 Initial MVP for ChatGPT visible bridge
```

## 8. 开源准备状态

| 检查项 | 状态 |
|--------|------|
| README 完整 | ✅ |
| LICENSE (MIT) | ✅ |
| .gitignore 排除敏感文件 | ✅ |
| .env.example 无真实凭证 | ✅ |
| 文档齐全 | ✅ |
| 示例文件 | ✅ |
| 测试通过 | ✅ |
| 版本号 | ✅ v0.1.0 |
| Release Notes | ✅ |
| 无 token/cookie/session 硬编码 | ✅ |
| 无 chat_id 硬编码 | ✅ |
| 未自动 git push | ✅ |

**尚未开源发布原因：** 等待用户确认和提供 GitHub 仓库地址。

## 9. 尚未实现内容

| 功能 | 状态 | 计划版本 |
|------|------|----------|
| Telegram bot 前端 | ❌ | v0.2.0 |
| 真实 ChatGPT Web adapter | ❌ | v0.3.0 |
| 执行模式（/agent approve） | ❌ | v0.4.0 |
| 文件上传支持 | ❌ | 未来 |
| 任务重试逻辑 | ❌ | 未来 |
| 任务模板 | ❌ | 未来 |
| Watch 模式 | ❌ | 未来可选 |
| 批量任务创建 | ❌ | 未来 |

## 10. 下一阶段 CGW-2 建议：Telegram 接入

**目标：** 接入 Telegram 命令路由，实现 `/cgpt ask` → 创建任务 → `/cgpt result` → 查询结果。

**两种方案：**

### 方案 A：Telegram Router Mock（轻量）

创建一个 mock Telegram bot 脚本，模拟 CLI 调用：

```python
# scripts/mock-telegram-router.py
# 读取 Telegram 消息，调用 CLI 命令，回复结果
```

- 优点：快速验证端到端流程，不依赖真实 Telegram bot。
- 缺点：不是真实集成，只用于开发测试。

### 方案 B：真实 OpenClaw/Hermes Telegram Gateway

利用已有的 OpenClaw Telegram 通道，编写一个 router：

1. 在 OpenClaw 配置中识别 `/cgpt` 命令前缀。
2. 将 `/cgpt ask <prompt>` 映射为 `cgpt-create-task --prompt "..."`。
3. 将 `/cgpt result <id>` 映射为 `cgpt-task-result <id>`。
4. 将结果通过 Telegram 回复给用户。

- 优点：复用现有基础设施，无需额外 bot token。
- 缺点：需要修改 OpenClaw 配置或添加新的 router 插件。

**推荐：** 先实现方案 A（mock）验证流程，再接入方案 B（真实 gateway）。

## 11. 下一阶段 CGW-3 建议：codex-chatgpt-control Live Adapter

**目标：** 接入真实 ChatGPT Web，通过 `codex-chatgpt-control` 或类似浏览器桥。

**设计要点：**

1. **Adapter 接口**：`LiveAdapter` 继承 `Adapter` 接口，实现 `send(task)` 方法。
2. **浏览器桥通信**：
   - 方式 1：IPC（stdin/stdout）调用 codex-chatgpt-control CLI。
   - 方式 2：HTTP API，codex-chatgpt-control 作为本地服务。
   - 方式 3：文件交换，将 prompt 写入文件，桥读取后写入结果文件。
3. **可见性**：浏览器操作对用户可见（默认 headful，非 headless）。
4. **可中断**：用户可随时 `Ctrl+C` 或关闭浏览器窗口。
5. **可报告**：遇到验证码、登录失效等 blocker 时，返回 `blocked` 状态并记录原因。
6. **超时保护**：单次任务硬超时（如 5 分钟）。

**实现步骤：**
1. 确认 `codex-chatgpt-control` 的接口协议（CLI 参数、输入输出格式）。
2. 实现 `CodexChatGPTAdapter` 类，封装桥接逻辑。
3. 添加 `--adapter codex` CLI 选项。
4. 测试端到端流程（创建任务 → 桥接 → 获取真实响应 → 生成报告）。
5. 更新 SECURITY_BOUNDARY.md，记录 live adapter 的安全约束。

## 12. Go / No-Go 判断

### Acceptance Criteria 检查

| # | 条件 | 状态 |
|---|------|------|
| 1 | `/home/conanxin/chatgpt-visible-bridge` 存在 | ✅ |
| 2 | README 和 docs 完整 | ✅ |
| 3 | CLI 能创建任务、处理 mock 任务、读取结果 | ✅ |
| 4 | reports 中能看到 `VISIBLE_CHATGPT_BRIDGE_OK` | ✅ |
| 5 | 测试通过 | ✅ 24/24 |
| 6 | 已本地 git commit | ✅ a4e6e45 |
| 7 | 无真实 token、cookie、session、chat_id 硬编码 | ✅ |
| 8 | 没有自动 push | ✅ |
| 9 | 没有真实操作 ChatGPT Web | ✅ |
| 10 | 最终报告写入 `docs/PHASE_CGW1_MVP_REPORT.md` | ✅ |

### 判断结果

🟢 **GO**

Phase CGW-1 MVP 已满足所有 Acceptance Criteria，可以进入下一阶段。

### 建议的下一步安全命令

```bash
# 如需测试完整 CLI 流程
cd /home/conanxin/chatgpt-visible-bridge
export CGW_HOME=/tmp/cgw-test
python3 -m chatgpt_visible_bridge.cli create-task --prompt "请只回复 VISIBLE_CHATGPT_BRIDGE_OK"
python3 -m chatgpt_visible_bridge.cli worker-once --mock
python3 -m chatgpt_visible_bridge.cli task-result <task_id>

# 如需运行测试
python3 -m pytest tests/ -v

# 如需查看当前状态
python3 -m chatgpt_visible_bridge.cli task-status

# 如需查看提交信息
cd /home/conanxin/chatgpt-visible-bridge && git log --oneline
```

---

*报告生成时间：2026-06-08*
*Git Commit: a4e6e45*
*版本: v0.1.0*
