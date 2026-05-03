# Webhooks

Webhooks let you receive MuntuAI events in real time via HTTP POST to an endpoint you control. Instead of polling the events resource, your server receives a push notification whenever something happens in the workspace.

---

## Registering a Webhook

### Via MCP (agents)

Requires `copilot` autonomy level. Call the `subscribe_events` tool (exposed inside the MCP server as a built-in):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "subscribe_events",
    "arguments": {
      "url": "https://your-server.example.com/muntu-webhook",
      "secret": "your-webhook-signing-secret-min-16-chars",
      "eventTypes": ["campaign.launched", "campaign.generation_complete", "reply.received"]
    }
  }
}
```

Leave `eventTypes` empty to receive all event types:
```json
{
  "url": "https://your-server.example.com/muntu-webhook",
  "secret": "your-webhook-signing-secret-min-16-chars",
  "eventTypes": []
}
```

### Via UI

Go to **Settings → Agent Keys → Webhooks** and click **Register Endpoint**.

---

## Webhook Payload

Every delivery is a `POST` request with:

```
Content-Type: application/json
X-Muntu-Signature: sha256=<hex>
```

**Payload shape:**
```json
{
  "apiVersion": "v1",
  "eventType": "campaign.launched",
  "workspaceId": "ws_abc123",
  "resourceType": "campaign",
  "resourceId": "wf_xyz",
  "payload": {
    "workflowId": "wf_xyz",
    "workflowName": "Q2 Security Outreach",
    "leadCount": 150
  },
  "createdAt": "2025-04-01T09:15:00Z"
}
```

---

## Verifying Signatures

Every delivery includes an `X-Muntu-Signature` header with an HMAC-SHA256 signature of the raw request body.

**Format:** `sha256=<hex>`

**Verification — Python:**
```python
import hmac
import hashlib

def verify_muntu_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature_header, expected)

# In your handler:
raw_body = request.get_data()  # raw bytes, before parsing
signature = request.headers.get("X-Muntu-Signature", "")
secret = "your-webhook-signing-secret"

if not verify_muntu_signature(raw_body, signature, secret):
    return Response("Forbidden", status=403)
```

**Verification — Node.js:**
```javascript
const crypto = require("crypto");

function verifyMuntuSignature(rawBody, signatureHeader, secret) {
  const expected = "sha256=" + crypto
    .createHmac("sha256", secret)
    .update(rawBody)
    .digest("hex");
  return crypto.timingSafeEqual(
    Buffer.from(signatureHeader),
    Buffer.from(expected)
  );
}

// In your Express handler:
app.post("/muntu-webhook", express.raw({ type: "application/json" }), (req, res) => {
  const sig = req.headers["x-muntu-signature"];
  if (!verifyMuntuSignature(req.body, sig, process.env.WEBHOOK_SECRET)) {
    return res.status(403).send("Forbidden");
  }
  const event = JSON.parse(req.body);
  // handle event...
  res.status(200).send("OK");
});
```

**Critical:** Always use `timingSafeEqual` (or `hmac.compare_digest`) — never use `===` for signature comparison. Always verify against the **raw request body bytes**, not a re-serialized JSON string.

---

## Retry Behavior

If your endpoint returns a non-2xx status or times out (10 second timeout), Muntu retries with exponential backoff:

| Attempt | Delay before retry |
|---|---|
| 1 | — |
| 2 | 1 second |
| 3 | 2 seconds |
| 4 | 4 seconds |
| 5 | 8 seconds |
| 6 (final) | 16 seconds |

After 6 failed attempts, the delivery is marked `failed`. You can manually retry a failed delivery from the UI (Settings → Webhooks → Delivery History → Retry) or via the `retryDelivery` API.

---

## Delivery Status

Each delivery attempt is tracked with:
- `status` — `pending`, `delivered`, `failed`
- `attemptCount` — number of attempts made
- `responseStatus` — HTTP status code from your endpoint
- `responseBody` — first 2000 chars of the response body

View delivery history in the UI under **Settings → Webhooks → Delivery History**.

---

## Requirements

- **HTTPS required** — HTTP URLs are rejected.
- **Secret minimum length** — 16 characters.
- **Response** — Your endpoint must return a 2xx status within 10 seconds. The response body is logged but not used.
- **Idempotency** — Deliveries may be retried. Your handler should be idempotent (safe to process the same event twice).

---

## Managing Webhooks

Clarification: `subscribe_events` is part of the MCP surface. Delivery history and retry controls are currently authenticated Muntu application features, not MCP built-in tools.

| Action | Method |
|---|---|
| Register endpoint | MCP tool `subscribe_events` or UI |
| List endpoints | UI (Settings → Webhooks) |
| Delete endpoint | UI or autonomous-level agent |
| View delivery history | UI or `listDeliveries` API |
| Retry failed delivery | UI (Delivery History → Retry) |
