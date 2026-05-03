# Sender Tools

Tools for managing email sender accounts (mailboxes used to send campaigns).

---

## list_ready_senders

**Min autonomy:** `observer`

List sender accounts that are currently ready to send campaigns (status `active`, health checks passing).

**Arguments:** None

**Response:**
```json
{
  "senders": [
    {
      "id": "sa_xyz",
      "email": "outreach@example.com",
      "displayName": "Outreach Team",
      "domainName": "example.com",
      "status": "active",
      "connectionStatus": "connected"
    }
  ],
  "total": 3
}
```

---

## get_sender_health

**Min autonomy:** `observer`

Return the latest health snapshot and readiness gates for a specific sender.

**Arguments:**
```json
{ "senderAccountId": "sa_xyz" }
```

**Response:**
```json
{
  "senderAccountId": "sa_xyz",
  "email": "outreach@example.com",
  "status": "active",
  "connectionStatus": "connected",
  "healthGates": {
    "domainVerified": true,
    "warmupComplete": true,
    "spfValid": true,
    "dkimValid": true,
    "connectionValid": true
  },
  "ready": true,
  "lastCheckedAt": "2025-04-01T09:00:00Z"
}
```

**`healthGates`** — each gate must be `true` for the sender to be considered ready. A sender with any `false` gate will not be used for sending.

---

## create_sender

**Min autonomy:** `copilot`

Create a managed sender (email account) on an existing managed domain. The mailbox can be created before the domain's verification is complete, but the sender remains blocked from campaign use until verification and warm-up allow it.

**Arguments:**
```json
{
  "managedDomainId": "md_abc123",
  "localPart": "outreach",
  "displayName": "Outreach Team"
}
```

| Field | Required | Description |
|---|---|---|
| `managedDomainId` | Yes | The domain to create the mailbox on (`md_...`) |
| `localPart` | Yes | The part before `@` (e.g., `"outreach"` → `outreach@yourdomain.com`) |
| `displayName` | No | Sender name shown to recipients |

**Response:**
```json
{
  "success": true,
  "senderAccountId": "sa_xyz",
  "email": "outreach@yourdomain.com",
  "status": "provisioning",
  "message": "Sender created. It will become ready after domain verification and warm-up complete."
}
```

**Warm-up:** Newly created senders go through an automated warm-up period before reaching `active` status. Listen for `sender.ready` event.

---

## assign_sender_to_campaign

**Min autonomy:** `copilot`

Assign a ready managed sender to a campaign. The sender must be in `active` status.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "senderAccountId": "sa_xyz"
}
```

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "senderAccountId": "sa_xyz",
  "email": "outreach@yourdomain.com"
}
```

---

## pause_sender

**Min autonomy:** `autonomous`

Pause a sender account and mark it unavailable for campaign sending. Campaigns that have this sender assigned will skip it until it is resumed via the dashboard.

**Arguments:**
```json
{ "senderAccountId": "sa_xyz" }
```

**Response:**
```json
{
  "success": true,
  "senderAccountId": "sa_xyz",
  "status": "paused"
}
```

---

## delete_sender

**Min autonomy:** `autonomous`

Delete a managed sender account and its associated inbox. This action is irreversible — all email history associated with this sender is lost.

**Arguments:**
```json
{ "senderAccountId": "sa_xyz" }
```

**Response:**
```json
{
  "success": true,
  "senderAccountId": "sa_xyz",
  "deleted": true
}
```
