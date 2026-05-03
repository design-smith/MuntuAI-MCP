# Authentication

All requests to the MuntuAI MCP server require a bearer token issued from the MuntuAI dashboard.

---

## Token Format

```
mnt_<keyId>.<secret>
```

- `keyId` — public identifier, alphanumeric + `-_`
- `secret` — private value, never stored in plaintext on Muntu's side

**Example:**
```
mnt_aBcDeFgHiJ.xYz123secretvalue
```

---

## How to Pass It

Every request must include an `Authorization` header:

```
Authorization: Bearer mnt_<keyId>.<secret>
```

For MCP clients (Claude Desktop, Cursor):

```json
{
  "headers": {
    "Authorization": "Bearer ${env:MUNTU_AGENT_KEY}"
  }
}
```

When the client supports environment-variable interpolation, prefer that over embedding the live key directly. Cursor supports this pattern:

```json
{
  "headers": {
    "Authorization": "Bearer ${env:MUNTU_AGENT_KEY}"
  }
}
```

For direct HTTP:

```bash
curl -X POST https://api.muntuai.com/api/mcp \
  -H "Authorization: Bearer mnt_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

---

## Verification Process

The server performs dual verification on every request:

1. **Fast check** — HMAC-SHA256 of the secret against the stored verifier. Runs in microseconds.
2. **Slow check** — bcrypt comparison for belt-and-suspenders security.
3. **Expiry** — If the key has an `expiresAt` date and it has passed, the request is rejected.
4. **Active flag** — If the key has been revoked (`isActive = false`), the request is rejected.
5. **Audit** — Every authenticated request is logged to the workspace's system event log.

---

## Rate Limits

Rate limits are enforced per key in a rolling 60-second window.

| Autonomy Level | Requests per minute |
|---|---|
| `observer` | 60 |
| `copilot` | 120 |
| `autonomous` | 120 |

When the limit is exceeded, the server returns an MCP error with a `retryAfterSeconds` field:

```json
{
  "error": {
    "code": -32603,
    "message": "Rate limit exceeded. Retry after 12 seconds.",
    "data": { "retryAfterSeconds": 12 }
  }
}
```

---

## Session Header

Muntu also accepts an optional `mcp-session-id` header:

```
mcp-session-id: <stable-session-id>
```

Use one stable value for the lifetime of a single agent session. This helps the server apply session-scoped safety controls consistently. If omitted, the server falls back to a key-derived session identifier.

---

## Key Lifecycle

- **Creation** — Via MuntuAI dashboard (Settings → Agent Keys). The raw key is shown once.
- **Expiry** — Optional. Set during creation. UTC timestamp.
- **Revocation** — Via dashboard. Takes effect immediately on the next request.
- **Last used** — Updated on every successful authentication. Visible in the dashboard.

---

## Security Notes

- Keys are workspace-scoped. A key for workspace A cannot access workspace B.
- Every tool invocation and blocked attempt is logged to the system event log regardless of outcome.
- If you lose a key before copying it, revoke it and create a new one. There is no recovery.
- Keys should be stored in environment variables, not hardcoded in source code.
- If a client requires local config-file headers, treat that config file as a secret and never commit it.
