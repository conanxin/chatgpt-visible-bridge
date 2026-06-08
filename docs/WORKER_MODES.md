# Worker Modes

## 三种 Worker 模式

| 模式 | 命令 | 行为 | 退出时机 | 推荐度 |
|------|------|------|----------|--------|
| **once** | `cgpt-worker-once --mock` | 处理 inbox 中最早的一个任务 | 处理完 1 个后立即退出 | ⭐ **默认推荐** |
| **drain** | `cgpt-worker-drain --mock` | 处理 inbox 中所有 pending 任务 | 全部处理完后退出 | 可选 |
| **watch** | `cgpt-worker-watch`（未来） | 常驻监听 inbox/，自动处理新任务 | 永不退出，需手动停止 | 非 MVP 默认 |

## Once 模式（默认推荐）

```bash
cgpt-worker-once --mock
```

- 从 inbox 读取最早的一个任务，移到 active。
- 发送给 Adapter，拿到结果。
- 写 report.md + result.json。
- 把任务从 active 移到 outbox（成功）或 failed（失败）。
- **立即退出**。不常驻，不轮询。

**为什么默认推荐？**

1. **可控**：用户决定何时运行 worker，不会意外处理不想处理的任务。
2. **可见**：每次运行都能看到 stdout 输出和日志。
3. **安全**：不会自动执行任何命令，处理完就停。
4. **可审计**：每次运行产生一组新的文件（report + result），方便回溯。

## Drain 模式（批量处理）

```bash
cgpt-worker-drain --mock
```

- 循环处理 inbox 中所有 pending 任务，直到为空。
- 每处理一个任务，写 report + result，然后移出 active。
- 全部处理完后退出。

**适用场景**：
- 用户积累了多个任务，想一次性处理完。
- 夜间批量处理（用户主动触发，不是自动）。

**注意**：Drain 模式不检查任务之间的依赖关系，按 FIFO 顺序处理。

## Watch 模式（未来可选，非 MVP 默认）

```bash
# 未来可能实现，但 MVP 不包含
cgpt-worker-watch --mock
```

- 常驻监听 inbox/ 目录，有新任务时自动处理。
- 需要手动启动和停止（如 `Ctrl+C`）。
- **MVP 阶段不实现**，因为：
  1. 与 "手动 one-shot" 的核心设计原则冲突。
  2. 常驻进程增加了复杂性和安全风险。
  3. 用户可以通过 cron 或 systemd timer 实现类似效果。

**如需类似 watch 的效果，建议**：

```bash
# 用 cron 每 30 分钟运行一次 drain
*/30 * * * * cd /home/conanxin/chatgpt-visible-bridge && cgpt-worker-drain --mock
```

## Mock 模式（默认）

```bash
cgpt-worker-once --mock
cgpt-worker-drain --mock
```

- **无网络调用**：纯本地计算。
- **安全测试**：可在不触碰 ChatGPT Web 的情况下验证完整 pipeline。
- **结构化响应**：返回分析、建议、风险、下一步建议。

### Mock 响应格式

```markdown
## 任务理解

已收到任务（ID: ...）。以下是对请求的分析和建议。

## 建议

1. 仔细审查原始需求。
2. 将大任务拆分为可验证的小步骤。
3. 使用本地工具或脚本执行，而非自动执行。

## 风险点

- 自动执行未经审查的 AI 建议可能导致意外副作用。
- 文件操作前应确认路径和权限。
- 敏感信息不应离开本地环境。

## 下一步建议

- 在 `reports/` 中查看完整分析。
- 如需执行，请手动审核并运行 `/agent approve`。

---

**注意：这是 mock adapter，未调用真实 ChatGPT Web。**
```

### Smoke Test Prompt

如果 prompt 是：
```
请只回复 VISIBLE_CHATGPT_BRIDGE_OK
```

MockAdapter 必须返回包含 `VISIBLE_CHATGPT_BRIDGE_OK` 的 summary，用于验证 pipeline 是否打通。

## Live 模式（占位符，不实现）

```bash
cgpt-worker-once --adapter live
```

- MVP 中返回 `blocked` 状态。
- 需要外部浏览器桥（如 codex-chatgpt-control）才能工作。

## 为什么 Watch 不作为默认？

| 风险 | 说明 |
|------|------|
| 不可控 | 任务自动处理，用户可能不知道正在发生什么 |
| 不可见 | 后台进程，stdout 可能被丢弃 |
| 不可审计 | 连续运行可能导致日志和文件堆积 |
| 不可中断 | 如果任务卡住，用户需要手动 kill 进程 |
| 违背设计原则 | 本项目的核心是 "手动、可见、可审计" |

因此，**once 是默认，drain 是选项，watch 是未来可选**。
