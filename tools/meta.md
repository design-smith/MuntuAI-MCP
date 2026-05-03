# Meta Tools

Tools for inspecting the authenticated key and managing webhook subscriptions.

---

## get_agent_key_info

**Min autonomy:** `observer`

Return metadata about the currently authenticated agent key. Does not expose key material.

**Arguments:** None

**Response:**
```json
{
  "workspaceId": "ws_abc123",
  "name": "Production Monitoring Agent",
  "autonomyLevel": "copilot",
  "keyPrefix": "mnt_aBcDeF",
  "lastUsedAt": "2025-04-01T09:00:00Z",
  "expiresAt": null,
  "createdAt": "2025-01-15T10:00:00Z"
}
```

| Field | Description |
|---|---|
| `workspaceId` | Workspace this key is scoped to |
| `name` | Display name set at key creation |
| `autonomyLevel` | `observer` \| `copilot` \| `autonomous` |
| `keyPrefix` | First few characters of the key ID (for identification) |
| `lastUsedAt` | Last successful authentication timestamp |
| `expiresAt` | Expiry timestamp, or `null` if no expiry |
| `createdAt` | Key creation timestamp |

**Use this to:**
- Confirm which workspace the agent is operating in
- Verify the key's autonomy level before attempting restricted operations
- Check whether the key is approaching expiry

---

## subscribe_events

**Min autonomy:** `copilot`

Register a webhook endpoint to receive workspace events in real time. The endpoint must be HTTPS and respond within 10 seconds with a 2xx status.

**Arguments:**
```json
{
  "url": "https://your-server.example.com/muntu-webhook",
  "secret": "your-webhook-signing-secret-min-16-chars",
  "eventTypes": ["campaign.launched", "campaign.generation_complete", "reply.received"]
}
```

| Field | Required | Description |
|---|---|---|
| `url` | Yes | HTTPS endpoint URL |
| `secret` | Yes | Signing secret (min 16 characters). Used to compute `X-Muntu-Signature` header. |
| `eventTypes` | No | Array of event types to receive. Empty array = all events. |

**Leave `eventTypes` empty to receive all events:**
```json
{
  "url": "https://your-server.example.com/muntu-webhook",
  "secret": "your-webhook-signing-secret-min-16-chars",
  "eventTypes": []
}
```

**Response:**
```json
{
  "success": true,
  "endpointId": "whe_abc123",
  "url": "https://your-server.example.com/muntu-webhook",
  "eventTypes": ["campaign.launched", "campaign.generation_complete", "reply.received"],
  "message": "Webhook endpoint registered"
}
```

**Signature verification:** Every delivery includes `X-Muntu-Signature: sha256=<hex>`. Always verify this before processing the payload. See [webhooks.md](../docs/webhooks.md) for verification code.

**Managing webhooks:** Endpoints can be viewed and deleted from Settings → Webhooks in the UI. Deleting requires `autonomous` level via MCP (not yet exposed as a tool — use the UI).
