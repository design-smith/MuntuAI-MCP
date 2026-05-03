# Agent Decision Guide

Quick-reference decision trees for common situations agents encounter in MuntuAI MCP.

---

## What Tool Should I Call?

### I want to read data
```
What data?
├── All campaigns list → resources/read: muntu://campaigns/{wsId}
├── All domains list → resources/read: muntu://domains/{wsId}
├── All senders list → resources/read: muntu://senders/{wsId}
├── Recent events → resources/read: muntu://events/{wsId}?cursor=0
├── One campaign's metrics → get_campaign_performance
├── One campaign's lead counts → get_lead_group_details
├── Leads with enrichment data → get_lead_sample
├── One domain's DNS status → check_domain_status
└── One sender's health → get_sender_health
```

### I want to take an action
```
What action?
├── Create a campaign → create_campaign
├── Launch a campaign → launch_campaign
├── Review drafts → sample_campaign_drafts → send_campaign_drafts
├── Add a domain → add_domain
├── Verify a domain → trigger_domain_verification
├── Create a sender → create_sender
├── Assign sender to campaign → assign_sender_to_campaign
├── Set up webhooks → subscribe_events
├── Pause a campaign (autonomous only) → pause_campaign
└── Resume a campaign (autonomous only) → resume_campaign
```

---

## My Tool Call Failed — What Now?

```
Error received?
├── "Insufficient autonomy level"
│    → Stop. Don't retry. Report to user: need higher-autonomy key.
│
├── "Rate limit exceeded. Retry after N seconds."
│    → Wait N seconds exactly. Then retry once.
│
├── "Unauthorized"
│    → Key is invalid, revoked, or expired.
│    → Call get_agent_key_info to check. Report to user.
│
├── "Invalid params" (code -32602)
│    → Check error.data.issues for field-level errors.
│    → Fix arguments before retrying.
│
└── "Internal error" (code -32603) with no specific message
     → Log the full error. Do not retry immediately.
     → Report to user with context.
```

---

## Domain Setup Decision Tree

```
Check list_managed_domains
├── Domain exists with nextAction: "none" → DONE, proceed to sender setup
│
├── Domain exists with nextAction: "trigger_verification"
│    → DNS is published. Call trigger_domain_verification.
│    → If still pending → wait 10 min, retry.
│
├── Domain exists with nextAction: "publish_dns_records_then_trigger_verification"
│    → Show DNS records to user.
│    → Wait for confirmation.
│    → Then trigger_domain_verification.
│
├── Domain exists with nextAction: "review_provider_errors"
│    → Call check_domain_status, read errors.
│    → Report specific errors to user.
│
└── No domain exists
     → add_domain → show DNS records → wait → trigger_domain_verification
```

---

## Sender Status Decision Tree

```
list_ready_senders
├── Senders returned → use their IDs for campaigns
│
└── No ready senders
     ├── Check resources/read: muntu://senders/{wsId}
     │    ├── Senders exist in "provisioning" status
     │    │    → Wait for warm-up. Poll get_sender_health.
     │    │    → Listen for sender.ready event.
     │    │
     │    └── No senders exist
     │         → Need a verified domain first.
     │         → create_sender on verified domain.
     │
     └── Domain not verified? → Domain setup workflow first.
```

---

## Campaign State Machine

```
[created/draft]
    │
    └── launch_campaign
         │
         └── [active: enrichment]
              │  leads getting external data
              └── [active: drafting]
                   │  personalized emails being generated
                   └── [active: sending]  OR  campaign.generation_complete event
                        │
                        ├── autosend: true → emails queuing automatically
                        │
                        └── autosend: false → drafts waiting for review
                             │
                             └── send_campaign_drafts
                                  │
                                  └── [completed]
```

**Paused state** can occur at any stage:
```
[active: any] → pause_campaign → [paused]
[paused] → resume_campaign → [active: same stage]
```

---

## When to Use Webhooks vs Polling

```
Scenario
├── I'm a long-running agent server → Use webhooks (subscribe_events)
│    → Register once, receive events as they happen
│    → No compute cost between events
│
├── I'm a script/notebook → Use polling (get_campaign_performance)
│    → Simpler to implement
│    → Poll every 30s is fine for draft completion
│
└── I need real-time reply alerts → Use webhooks
     → reply.received event fires within seconds of delivery
     → Polling would miss fast replies between poll windows
```

---

## Lead Count Sanity Checks

Before launching a campaign, verify:

```
Check workspace policy: policy.riskThresholdLeadCount
    │
    └── Lead count > riskThresholdLeadCount?
         ├── Yes → Campaign will be blocked with "lead_count_too_high"
         │         → Either: reduce leads (import_leads with smaller set)
         │         → Or: ask user to raise threshold in workspace settings
         │
         └── No → Safe to launch
```

---

## Quality Check Before Sending

After drafts are generated, always spot-check before sending:

```
sample_campaign_drafts (count: 5)
    │
    ├── Check each draft for:
    │    ├── No template placeholders ({{firstName}} appearing literally)
    │    ├── Correct company name
    │    ├── Relevant personalization (not generic)
    │    └── Length appropriate (typically <150 words for cold outreach)
    │
    ├── Quality good → send_campaign_drafts
    │
    └── Quality issues found
         → Report specific issues to user
         → Ask if they want to re-launch with updated outreachGuide
         → Do NOT send bad drafts
```
