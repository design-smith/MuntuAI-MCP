# Workflows

End-to-end guides for common agent tasks. Each workflow documents the exact sequence of tool calls, what to check at each step, and how to handle errors.

---

## Available Workflows

| Workflow | Description |
|---|---|
| [Launch First Campaign](launch-first-campaign.md) | Full setup from scratch: domain → sender → leads → campaign → launch |
| [Review and Send Drafts](review-and-send-drafts.md) | Review generated drafts and selectively send |
| [Domain Setup](domain-setup.md) | Register a domain and verify DNS |
| [Monitor Campaign](monitor-campaign.md) | Poll performance and react to events |

---

## General Principles

**All MCP calls return immediately.** Campaign operations (enrichment, drafting, sending) run asynchronously. Use `get_campaign_performance` to poll progress or register webhooks for push notifications.

**Check `success: false` in responses.** Several tools return success-shaped responses with `success: false` when a business rule is violated. Always check this field before proceeding.

**Prefer resources over tools for reading.** The `muntu://` resources are paginated read views optimized for listing. Use tools for actions and targeted lookups.

**Autonomy levels gate tool access.** Always call `get_agent_key_info` at the start of a session to confirm what the key can do. Don't attempt autonomous-level operations with a copilot key.

---

## Decision Flowchart

```
Start
 │
 ├── Need to read data only? → Use resources (muntu:// URIs)
 │
 ├── Need to act on a campaign?
 │    ├── Campaign doesn't exist yet → create_campaign
 │    ├── Campaign exists but not launched → launch_campaign
 │    ├── Campaign launched, waiting for drafts → poll get_campaign_performance
 │    ├── Drafts ready → sample_campaign_drafts → send_campaign_drafts
 │    └── Campaign running → get_campaign_performance (poll or webhook)
 │
 ├── Need to set up infrastructure?
 │    ├── No domain → add_domain → (wait for DNS) → trigger_domain_verification
 │    └── No sender → create_sender → (wait for warm-up) → sender.ready event
 │
 └── Need to monitor events? → subscribe_events (webhook) or events resource
```
