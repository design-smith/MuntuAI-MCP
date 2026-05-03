# Tools

MuntuAI MCP exposes 30 tools plus one built-in (`subscribe_events`). All tools require authentication via a bearer token and enforce the caller's autonomy level.

---

## Tool Index

| Tool | Min Level | Category | Description |
|---|---|---|---|
| [`get_agent_key_info`](meta.md#get_agent_key_info) | observer | Meta | Info about the current key |
| [`get_campaign_performance`](campaigns.md#get_campaign_performance) | observer | Campaigns | Live metrics for a campaign |
| [`list_campaign_drafts`](campaigns.md#list_campaign_drafts) | observer | Campaigns | All drafted emails for a campaign |
| [`sample_campaign_drafts`](campaigns.md#sample_campaign_drafts) | observer | Campaigns | Random sample of drafted emails |
| [`get_lead_group_details`](leads.md#get_lead_group_details) | observer | Leads | Lead status counts for a workflow |
| [`get_lead_sample`](leads.md#get_lead_sample) | observer | Leads | Sample of leads with enrichment data |
| [`list_managed_domains`](domains.md#list_managed_domains) | observer | Domains | All domains with verification status |
| [`check_domain_status`](domains.md#check_domain_status) | observer | Domains | DNS verification status for a domain |
| [`list_ready_senders`](senders.md#list_ready_senders) | observer | Senders | Senders ready to send campaigns |
| [`get_sender_health`](senders.md#get_sender_health) | observer | Senders | Health snapshot for a sender |
| [`create_campaign`](campaigns.md#create_campaign) | copilot | Campaigns | Create a new outreach campaign |
| [`update_campaign_settings`](campaigns.md#update_campaign_settings) | copilot | Campaigns | Update campaign configuration |
| [`launch_campaign`](campaigns.md#launch_campaign) | copilot | Campaigns | Start enrichment → draft → send pipeline |
| [`send_campaign_drafts`](campaigns.md#send_campaign_drafts) | copilot | Campaigns | Send drafted emails after review |
| [`submit_campaign_plan`](campaigns.md#submit_campaign_plan) | copilot | Campaigns | Submit legacy draft-review artifact |
| [`approve_campaign_plan`](campaigns.md#approve_campaign_plan) | copilot | Campaigns | Approve a pending draft-review artifact |
| [`import_leads`](leads.md#import_leads) | copilot | Leads | Import leads from array or CSV URL |
| [`enrich_lead_sample`](leads.md#enrich_lead_sample) | copilot | Leads | Enrich a sample of leads |
| [`generate_email_preview`](email-generation.md#generate_email_preview) | copilot | Email | Preview email for a lead |
| [`refine_email_preview`](email-generation.md#refine_email_preview) | copilot | Email | Regenerate preview with feedback |
| [`generate_campaign_guide`](email-generation.md#generate_campaign_guide) | copilot | Email | Campaign guide from a brief |
| [`add_domain`](domains.md#add_domain) | copilot | Domains | Register a new sending domain |
| [`trigger_domain_verification`](domains.md#trigger_domain_verification) | copilot | Domains | Trigger DNS verification |
| [`create_sender`](senders.md#create_sender) | copilot | Senders | Create a managed sender |
| [`assign_sender_to_campaign`](senders.md#assign_sender_to_campaign) | copilot | Senders | Assign sender to a campaign |
| [`subscribe_events`](meta.md#subscribe_events) | copilot | Meta | Register a webhook endpoint |
| [`pause_campaign`](campaigns.md#pause_campaign) | autonomous | Campaigns | Pause a running campaign |
| [`resume_campaign`](campaigns.md#resume_campaign) | autonomous | Campaigns | Resume a paused campaign |
| [`pause_sender`](senders.md#pause_sender) | autonomous | Senders | Pause a sender account |
| [`delete_sender`](senders.md#delete_sender) | autonomous | Senders | Delete a managed sender |

---

## Tool Categories

- **[Campaigns](campaigns.md)** — Create, launch, monitor, and review campaigns
- **[Leads](leads.md)** — Import, enrich, and inspect lead groups
- **[Senders](senders.md)** — Manage email sender accounts
- **[Domains](domains.md)** — Register and verify sending domains
- **[Email Generation](email-generation.md)** — Preview and guide generation
- **[Meta](meta.md)** — Key info and webhook registration

---

## Calling a Tool

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_campaign_performance",
    "arguments": {
      "workflowId": "wf_abc123"
    }
  }
}
```

---

## Tool Response Shape

All tools return structured content in two formats simultaneously:

```json
{
  "content": [
    { "type": "text", "text": "{\"workflowId\":\"wf_abc\", ...}" }
  ],
  "structuredContent": {
    "workflowId": "wf_abc",
    ...
  }
}
```

Prefer `structuredContent` when available. Fall back to parsing `content[0].text` as JSON.

---

## Listing All Tools

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```
