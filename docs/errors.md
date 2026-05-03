# Errors

All errors follow the JSON-RPC 2.0 error format embedded in a `result` envelope from MCP.

---

## Error Shape

```json
{
  "error": {
    "code": -32603,
    "message": "Insufficient autonomy level",
    "data": { ... }
  }
}
```

---

## Common Error Codes

| Code | Meaning |
|---|---|
| `-32700` | Parse error — malformed JSON |
| `-32600` | Invalid request — missing required JSON-RPC fields |
| `-32601` | Method not found |
| `-32602` | Invalid params — schema validation failed |
| `-32603` | Internal error — auth failure, policy block, or tool error |

All application-level errors (auth, rate limit, autonomy, policy) use `-32603` with a descriptive `message`.

---

## Authentication Errors

### Invalid token
```json
{
  "error": {
    "code": -32603,
    "message": "Unauthorized"
  }
}
```
Cause: Missing or malformed `Authorization: Bearer mnt_...` header, or the secret doesn't verify.

### Revoked key
```json
{
  "error": {
    "code": -32603,
    "message": "Unauthorized"
  }
}
```
Cause: Key has been revoked (`isActive = false`) in the dashboard.

### Expired key
```json
{
  "error": {
    "code": -32603,
    "message": "Unauthorized"
  }
}
```
Cause: Key has an `expiresAt` that has passed. Create a new key.

---

## Rate Limit Errors

```json
{
  "error": {
    "code": -32603,
    "message": "Rate limit exceeded. Retry after 12 seconds.",
    "data": { "retryAfterSeconds": 12 }
  }
}
```

Rate limits are per-key in a rolling 60-second window:

| Autonomy Level | Requests/minute |
|---|---|
| `observer` | 60 |
| `copilot` | 120 |
| `autonomous` | 120 |

Always check `data.retryAfterSeconds` and back off before retrying.

---

## Autonomy Errors

```json
{
  "error": {
    "code": -32603,
    "message": "Insufficient autonomy level"
  }
}
```

Cause: The tool requires a higher autonomy level than the key has. Check the [autonomy matrix](autonomy-levels.md#permission-matrix) and use a key with sufficient level.

This attempt is also logged in the workspace event stream as `agent.action.blocked` with `reason: "autonomy_level_insufficient"`.

---

## Policy Errors

```json
{
  "error": {
    "code": -32603,
    "message": "Workspace policy ceiling restricts this action"
  }
}
```

Cause: The workspace `autonomyCeiling` setting limits the effective autonomy level even if the key has a higher level. The workspace owner must raise the ceiling in Settings → Policy.

---

## Tool Validation Errors

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "issues": [
        { "path": ["workflowId"], "message": "Required" }
      ]
    }
  }
}
```

Cause: Arguments didn't pass the tool's Zod schema. Check `data.issues` for specific field errors.

---

## Campaign Policy Block

When `create_campaign` or `launch_campaign` is blocked by workspace safety policy, the tool returns a **success response** (not an error) with `success: false`:

```json
{
  "success": false,
  "blocked": true,
  "reasons": ["lead_count_too_high", "domain_not_verified"],
  "workflowId": null
}
```

This is not an MCP protocol error — it's a business-level rejection. Check `reasons` and resolve each blocker before retrying.

Common `reasons`:
- `lead_count_too_high` — exceeds `riskThresholdLeadCount` workspace policy setting
- `domain_not_verified` — assigned sending domain is not verified
- `no_ready_senders` — no sender accounts are in `active` status
- `approval_required` — workspace policy requires human approval before launch

---

## Resource Not Found

```json
{
  "error": {
    "code": -32603,
    "message": "Resource not found"
  }
}
```

Cause: The `workflowId`, `managedDomainId`, `senderAccountId`, or other resource ID doesn't exist in the workspace, or belongs to a different workspace.

---

## Error Handling Checklist

1. **Check `error.code`** — if `-32602`, fix your arguments
2. **Check `error.message`** — human-readable description of the problem
3. **Check `data.retryAfterSeconds`** — for rate limit errors, wait this long before retrying
4. **Check `success: false` in tool results** — business rejections come as successful responses
5. **Never retry immediately on `-32603`** — diagnose first; most `-32603` errors require a fix, not a retry
