# Workflow: Monitor Campaign

Track campaign progress, react to events, and know when to take action.

**Required autonomy level:** `observer` (for monitoring); `copilot`/`autonomous` for actions

---

## Polling Approach

The simplest monitoring strategy: poll `get_campaign_performance` on a schedule.

```json
// tools/call: get_campaign_performance
{
  "workflowId": "wf_abc123"
}
```

**Recommended polling interval:** 30 seconds during active stages; 5 minutes once in `sending` stage.

**Key fields to watch:**

```json
{
  "status": "active",
  "stage": "drafting",
  "leadCounts": {
    "total": 150,
    "enriched": 120,
    "drafted": 45,
    "sent": 0,
    "replied": 0,
    "bounced": 0
  }
}
```

**Stage progression:**
```
enrichment → drafting → sending → complete
```

**Decision points by stage:**

| Stage | What's happening | When to act |
|---|---|---|
| `enrichment` | Leads getting external data | Watch for completion |
| `drafting` | Personalized emails being generated | Watch for `drafted > 0` |
| `sending` | Emails queuing and delivering | Review drafts if `autosend: false` |
| `complete` | All emails sent | Review final metrics |

---

## Webhook Approach (Recommended)

Register a webhook to get push notifications instead of polling:

```json
// tools/call: subscribe_events
{
  "url": "https://your-server.example.com/muntu-webhook",
  "secret": "your-secret-min-16-chars",
  "eventTypes": [
    "campaign.generation_complete",
    "campaign.paused",
    "reply.received",
    "enrichment.sample_complete"
  ]
}
```

**Event-driven loop:**
```
launch_campaign
    │
    ├── campaign.generation_complete → sample_campaign_drafts → send_campaign_drafts
    │
    ├── campaign.paused → get_campaign_performance (check reason) → resume_campaign or investigate
    │
    └── reply.received → notify user / log CRM
```

See [webhooks.md](../docs/webhooks.md) for payload verification and full delivery spec.

---

## Reading Events Directly

For simple monitoring without a server endpoint, poll the events resource:

```json
// resources/read
{
  "uri": "muntu://events/{workspaceId}?cursor=0&resourceType=campaign&actorType=system"
}
```

Filter to specific event types:

```json
// Only campaign events
{ "uri": "muntu://events/{workspaceId}?cursor=0&eventType=campaign.generation_complete" }
```

```json
// Only replies
{ "uri": "muntu://events/{workspaceId}?cursor=0&eventType=reply.received" }
```

---

## Handling Pauses

If a campaign pauses unexpectedly:

```json
// tools/call: get_campaign_performance
{
  "workflowId": "wf_abc123"
}
```

Check `status: "paused"`. The `campaign.paused` event payload includes `pauseReason`:

| `pauseReason` | Meaning | Action |
|---|---|---|
| `daily_limit` | Hit daily send limit | Normal — resumes tomorrow automatically |
| `policy_block` | Workspace policy blocked a batch | Check policy settings |
| `sender_issue` | Sender paused or disconnected | Check sender health |
| `manual` | Paused by user or agent | Resume when ready |

To resume (requires `autonomous` level):

```json
// tools/call: resume_campaign
{
  "workflowId": "wf_abc123"
}
```

---

## Monitoring Multiple Campaigns

Read all active campaigns at once:

```json
// resources/read
{ "uri": "muntu://campaigns/{workspaceId}?cursor=0&limit=20" }
```

Then call `get_campaign_performance` for any that show `status: "active"`.

---

## Performance Benchmarks

Typical good campaign metrics for reference:

| Metric | Target |
|---|---|
| Open rate | > 30% |
| Reply rate | > 5% |
| Bounce rate | < 5% |

High bounce rate (> 5%) is a deliverability warning sign — consider pausing and investigating sender health.
