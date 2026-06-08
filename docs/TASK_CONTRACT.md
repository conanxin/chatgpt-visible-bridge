# Task Contract

## Task JSON Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique task identifier (16-char hex) |
| `source` | string | Origin of the task (e.g., `cli`, `telegram`, `agent`) |
| `type` | string | Task type: `chat`, `analysis`, `code_review`, `planning`, `generic` |
| `status` | string | Current status: `pending`, `active`, `completed`, `failed`, `blocked` |
| `prompt` | string | The user's request to ChatGPT |
| `created_at` | string (ISO 8601) | Creation timestamp |
| `mode` | string | `consult_only` or `execute` |
| `policy` | object | Execution policy (see below) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `reply_to` | string | Reference ID for reply threading (e.g., Telegram message_id) |

### Policy Object

```json
{
  "consult_only": true,
  "allow_execute": false,
  "allow_upload_files": false
}
```

- `consult_only`: If true, ChatGPT should only provide analysis and suggestions.
- `allow_execute`: If true, the user may choose to execute suggestions (requires explicit approval).
- `allow_upload_files`: If true, file upload may be attempted (not in MVP).

## Status Lifecycle

```
pending → active → completed
  ↓         ↓
failed   blocked
```

- **pending**: Task is in `inbox/`, waiting for worker.
- **active**: Task is in `active/`, being processed by worker.
- **completed**: Task succeeded, result in `outbox/` + report in `reports/`.
- **failed**: Worker or adapter error, record in `failed/`.
- **blocked**: Policy or adapter blocked execution (e.g., live adapter unavailable).

## Example Task JSON

See [examples/task.example.json](../examples/task.example.json).

## Result JSON Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Task ID |
| `status` | string | `success`, `failed`, or `blocked` |
| `summary` | string | Response summary or full text |
| `completed_at` | string (ISO 8601) | Completion timestamp |
| `adapter` | string | Adapter name used (`mock` or `live`) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `report_path` | string | Path to the Markdown report |
| `stop_reason` | string | Why the worker stopped (e.g., `mock_consult_only`, `worker_exception`) |
| `suggested_next_action` | string | Recommended next step for the user |

## Example Result JSON

See [examples/result.example.json](../examples/result.example.json).
