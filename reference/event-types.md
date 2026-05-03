# Event Types Reference

All 21 event types emitted by MuntuAI, with full payload shapes.

---

## Domain Events

### `domain.verified`
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

### `domain.failed`
A domain verification attempt failed.
```json
{
  "eventType": "domain.failed",
  "resourceType": "domain",
  "payload": {
    "domainName": "outreach.example.com",
    "managedDomainId": "md_abc",
    "trackKey": "sending_infra",
    "reason": "DNS records not found"
  }
}
```

### `domain.verification_expired`
A previously verified domain's verification has lapsed (DNS records removed or TTL expired).
```json
{
  "eventType": "domain.verification_expired",
  "resourceType": "domain",
  "payload": {
    "domainName": "outreach.example.com",
    "managedDomainId": "md_abc"
  }
}
```

---

## Sender Events

### `sender.ready`
A sender has passed warmup and health checks and is ready to send campaigns.
```json
{
  "eventType": "sender.ready",
  "resourceType": "sender",
  "payload": {
    "senderAccountId": "sa_abc",
    "email": "hello@outreach.example.com"
  }
}
```

### `sender.paused`
A sender has been paused (manually or by policy).
```json
{
  "eventType": "sender.paused",
  "resourceType": "sender",
  "payload": {
    "senderAccountId": "sa_abc",
    "email": "hello@outreach.example.com",
    "reason": "manual"
  }
}
```

### `sender.suspended`
A sender has been suspended due to delivery issues or policy violations.
```json
{
  "eventType": "sender.suspended",
  "resourceType": "sender",
  "payload": {
    "senderAccountId": "sa_abc",
    "email": "hello@outreach.example.com",
    "reason": "bounce_rate_exceeded"
  }
}
```

---

## Campaign Events

### `campaign.launched`
A campaign has started (enrichment stage beginning).
```json
{
  "eventType": "campaign.launched",
  "resourceType": "campaign",
  "payload": {
    "workflowId": "wf_abc",
    "workflowName": "Q2 Security Outreach",
    "leadCount": 150
  }
}
```

### `campaign.approved`
A campaign draft was approved and a workflow was created.
```json
{
  "eventType": "campaign.approved",
  "resourceType": "campaign",
  "payload": {
    "workflowId": "wf_abc",
    "workflowName": "Q2 Security Outreach"
  }
}
```

### `campaign.pending_review`
A campaign draft was submitted and is waiting for approval.
```json
{
  "eventType": "campaign.pending_review",
  "resourceType": "campaign_plan",
  "payload": {
    "planId": "cp_abc",
    "workflowName": "Q2 Security Outreach"
  }
}
```

### `campaign.rejected`
A campaign draft was rejected.
```json
{
  "eventType": "campaign.rejected",
  "resourceType": "campaign_plan",
  "payload": {
    "planId": "cp_abc",
    "reason": "Content policy violation"
  }
}
```

### `campaign.paused`
A running campaign was paused (at the next batch checkpoint).
```json
{
  "eventType": "campaign.paused",
  "resourceType": "campaign",
  "payload": {
    "workflowId": "wf_abc",
    "pauseReason": "daily_limit",
    "stage": "sending"
  }
}
```

**`pauseReason` values:** `daily_limit` | `policy_block` | `sender_issue` | `manual`

### `campaign.policy_blocked`
A campaign was blocked by workspace safety policy before launch.
```json
{
  "eventType": "campaign.policy_blocked",
  "resourceType": "campaign",
  "payload": {
    "workflowId": "wf_abc",
    "reasons": ["lead_count_too_high", "domain_not_verified"]
  }
}
```

### `campaign.generation_complete`
All email drafts for a campaign have been generated and are ready for review or sending.
```json
{
  "eventType": "campaign.generation_complete",
  "resourceType": "campaign",
  "payload": {
    "workflowId": "wf_abc",
    "workflowName": "Q2 Security Outreach",
    "draftCount": 150
  }
}
```

---

## Campaign Sender Assignment Events

### `campaign.sender.assigned`
A sender was assigned to a campaign.
```json
{
  "eventType": "campaign.sender.assigned",
  "resourceType": "campaign_sender_assignment",
  "payload": {
    "workflowId": "wf_abc",
    "senderAccountId": "sa_xyz",
    "email": "hello@outreach.example.com"
  }
}
```

### `campaign.sender.paused`
A sender assignment was paused within a campaign.
```json
{
  "eventType": "campaign.sender.paused",
  "resourceType": "campaign_sender_assignment",
  "payload": {
    "workflowId": "wf_abc",
    "senderAccountId": "sa_xyz",
    "email": "hello@outreach.example.com"
  }
}
```

### `campaign.sender.removed`
A sender was removed from a campaign assignment.
```json
{
  "eventType": "campaign.sender.removed",
  "resourceType": "campaign_sender_assignment",
  "payload": {
    "workflowId": "wf_abc",
    "senderAccountId": "sa_xyz"
  }
}
```

---

## Agent Events

### `agent.action.permitted`
An agent tool call was authenticated and authorized.
```json
{
  "eventType": "agent.action.permitted",
  "resourceType": "assistant_tool",
  "actorType": "agent",
  "payload": {
    "toolName": "create_campaign",
    "autonomyLevel": "copilot",
    "agentKeyId": "ak_abc"
  }
}
```

### `agent.action.blocked`
An agent tool call was rejected (wrong autonomy level, rate limit, etc.).
```json
{
  "eventType": "agent.action.blocked",
  "resourceType": "assistant_tool",
  "actorType": "agent",
  "payload": {
    "toolName": "pause_campaign",
    "reason": "autonomy_level_insufficient",
    "requiredLevel": "autonomous",
    "agentLevel": "copilot"
  }
}
```

### `agent.tool.invoked`
An agent successfully executed a tool. Emitted after the tool completes.
```json
{
  "eventType": "agent.tool.invoked",
  "resourceType": "assistant_tool",
  "actorType": "agent",
  "payload": {
    "toolName": "launch_campaign",
    "args": { "workflowId": "wf_abc" }
  }
}
```

---

## Lead & Enrichment Events

### `enrichment.sample_complete`
A lead enrichment sample (triggered by `enrich_lead_sample`) has completed.
```json
{
  "eventType": "enrichment.sample_complete",
  "resourceType": "lead_group",
  "payload": {
    "workflowId": "wf_abc",
    "enrichedCount": 3,
    "failedCount": 0
  }
}
```

### `reply.received`
A lead replied to a campaign email.
```json
{
  "eventType": "reply.received",
  "resourceType": "lead",
  "payload": {
    "workflowId": "wf_abc",
    "leadId": "lead_xyz",
    "email": "contact@example.com",
    "subject": "Re: Your outreach"
  }
}
```

---

## Filtering Events

Events can be filtered when reading via the resource:

```
muntu://events/{workspaceId}?cursor=0&eventType=reply.received
muntu://events/{workspaceId}?cursor=0&resourceType=campaign&actorType=agent
muntu://events/{workspaceId}?cursor=0&eventType=campaign.generation_complete
```

Available filter params:
| Param | Values |
|---|---|
| `eventType` | Any of the 21 event types above |
| `resourceType` | `domain`, `sender`, `campaign`, `lead`, `campaign_plan`, `campaign_sender_assignment`, `lead_group`, `request`, `assistant_tool` |
| `actorType` | `system`, `user`, `agent` |
