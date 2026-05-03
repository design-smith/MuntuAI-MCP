# Guide for Cursor (and Cursor-based Agents)

This guide is for Cursor AI operating with MuntuAI MCP tools connected. It covers setup, common patterns, and pitfalls specific to the Cursor environment.

---

## Setup in Cursor

Add to your Cursor MCP config (`~/.cursor/mcp.json` or project-level `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "muntuai": {
      "url": "https://api.muntuai.com/api/mcp",
      "headers": {
        "Authorization": "Bearer ${env:MUNTU_AGENT_KEY}"
      }
    }
  }
}
```

Restart Cursor after editing. The MuntuAI tools will appear in the tool picker.
Security note: keep the agent key in an environment variable if your Cursor config supports interpolation. Do not paste the raw key into a committed project config.

---

## Verifying Connection

Ask Cursor: "Call get_agent_key_info and show me the result."

Expected response:
```json
{
  "workspaceId": "ws_...",
  "name": "My Agent Key",
  "autonomyLevel": "copilot",
  ...
}
```

If this fails, check:
1. The `Authorization` header contains your full key (`mnt_...`)
2. The URL is exactly `https://api.muntuai.com/api/mcp`
3. Cursor has been restarted after config changes

---

## Common Use Cases in Cursor

### Check campaign status
> "Read the campaigns resource and show me all active campaigns."

Cursor will call `resources/list` to get the URI, then `resources/read` to get the data.

### Launch a campaign
> "Create a campaign called 'Q2 Outreach' targeting [leads]. Use [email account]. Draft a sample email about [product]. Launch it with autosend off."

Cursor will call `create_campaign` then `launch_campaign`.

### Review drafts
> "Sample 5 drafts from campaign wf_abc123 and tell me if the quality looks good."

Cursor will call `sample_campaign_drafts` and analyze the results.

### Domain setup
> "Add the domain outreach.example.com and tell me what DNS records to add."

Cursor will call `add_domain` and present the DNS records.

---

## Resource URIs

Cursor needs to call `resources/list` first to get workspace-specific URIs. Prompt it explicitly if needed:

> "Call resources/list first, then read the campaigns resource."

Or reference the resource by name:

> "Read the 'campaigns' resource."

Cursor will resolve the URI automatically using the list response.

---

## Autonomy Levels in Cursor

If Cursor gets an "Insufficient autonomy level" error, it means the tool requires a higher-level key. Common cases:

| Attempted action | Required level | Error |
|---|---|---|
| Pause a campaign | `autonomous` | "Insufficient autonomy level" |
| Delete a sender | `autonomous` | "Insufficient autonomy level" |
| Create a campaign | `copilot` | "Insufficient autonomy level" |

Fix: Create a new key with the required autonomy level in Settings → Agent Keys.

---

## Prompting Tips for Cursor

**Be specific about IDs.** Cursor works best when you provide workflow IDs directly:
> "Get performance for workflow wf_abc123"

**Chain operations explicitly:**
> "Create the campaign, then launch it, then poll performance once."

**Separate reading from acting:**
> "First list all campaigns. Then, separately, launch the one called 'Q2 Outreach'."

**Handle async correctly:**
> "Launch the campaign, then check performance every 30 seconds until drafts appear. When they do, sample 5 and show me."

---

## What Cursor Cannot Do (Without Your Help)

- **Publish DNS records** — Cursor can tell you what records to add, but you have to add them at your DNS provider (Cloudflare, Route53, etc.)
- **Approve campaigns in the UI** — When `approvalMode: "always_require"`, a human must approve in the dashboard
- **Create or revoke keys** — Key management is UI-only

---

## Troubleshooting

**Tool not found in Cursor:**
- Restart Cursor after editing the MCP config
- Verify the config file location (`~/.cursor/mcp.json` vs project-level)
- Check that `muntuai` key in the config matches what Cursor expects

**Authentication errors:**
- Confirm the key starts with `mnt_` and includes both the keyId and secret separated by `.`
- Check that the key hasn't been revoked in the MuntuAI dashboard
- Confirm the key hasn't expired (`expiresAt` in `get_agent_key_info`)

**Rate limit errors:**
- Copilot/autonomous keys: 120 requests/minute
- Observer keys: 60 requests/minute
- Cursor may retry automatically — if it keeps failing, wait 60 seconds
