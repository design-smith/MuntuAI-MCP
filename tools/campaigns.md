# Campaign Tools

Tools for creating, launching, monitoring, pausing, and reviewing campaigns.

---

## create_campaign

**Min autonomy:** `copilot`

Create an outreach campaign. This is the primary tool for setting up a campaign end-to-end — it accepts leads, sending accounts, email configuration, and follow-up settings in a single call.

**Arguments:**
```json
{
  "name": "Q2 Security Outreach",
  "sampleEmail": "Hi {{firstName}},\n\nI noticed you're leading security at {{companyName}}...",
  "outreachGuide": "Focus on the specific security challenge relevant to the lead's company size.",
  "messageIntent": "Book a 15-minute demo for Zykr cybersecurity platform",
  "emailAccountIds": ["sa_abc123"],
  "leads": [
    {
      "email": "cto@example.com",
      "name": "Alex Chen",
      "companyName": "Acme Corp",
      "jobTitle": "CTO",
      "website": "https://acmecorp.com"
    }
  ],
  "autoRespond": true,
  "autoSendResponses": false,
  "autosend": false,
  "dailySendLimit": 25,
  "followUpCount": 2,
  "followUpWindow": 5,
  "followUpTrigger": "no_action"
}
```

**Key fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Campaign display name |
| `sampleEmail` | string | Yes | Template email. Use `{{firstName}}`, `{{companyName}}`, etc. |
| `outreachGuide` | string | Yes | Instructions for the AI when drafting personalized emails |
| `messageIntent` | string | Yes | One-line goal of the campaign |
| `emailAccountIds` | string[] | Yes* | Sender account IDs to use (`sa_...`) |
| `emailAddresses` | string[] | Yes* | Alternative: pass email addresses instead of IDs |
| `leads` | Lead[] | Yes* | Array of lead objects |
| `sourceUrl` | string | Yes* | Alternative: public CSV URL for leads |
| `autosend` | boolean | No | If true, emails send automatically without draft review |
| `dailySendLimit` | number | No | Max emails per day across all senders |
| `followUpCount` | number | No | Number of follow-up emails (0-5) |
| `followUpWindow` | number | No | Days between follow-ups |
| `followUpTrigger` | string | No | `"no_action"` or `"no_open"` |

*At least one of `emailAccountIds`/`emailAddresses` is required; at least one of `leads`/`sourceUrl` is required.

**Lead object shape:**
```json
{
  "email": "required@example.com",
  "name": "Optional Name",
  "companyName": "Optional Company",
  "jobTitle": "Optional Job Title",
  "website": "https://optional-website.com",
  "linkedinUrl": "https://linkedin.com/in/optional"
}
```

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "leadCount": 42,
  "message": "Campaign created successfully"
}
```

If blocked by workspace policy:
```json
{
  "success": false,
  "blocked": true,
  "reasons": ["lead_count_too_high", "no_ready_senders"],
  "workflowId": null
}
```

---

## update_campaign_settings

**Min autonomy:** `copilot`

Update the configuration of an existing campaign. Uses the same fields as `create_campaign`. Only provided fields are updated.

**Arguments:** Same shape as `create_campaign`, plus:
```json
{
  "workflowId": "wf_abc123"
}
```

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123"
}
```

---

## launch_campaign

**Min autonomy:** `copilot`

Start a campaign. Triggers the full autonomous pipeline: enrichment → drafting → sending (or draft review if `autosend: false`). Returns immediately — the pipeline runs asynchronously.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "autosend": false,
  "messageIntent": "Book a 15-minute demo",
  "outreachGuide": "Focus on pain points from their recent blog posts.",
  "dailySendLimit": 30
}
```

| Field | Required | Description |
|---|---|---|
| `workflowId` | Yes | The campaign to launch |
| `autosend` | No | Override autosend setting for this launch |
| `messageIntent` | No | Override message intent |
| `outreachGuide` | No | Override outreach guide |
| `dailySendLimit` | No | Override daily send limit |

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "message": "Campaign launched"
}
```

**After launch:** Poll `get_campaign_performance` or listen for `campaign.generation_complete` webhook event to know when drafts are ready.

---

## pause_campaign

**Min autonomy:** `autonomous`

Pause a running campaign. The pipeline halts at the next batch checkpoint (not mid-batch).

**Arguments:**
```json
{ "workflowId": "wf_abc123" }
```

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "status": "paused"
}
```

---

## resume_campaign

**Min autonomy:** `autonomous`

Resume a paused campaign from its last checkpoint stage.

**Arguments:**
```json
{ "workflowId": "wf_abc123" }
```

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "status": "active"
}
```

---

## get_campaign_performance

**Min autonomy:** `observer`

Get live performance metrics for a campaign. Safe to poll every 30 seconds.

**Arguments:**
```json
{ "workflowId": "wf_abc123" }
```

**Response:**
```json
{
  "workflowId": "wf_abc123",
  "workflowName": "Q2 Security Outreach",
  "status": "active",
  "stage": "sending",
  "leadCounts": {
    "total": 150,
    "enriched": 148,
    "drafted": 150,
    "sent": 42,
    "opened": 18,
    "replied": 3,
    "bounced": 1,
    "failed": 0
  },
  "metrics": {
    "openRate": 0.43,
    "replyRate": 0.07,
    "bounceRate": 0.02,
    "clickRate": 0.12
  }
}
```

**`stage` values:** `enrichment` | `drafting` | `sending` | `complete`

---

## list_campaign_drafts

**Min autonomy:** `observer`

Return all drafted emails for a campaign for full review.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "status": "drafted",
  "limit": 50,
  "offset": 0
}
```

| Field | Default | Description |
|---|---|---|
| `status` | `"all"` | `"drafted"` \| `"pending_review"` \| `"all"` |
| `limit` | `250` | Max records to return |
| `offset` | `0` | Pagination offset |

**Response:**
```json
{
  "workflowId": "wf_abc123",
  "total": 150,
  "drafts": [
    {
      "leadId": "lead_xyz",
      "email": "cto@example.com",
      "subject": "Quick question about your security stack",
      "body": "Hi Alex,\n\n...",
      "status": "drafted"
    }
  ]
}
```

---

## sample_campaign_drafts

**Min autonomy:** `observer`

Return a random sample of drafted emails for spot-checking quality before sending.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "status": "drafted",
  "count": 5
}
```

**Response:** Same shape as `list_campaign_drafts` but with a random subset.

---

## send_campaign_drafts

**Min autonomy:** `copilot`

Send drafted emails after review. If `leadIds` is omitted, sends all drafted emails in the workflow.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "leadIds": ["lead_abc", "lead_def"]
}
```

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "queued": 42
}
```

---

## submit_campaign_plan

**Min autonomy:** `copilot`

Submit a legacy draft-review artifact for workspace policy evaluation and creation. Used by older agent flows; prefer `create_campaign` + `launch_campaign` for new integrations.

---

## approve_campaign_plan

**Min autonomy:** `copilot`

Approve a pending legacy draft-review artifact and create its workflow. Pair with `submit_campaign_plan`.
