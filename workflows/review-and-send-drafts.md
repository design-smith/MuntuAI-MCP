# Workflow: Review and Send Drafts

Review generated campaign drafts and selectively approve or send them.

**Required autonomy level:** `copilot`  
**Trigger:** After `campaign.generation_complete` event or when `get_campaign_performance` shows `stage: "sending"` or drafted lead count > 0

---

## Overview

```
1. Confirm drafts are ready
2. Sample drafts for quality check
3. Decide: approve all or filter
4. Send approved drafts
```

---

## Step 1 — Confirm drafts are ready

```json
// tools/call: get_campaign_performance
{
  "workflowId": "wf_abc123"
}
```

**Look for:**
```json
{
  "leadCounts": {
    "drafted": 150,
    "sent": 0
  },
  "stage": "sending"
}
```

If `drafted` is 0, drafts are not yet ready. Continue polling or wait for `campaign.generation_complete` webhook.

---

## Step 2 — Sample drafts for quality check

Don't review all 150 drafts — sample a representative set:

```json
// tools/call: sample_campaign_drafts
{
  "workflowId": "wf_abc123",
  "status": "drafted",
  "count": 5
}
```

**Response:**
```json
{
  "drafts": [
    {
      "leadId": "lead_abc",
      "email": "cto@example.com",
      "subject": "Quick question about your security stack, Alex",
      "body": "Hi Alex,\n\nI noticed Acme Corp recently expanded into enterprise security monitoring...",
      "status": "drafted"
    }
  ]
}
```

**Review for:**
- Correct personalization (names, company names)
- Tone matches the outreach guide
- No hallucinations or irrelevant content
- Subject line is compelling and specific

---

## Step 3 — Full review (optional)

If the sample quality is acceptable but you want to scan all drafts:

```json
// tools/call: list_campaign_drafts
{
  "workflowId": "wf_abc123",
  "status": "drafted",
  "limit": 50,
  "offset": 0
}
```

Paginate through all drafts:
```json
{ "limit": 50, "offset": 50 }  // page 2
{ "limit": 50, "offset": 100 } // page 3
```

---

## Step 4a — Send all drafts

If quality is good across the sample, send all:

```json
// tools/call: send_campaign_drafts
{
  "workflowId": "wf_abc123"
}
```

No `leadIds` = send all drafted emails.

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "queued": 150
}
```

---

## Step 4b — Send specific leads only

If you want to exclude certain leads after review:

```json
// tools/call: send_campaign_drafts
{
  "workflowId": "wf_abc123",
  "leadIds": ["lead_abc", "lead_def", "lead_ghi"]
}
```

Only the specified leads will receive emails. Other drafted leads remain in `drafted` status and can be sent later.

---

## After Sending

Monitor delivery progress:

```json
// tools/call: get_campaign_performance
{
  "workflowId": "wf_abc123"
}
```

Watch for `leadCounts.sent` to increment and `leadCounts.opened`, `leadCounts.replied` to grow over time.

Set up a reply notification webhook if you want real-time alerts:

```json
// tools/call: subscribe_events
{
  "url": "https://your-server.example.com/webhook",
  "secret": "your-secret-here",
  "eventTypes": ["reply.received"]
}
```
