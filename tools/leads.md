# Lead Tools

Tools for importing, enriching, and inspecting leads and lead groups.

---

## import_leads

**Min autonomy:** `copilot`

Import leads into a campaign workflow. Can accept a structured array or a publicly accessible CSV URL. Creates the workflow if no `workflowId` is provided.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "leads": [
    {
      "email": "cto@example.com",
      "name": "Alex Chen",
      "companyName": "Acme Corp",
      "jobTitle": "CTO",
      "website": "https://acmecorp.com"
    }
  ]
}
```

Or from a CSV URL:
```json
{
  "workflowId": "wf_abc123",
  "sourceUrl": "https://public-storage.example.com/leads.csv"
}
```

| Field | Required | Description |
|---|---|---|
| `workflowId` | No | Target workflow. Created if omitted. |
| `leads` | Yes* | Array of lead objects |
| `sourceUrl` | Yes* | Public CSV URL (alternative to `leads`) |

*One of `leads` or `sourceUrl` is required.

**CSV format:** Must have an `email` column. Other recognized columns: `name`, `firstName`, `lastName`, `companyName`, `jobTitle`, `website`, `linkedinUrl`.

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "imported": 87,
  "skipped": 3,
  "message": "87 leads imported"
}
```

---

## get_lead_group_details

**Min autonomy:** `observer`

Get details and lead status counts for a workflow (lead group). Look up by `workflowId` or `workflowName`.

**Arguments:**
```json
{ "workflowId": "wf_abc123" }
```

Or by name:
```json
{ "workflowName": "Q2 Security Outreach" }
```

**Response:**
```json
{
  "workflowId": "wf_abc123",
  "workflowName": "Q2 Security Outreach",
  "status": "active",
  "leadCounts": {
    "total": 150,
    "uploaded": 150,
    "enriched": 148,
    "drafted": 150,
    "sent": 42,
    "opened": 18,
    "replied": 3,
    "bounced": 1,
    "failed": 0,
    "pending": 108
  }
}
```

---

## get_lead_sample

**Min autonomy:** `observer`

Fetch a sample of leads from a workflow, including enrichment data if available. Prefers enriched leads by default.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "count": 5,
  "preferEnriched": true
}
```

| Field | Default | Description |
|---|---|---|
| `count` | `5` | Number of leads to return (max 20) |
| `preferEnriched` | `true` | Return enriched leads first if available |

**Response:**
```json
{
  "workflowId": "wf_abc123",
  "leads": [
    {
      "id": "lead_xyz",
      "email": "cto@example.com",
      "name": "Alex Chen",
      "companyName": "Acme Corp",
      "jobTitle": "CTO",
      "status": "enriched",
      "enrichmentData": {
        "location": "San Francisco, CA",
        "companySize": "50-200",
        "industry": "Software",
        "recentNews": "Acme Corp raised Series B in January"
      }
    }
  ]
}
```

---

## enrich_lead_sample

**Min autonomy:** `copilot`

Enrich a sample of leads (up to 5) in a workflow. Pulls external data (LinkedIn, company info, news) to populate enrichment fields. Emits `enrichment.sample_complete` event when done.

Defaults to the first 3 unenriched leads if `leadIds` is not specified.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "leadIds": ["lead_abc", "lead_def", "lead_ghi"]
}
```

| Field | Required | Description |
|---|---|---|
| `workflowId` | Yes | Target workflow |
| `leadIds` | No | Specific leads to enrich (max 5). Defaults to first 3. |

**Response:**
```json
{
  "success": true,
  "workflowId": "wf_abc123",
  "queued": 3,
  "message": "Enrichment started for 3 leads"
}
```

**Note:** Enrichment runs asynchronously. Listen for `enrichment.sample_complete` event or poll `get_lead_sample` to see results.

**Caching:** Results are cached by email address. If a lead has been enriched in any previous campaign, the cached result is applied immediately without calling external APIs.
