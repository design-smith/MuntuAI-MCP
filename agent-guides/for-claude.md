# Guide for Claude (and Claude-based Agents)

This guide is written for Claude operating as an agent with access to MuntuAI MCP tools. Follow these instructions to navigate the MCP correctly and avoid common mistakes.

---

## Before You Start: Orientation

Always begin a session by reading your key info and workspace state:

```
tools/call: get_agent_key_info
```

This tells you:
- Your `autonomyLevel` — determines what you can do
- Your `workspaceId` — needed for resource URIs
- Whether your key is approaching expiry

Then read the workspace resources:

```
resources/list
→ gives you all muntu:// URIs for this workspace
```

```
resources/read: muntu://workspace/{workspaceId}
→ policy settings: approvalMode, autonomyCeiling, riskThresholdLeadCount
```

**Never guess workspace IDs.** Always read them from `resources/list`.
**Never hardcode agent keys in prompts, notes, or checked-in config.** Keep them in local secret-bearing configuration or environment variables.

---

## Autonomy Level Decision Tree

Before calling any tool, check if your level permits it:

| You want to... | Required level |
|---|---|
| Read data (campaigns, events, senders) | `observer` |
| Create campaigns, launch, send drafts | `copilot` |
| Pause/resume campaigns, delete senders | `autonomous` |
| Register webhooks | `copilot` |

If you get `"Insufficient autonomy level"` — stop. Do not retry. Inform the user that the key needs to be upgraded.

---

## Campaign Lifecycle (What Happens Asynchronously)

`launch_campaign` returns immediately. The actual work runs in the background:

```
launch_campaign → returns in ~1 second
    │
    ├── Enrichment stage (minutes) → leads get external data
    │
    ├── Drafting stage (minutes) → personalized emails generated
    │
    └── campaign.generation_complete event fires
         → sample_campaign_drafts → review → send_campaign_drafts
```

**Do not assume drafts are ready right after launch.** Poll `get_campaign_performance` and wait for `leadCounts.drafted > 0`.

---

## Reading Data: Resources vs Tools

**Use resources for listing/browsing:**
```
muntu://campaigns/{workspaceId}       → all campaigns
muntu://domains/{workspaceId}         → all domains
muntu://senders/{workspaceId}         → all senders
muntu://events/{workspaceId}?cursor=0 → recent events
```

**Use tools for targeted lookups and actions:**
```
get_campaign_performance → live metrics for one campaign
get_lead_group_details   → lead counts for one campaign
get_sender_health        → health gates for one sender
check_domain_status      → DNS status for one domain
```

---

## Handling `success: false`

Several tools return `success: false` instead of throwing an error. Always check:

```python
result = tools_call("create_campaign", {...})
if not result["success"]:
    # read result["reasons"] and report to user
    # do NOT retry without fixing the underlying issue
```

Common `reasons` and fixes:

| Reason | Fix |
|---|---|
| `lead_count_too_high` | Reduce leads or ask user to update workspace risk policy |
| `domain_not_verified` | Complete domain setup first |
| `no_ready_senders` | Wait for sender warm-up or create a new sender |
| `approval_required` | User must approve in dashboard |

---

## Domain Setup Pattern

```
1. list_managed_domains → check nextAction
2. If nextAction !== "none":
   a. add_domain (if no domain exists)
   b. Show DNS records to user
   c. Wait for user to confirm DNS published
   d. trigger_domain_verification
   e. If still pending → wait 10 min, check_domain_status, retry
3. Create sender on verified domain
4. Wait for sender.ready event or poll get_sender_health
```

**Never trigger verification immediately after adding DNS.** DNS propagation takes time. Ask the user to wait 5–30 minutes.

---

## Draft Review Pattern

```
1. launch_campaign (autosend: false)
2. Poll get_campaign_performance every 30s
3. When leadCounts.drafted > 0:
   a. sample_campaign_drafts (count: 5)
   b. Review quality — personalization, tone, accuracy
   c. If acceptable → send_campaign_drafts
   d. If not acceptable → report to user with specific issues
```

When reviewing drafts, check for:
- Correct first name / company name (no template placeholder leakage)
- Coherent connection to the lead's actual context
- Subject line specificity (not generic)
- Appropriate length (most outreach emails should be <150 words)

---

## Event Polling Pattern

When waiting for async operations, use the events resource:

```
muntu://events/{workspaceId}?cursor=0&eventType=campaign.generation_complete
```

Poll every 30 seconds. When you see the event, proceed to draft review.

Or set up a webhook at session start so you get push notifications:

```
tools/call: subscribe_events
{
  "url": "https://your-endpoint.example.com/webhook",
  "secret": "...",
  "eventTypes": ["campaign.generation_complete", "reply.received"]
}
```

---

## What NOT to Do

- **Do not guess workspace IDs or resource IDs.** Always read from the API.
- **Do not retry a blocked tool call without fixing the underlying issue.** Retrying `launch_campaign` after `no_ready_senders` will fail again.
- **Do not call `pause_campaign` or `delete_sender` with a `copilot` key.** These require `autonomous`.
- **Do not show raw IDs to users unless helpful.** Prefer names and statuses.
- **Do not assume DNS is instant.** Always warn the user that DNS changes take time.
- **Do not send all drafts without reviewing a sample.** Always spot-check quality first.

---

## Useful Starting Queries

When dropped into a new session, run these to orient yourself:

```
1. get_agent_key_info                        → who am I, what can I do
2. resources/read: muntu://workspace/{id}    → policy, counts
3. resources/read: muntu://campaigns/{id}    → active campaigns
4. resources/read: muntu://domains/{id}      → domain status
5. resources/read: muntu://senders/{id}      → sender status
```
