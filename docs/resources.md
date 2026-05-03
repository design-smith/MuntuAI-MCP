# Resources

Resources are read-only views of workspace data. Agents read them via `resources/read` with a `muntu://` URI. All resources require authentication and are scoped to the authenticated key's workspace.

---

## Listing Available Resources

Call `resources/list` to get the URIs for your workspace:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/list",
  "params": {}
}
```

The response includes all 6 resources with their workspace-specific URIs pre-filled.

---

## The Six Resources

### workspace

**URI:** `muntu://workspace/{workspaceId}`

Returns workspace profile, active policy settings, and infrastructure counts.

```json
{
  "workspace": {
    "id": "ws_abc123",
    "name": "Acme Corp",
    "createdAt": "2025-01-15T10:00:00Z"
  },
  "policy": {
    "approvalMode": "always_require",
    "autonomyCeiling": "copilot",
    "maxDailySendLimit": 500,
    "riskThresholdLeadCount": 100
  },
  "counts": {
    "domains": 3,
    "emailAccounts": 7,
    "workspaceMembers": 2
  }
}
```

---

### domains

**URI:** `muntu://domains/{workspaceId}?cursor=0&limit=50`

Returns all workspace domains unified from three sources: Muntu-managed domains, outreach domains, and domains inferred from connected email accounts.

**Query parameters:**
| Param | Default | Max | Description |
|---|---|---|---|
| `cursor` | `0` | — | Offset to start from |
| `offset` | `0` | — | Alias for cursor |
| `limit` | `50` | `200` | Records per page |

**Response shape:**
```json
{
  "workspaceId": "ws_abc123",
  "total": 3,
  "cursor": 0,
  "nextCursor": null,
  "domains": [
    {
      "domainName": "outreach.example.com",
      "status": "verified",
      "verified": true,
      "sources": ["muntu_managed"],
      "managedDomain": { "id": "md_xyz", "status": "verified", ... },
      "verification": {
        "aggregateStatus": "verified",
        "campaignAssignmentAllowed": true,
        "tracks": [...]
      },
      "dnsRequirements": [],
      "dnsPlanSummary": { "pendingCount": 0, "verifiedCount": 5 },
      "nextAction": "none"
    }
  ]
}
```

**`nextAction` values:**
- `none` — domain is verified, no action needed
- `publish_dns_records_then_trigger_verification` — DNS records need to be added
- `trigger_verification` — DNS is published, call `trigger_domain_verification`
- `review_provider_errors` — provider returned an error, check track details
- `resolve_track_failures` — verification failed, needs investigation
- `inspect_domain_status` — unknown state, call `check_domain_status`

---

### senders

**URI:** `muntu://senders/{workspaceId}?cursor=0&limit=50`

Returns all email accounts: Muntu-created mailboxes and externally imported/connected accounts.

**Query parameters:** same as domains (`cursor`, `offset`, `limit`)

**Response shape:**
```json
{
  "workspaceId": "ws_abc123",
  "total": 4,
  "cursor": 0,
  "nextCursor": null,
  "emailAccounts": [
    {
      "id": "sa_xyz",
      "email": "hello@outreach.example.com",
      "displayName": "Hello Team",
      "source": "muntu_created",
      "imported": false,
      "status": "active",
      "connectionStatus": "connected",
      "domainName": "outreach.example.com"
    }
  ]
}
```

**`source` values:** `muntu_created` | `imported`  
**`status` values:** `active` | `provisioning` | `paused` | `suspended` | `disabled`

---

### campaigns

**URI:** `muntu://campaigns/{workspaceId}?cursor=0&limit=20`

Returns a unified view of all campaigns: active workflows and draft review plans.

**Query parameters:** `cursor`, `offset`, `limit` (default 20, max 100)

**Response shape:**
```json
{
  "workspaceId": "ws_abc123",
  "total": 12,
  "cursor": 0,
  "nextCursor": "20",
  "campaigns": [
    {
      "id": "wf_abc",
      "name": "Q2 Security Outreach",
      "status": "active",
      "source": "workflow",
      "createdAt": "2025-03-01T09:00:00Z"
    }
  ]
}
```

**`status` values:** `draft` | `active` | `paused` | `completed` | `failed` | `pending_review` | `approved` | `rejected`

---

### campaign-plans

**URI:** `muntu://campaign-plans/{workspaceId}?cursor=0&limit=20`

The draft review queue — campaign plans submitted by agents that require human or automated approval before execution.

**Query parameters:** `cursor`, `offset`, `limit` (default 20, max 100)

**Response shape:**
```json
{
  "workspaceId": "ws_abc123",
  "total": 2,
  "cursor": 0,
  "nextCursor": null,
  "plans": [
    {
      "id": "cp_xyz",
      "workflowId": "wf_abc",
      "approvalState": "pending_review",
      "strategy": "...",
      "emailSequence": [...],
      "createdAt": "2025-04-01T08:00:00Z"
    }
  ]
}
```

---

### events

**URI:** `muntu://events/{workspaceId}?cursor=0`

Recent workspace system events. 50 per page.

**Query parameters:**
| Param | Description |
|---|---|
| `cursor` | Offset (default: `0`) |
| `eventType` | Filter by event type, e.g. `campaign.launched` |
| `resourceType` | Filter by resource type, e.g. `campaign`, `domain`, `sender` |
| `actorType` | Filter by who triggered it: `system`, `user`, or `agent` |

**Example — get only campaign launch events triggered by agents:**
```
muntu://events/{workspaceId}?cursor=0&eventType=campaign.launched&actorType=agent
```

**Response shape:**
```json
{
  "workspaceId": "ws_abc123",
  "total": 47,
  "cursor": 0,
  "nextCursor": "50",
  "events": [
    {
      "id": "ev_abc",
      "eventType": "campaign.launched",
      "actorType": "agent",
      "actorId": "usr_xyz",
      "resourceType": "campaign",
      "resourceId": "wf_abc",
      "payload": { ... },
      "createdAt": "2025-04-01T09:15:00Z"
    }
  ]
}
```

See [`docs/events.md`](events.md) for all event types and payload shapes.

---

## Pagination

Resources that support pagination return:
- `total` — total record count across all pages
- `cursor` — the offset used for this page
- `nextCursor` — offset string to use for the next page, or `null` if this is the last page

To paginate:
```
muntu://domains/{workspaceId}?cursor=0&limit=50      # page 1
muntu://domains/{workspaceId}?cursor=50&limit=50     # page 2
muntu://domains/{workspaceId}?cursor=100&limit=50    # page 3
```
