# Workflow: Launch First Campaign

Full end-to-end setup from scratch: infrastructure → leads → campaign → launch.

**Required autonomy level:** `copilot`  
**Time to complete:** ~5–30 minutes (most time is DNS propagation and sender warm-up)

---

## Overview

```
1. Confirm infrastructure (domains + senders)
2. Add domain (if needed)
3. Publish DNS records → trigger verification
4. Create sender (if needed)
5. Create campaign with leads
6. Launch campaign
7. Monitor progress
```

---

## Step 1 — Check existing infrastructure

Read the workspace state before doing anything:

```json
// resources/read
{ "uri": "muntu://workspace/{workspaceId}" }
```

```json
// resources/read
{ "uri": "muntu://domains/{workspaceId}" }
```

```json
// resources/read
{ "uri": "muntu://senders/{workspaceId}" }
```

**Check:**
- Does a verified domain exist with `nextAction: "none"`?
- Does a ready sender exist with `status: "active"`?

If both exist, skip to Step 5.

---

## Step 2 — Add domain (if needed)

```json
// tools/call: add_domain
{
  "domainName": "outreach.yourdomain.com"
}
```

**Response includes `dnsRecords`** — these must be published to your DNS provider before proceeding. Show the DNS records to the user and ask them to add them.

**DNS record types to expect:**
- `TXT` — SPF record
- `CNAME` — DKIM records (usually 2)
- `CNAME` — Tracking/open pixel

---

## Step 3 — Trigger domain verification

After the user confirms DNS records are published (allow 5–30 minutes for propagation):

```json
// tools/call: trigger_domain_verification
{
  "managedDomainId": "md_abc123"
}
```

**If `status: "pending"`** — DNS hasn't propagated yet. Wait and retry. Call `check_domain_status` to re-check without triggering a full re-verification:

```json
// tools/call: check_domain_status
{
  "managedDomainId": "md_abc123"
}
```

**If `status: "verified"`** — proceed to Step 4.

---

## Step 4 — Create sender (if needed)

```json
// tools/call: create_sender
{
  "managedDomainId": "md_abc123",
  "localPart": "outreach",
  "displayName": "Outreach Team"
}
```

**Response:** `status: "provisioning"` — the sender needs to warm up before it can send.

Listen for `sender.ready` event (via webhook) or poll `get_sender_health`:

```json
// tools/call: get_sender_health
{
  "senderAccountId": "sa_xyz"
}
```

**When `ready: true`** — sender is active and can be used for campaigns.

---

## Step 5 — Create campaign

```json
// tools/call: create_campaign
{
  "name": "Q2 Security Outreach",
  "sampleEmail": "Hi {{firstName}},\n\nI noticed you're leading security at {{companyName}}. Teams in that role often tell us they spend too much time on manual threat triage.\n\nZykr automates that investigation work so analysts can focus on response and prevention.\n\nWould you be open to a quick 15-minute demo?\n\nBest,\nNathan",
  "outreachGuide": "Open with a specific observation about the company's security posture or recent growth. In the second paragraph, connect to how Zykr reduces analyst time on manual triage. Keep it under 100 words.",
  "messageIntent": "Book a 15-minute Zykr cybersecurity demo",
  "emailAccountIds": ["sa_xyz"],
  "leads": [
    {
      "email": "cto@example.com",
      "name": "Alex Chen",
      "companyName": "Acme Corp",
      "jobTitle": "CTO",
      "website": "https://acmecorp.com"
    }
  ],
  "autosend": false,
  "dailySendLimit": 25,
  "followUpCount": 2,
  "followUpWindow": 5,
  "followUpTrigger": "no_action"
}
```

**Check response for `success: false`:**

```json
{
  "success": false,
  "blocked": true,
  "reasons": ["lead_count_too_high"]
}
```

Common blockers and fixes:
| Reason | Fix |
|---|---|
| `lead_count_too_high` | Reduce leads or ask workspace owner to increase risk threshold |
| `domain_not_verified` | Complete domain verification first |
| `no_ready_senders` | Wait for sender warm-up or assign a ready sender |
| `approval_required` | Workspace requires human approval — submit via UI |

---

## Step 6 — (Optional) Preview a draft

Before launching, verify quality by generating a preview email:

```json
// tools/call: generate_email_preview
{
  "workflowId": "wf_abc123",
  "leadId": "lead_xyz",
  "sampleEmail": "...",
  "outreachGuide": "...",
  "messageIntent": "Book a 15-minute Zykr cybersecurity demo"
}
```

Review the generated subject and body. Use `refine_email_preview` if changes are needed.

---

## Step 7 — Launch campaign

```json
// tools/call: launch_campaign
{
  "workflowId": "wf_abc123",
  "autosend": false
}
```

**Returns immediately.** The pipeline runs asynchronously:
1. Enrichment — pulls data for each lead
2. Drafting — generates personalized emails
3. (If `autosend: false`) Pauses for draft review

---

## Step 8 — Monitor progress

Poll every 30 seconds:

```json
// tools/call: get_campaign_performance
{
  "workflowId": "wf_abc123"
}
```

**When `stage: "sending"` or `leadCounts.drafted > 0`** — drafts are ready for review.

Or use webhooks to get push notification when drafts are ready (no polling needed):

```json
// tools/call: subscribe_events
{
  "url": "https://your-server.example.com/webhook",
  "secret": "your-secret-min-16-chars",
  "eventTypes": ["campaign.generation_complete"]
}
```

---

## Step 9 — Review and send drafts

See [Review and Send Drafts workflow](review-and-send-drafts.md).
