# CRM Tools

Tools for querying connected CRMs (HubSpot, Salesforce, Pipedrive, Zoho CRM) and launching campaigns from CRM data.

Supported providers: `hubspot`, `salesforce`, `pipedrive`, `zoho_crm`

---

## list_crm_connections

**Min autonomy:** `observer`

List all CRM providers connected to the current organization.

**Arguments:** none

**Returns:**
```json
[
  {
    "id": "crm_abc123",
    "providerId": "hubspot",
    "displayName": "Acme Corp (hubspot-portal-12345)",
    "connectedAccountId": "12345",
    "status": "connected",
    "lastUsedAt": "2026-05-07T14:32:00Z",
    "schemaFetchedAt": "2026-05-06T10:00:00Z"
  }
]
```

**Status values:**
- `connected` — active and ready to query
- `needs_reconnect` — token expired or revoked; user must re-authorize
- `disconnected` — intentionally disconnected

**When to use:** Before running any CRM query, call this to find the `connectionId` for the CRM the user wants to use.

---

## query_crm

**Min autonomy:** `copilot`

Execute a natural-language query against a connected CRM. Returns matching records (contacts, companies, deals, etc.).

**Arguments:**
```json
{
  "connectionId": "crm_abc123",
  "query": "contacts at SaaS companies in New York with more than 50 employees"
}
```

**Returns:**
```json
{
  "resultId": "res_xyz789",
  "records": [
    {
      "id": "12345",
      "firstname": "Jane",
      "lastname": "Doe",
      "email": "jane@example.com",
      "company": "Acme Corp",
      "jobtitle": "VP of Sales",
      "city": "New York"
    }
  ],
  "totalCount": 14,
  "summary": "Found 14 contacts matching 'SaaS companies in New York'",
  "objectType": "contacts",
  "connectionId": "crm_abc123",
  "providerId": "hubspot"
}
```

**Notes:**
- Object type is inferred from the query (contacts, companies/accounts, deals/opportunities)
- Results are cached for 24 hours via `resultId` for follow-up operations
- Record fields vary by provider and object type
- If the query returns no results, `records` is `[]` and `totalCount` is 0

**When to use:** When the user asks to find, list, or filter CRM records before launching a campaign.

---

## create_campaign_from_crm_result

**Min autonomy:** `copilot`

Launch a campaign directly from a CRM query result. Converts CRM records into campaign leads.

**Arguments:**
```json
{
  "resultId": "res_xyz789",
  "campaignName": "Q3 VP Sales Outreach",
  "messageIntent": "Book a 15-min demo of Muntu's AI outreach tool",
  "outreachGuide": "Lead is a VP of Sales at a SaaS company. Focus on pipeline acceleration.",
  "emailAccountIds": ["sa_abc123"],
  "dailySendLimit": 20,
  "followUpCount": 2,
  "followUpTrigger": "no_action",
  "autosend": false
}
```

**Field mapping from CRM records:**

| CRM field | Campaign lead field |
|-----------|---------------------|
| `email` / `Email` | `email` (required) |
| `firstname` + `lastname` / `Name` / `Full_Name` | `name` |
| `company` / `Account.Name` / `company_name` | `companyName` |
| `jobtitle` / `Title` / `Job_Title` | `jobTitle` |
| `website` / `Website` | `website` |

Records missing an `email` field are skipped.

**Returns:** Same shape as `create_campaign`.

**When to use:** After `query_crm` returns the records the user wants to reach. Do not call `create_campaign` separately — use this tool to preserve the CRM-to-campaign linkage.

---

## get_crm_schema

**Min autonomy:** `observer`

Fetch or refresh the field schema for a connected CRM. Useful for understanding what data fields are available before constructing a query.

**Arguments:**
```json
{
  "connectionId": "crm_abc123"
}
```

**Returns:**
```json
{
  "schema": {
    "objects": [
      {
        "name": "contacts",
        "label": "Contacts",
        "fields": [
          { "name": "firstname", "label": "First Name", "type": "string" },
          { "name": "email", "label": "Email", "type": "string" },
          { "name": "jobtitle", "label": "Job Title", "type": "string" }
        ]
      }
    ],
    "fetchedAt": "2026-05-08T10:00:00Z"
  }
}
```

**When to use:** When writing a complex CRM query that needs to reference specific field names, or when the user asks "what fields does my HubSpot have?".

---

## Typical Workflow

```
1. list_crm_connections          → pick connectionId for user's CRM
2. query_crm                     → find target records (returns resultId)
3. [optionally] show user the records and confirm
4. create_campaign_from_crm_result → launch campaign from those records
```

If the user already knows their CRM is connected and what they want to target, steps 1–2 can be combined in a single turn.

---

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| `NOT_FOUND` on `query_crm` | Connection disconnected or wrong org | Call `list_crm_connections` again |
| `INTERNAL_SERVER_ERROR` with "token expired" | Auth token stale | Tell user to reconnect from Settings → Connections → CRM |
| `needs_reconnect` status | Same as above | Surface reconnect message to user |
| Empty `records` | No matching data | Widen the query or confirm the object type |
