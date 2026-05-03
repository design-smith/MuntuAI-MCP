# Events

MuntuAI emits system events whenever significant things happen in a workspace. Events can be read via the `events` resource or delivered to external systems via webhooks.

---

## Reading Events

Via the events resource (paginated, 50 per page):

```
muntu://events/{workspaceId}?cursor=0
```

With filters:

```
muntu://events/{workspaceId}?cursor=0&eventType=campaign.launched
muntu://events/{workspaceId}?cursor=0&actorType=agent
muntu://events/{workspaceId}?cursor=0&resourceType=domain
```

Available filter parameters:
| Param | Values |
|---|---|
| `eventType` | Any of the 21 event types below |
| `resourceType` | `domain`, `sender`, `campaign`, `lead`, `campaign_plan`, `campaign_sender_assignment`, `lead_group`, `request`, `assistant_tool` |
| `actorType` | `system`, `user`, `agent` |

---

## Event Object Shape

```json
{
  "id": "ev_aBcDeFgH",
  "eventType": "campaign.launched",
  "workspaceId": "ws_xyz",
  "actorType": "agent",
  "actorId": "usr_abc",
  "agentKeyId": "ak_def",
  "resourceType": "campaign",
  "resourceId": "wf_ghi",
  "payload": { ... },
  "createdAt": "2025-04-01T09:15:00Z"
}
```

- `actorType` — who triggered the event: `system` (automated), `user` (human via UI), or `agent` (via MCP key)
- `agentKeyId` — set when `actorType` is `agent`, identifies which key was used
- `payload` — event-specific data (see below)

---

## All Event Types

### Domain Events

#### `domain.verified`
A domain passed verification with the email provider.
```json
{
  "eventType": "domain.verified",
  "resourceType": "domain",
  "payload": {
    "domainName": "outreach.example.com",
    "managedDomainId": "md_abc",
    "trackKey": "sending_infra"
  }
}
```

#### `domain.failed`
A domain verification attempt failed.
```json
{
  "payload": {
    "domainName": "outreach.example.com",
    "managedDomainId": "md_abc",
    "trackKey": "sending_infra",
    "reason": "DNS records not found"
  }
}
```

#### `domain.verification_expired`
A previously verified domain's verification has lapsed.

---

### Sender Events

#### `sender.ready`
A sender has passed warmup and health checks and is ready to send campaigns.
```json
{
  "payload": {
    "senderAccountId": "sa_abc",
    "email": "hello@outreach.example.com"
  }
}
```

#### `sender.paused`
A sender has been paused (manually or by policy).

#### `sender.suspended`
A sender has been suspended due to delivery issues or policy violations.

---

### Campaign Events

#### `campaign.launched`
A campaign has started (enrichment stage beginning).
```json
{
  "payload": {
    "workflowId": "wf_abc",
    "workflowName": "Q2 Security Outreach",
    "leadCount": 150
  }
}
```

#### `campaign.approved`
A campaign draft was approved and a workflow was created.

#### `campaign.pending_review`
A campaign draft was submitted and is waiting for approval.

#### `campaign.rejected`
A campaign draft was rejected.

#### `campaign.paused`
A running campaign was paused (at the next batch checkpoint).
```json
{
  "payload": {
    "workflowId": "wf_abc",
    "pauseReason": "daily_limit",
    "stage": "sending"
  }
}
```

#### `campaign.policy_blocked`
A campaign was blocked by workspace safety policy before launch.
```json
{
  "payload": {
    "workflowId": "wf_abc",
    "reasons": ["lead_count_too_high", "domain_not_verified"]
  }
}
```

#### `campaign.generation_complete`
All email drafts for a campaign have been generated and are ready for review or sending.

---

### Campaign Sender Assignment Events

#### `campaign.sender.assigned`
A sender was assigned to a campaign.
```json
{
  "payload": {
    "workflowId": "wf_abc",
    "senderAccountId": "sa_xyz",
    "email": "hello@outreach.example.com"
  }
}
```

#### `campaign.sender.paused`
A sender assignment was paused within a campaign.

#### `campaign.sender.removed`
A sender was removed from a campaign assignment.

---

### Agent Events

#### `agent.action.permitted`
An agent tool call was authenticated and authorized.
```json
{
  "payload": {
    "toolName": "create_campaign",
    "autonomyLevel": "copilot",
    "agentKeyId": "ak_abc"
  }
}
```

#### `agent.action.blocked`
An agent tool call was rejected (wrong autonomy level, rate limit, etc.).
```json
{
  "payload": {
    "toolName": "pause_campaign",
    "reason": "autonomy_level_insufficient",
    "requiredLevel": "autonomous",
    "agentLevel": "copilot"
  }
}
```

#### `agent.tool.invoked`
An agent successfully executed a tool. Emitted after the tool completes.
```json
{
  "payload": {
    "toolName": "launch_campaign",
    "args": { "workflowId": "wf_abc" }
  }
}
```

---

### Lead & Enrichment Events

#### `enrichment.sample_complete`
A lead enrichment sample (triggered by `enrich_lead_sample`) has completed.
```json
{
  "payload": {
    "workflowId": "wf_abc",
    "enrichedCount": 3,
    "failedCount": 0
  }
}
```

#### `reply.received`
A lead replied to a campaign email.
```json
{
  "payload": {
    "workflowId": "wf_abc",
    "leadId": "lead_xyz",
    "email": "contact@example.com",
    "subject": "Re: Your outreach"
  }
}
```

---

## Using Events for Agent Loops

Events are the primary way for agents to know when async operations complete.

**Pattern: Launch and poll**
```
1. Call launch_campaign → returns immediately
2. Read events resource every 30s filtering for campaign.generation_complete or campaign.paused
3. When campaign.generation_complete fires → call sample_campaign_drafts to review
4. Decide to send → call send_campaign_drafts
```

**Pattern: Webhook-driven**
```
1. Call subscribe_events (via MCP) or register webhook (via UI)
2. Muntu POSTs events to your endpoint as they happen
3. Your handler triggers agent actions in response
```

See [`docs/webhooks.md`](webhooks.md) for webhook setup.
