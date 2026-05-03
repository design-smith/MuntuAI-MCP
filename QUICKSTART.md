# Quickstart — MuntuAI MCP

Get connected and run your first tool call in under 5 minutes.

Security note: keep your agent key in an environment variable or secret manager. Do not commit it into config files, notebooks, or shared screenshots.

---

## Step 1 — Create an agent key

1. Log in to [app.muntuai.com](https://app.muntuai.com)
2. Go to **Settings → Agent Keys**
3. Click **Create Key**
4. Enter a name (e.g. `Claude Desktop`), choose **CoPilot** autonomy level
5. Copy the key shown — it starts with `mnt_` — you will not see it again

---

## Step 2 — Connect your client

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "muntu": {
      "url": "https://api.muntuai.com/api/mcp",
      "headers": {
        "Authorization": "Bearer ${env:MUNTU_AGENT_KEY}"
      }
    }
  }
}
```

Restart Claude Desktop. You should see "muntu" in the MCP tools list.

### Cursor

Open Cursor Settings → MCP, or create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "muntu": {
      "url": "https://api.muntuai.com/api/mcp",
      "headers": {
        "Authorization": "Bearer ${env:MUNTU_AGENT_KEY}"
      }
    }
  }
}
```

### Python

```bash
pip install requests
export MUNTU_AGENT_KEY="mnt_YOUR_KEY_HERE"
python clients/python/muntu_mcp_client.py list-campaigns
```

Recommended:

```bash
export MUNTU_SESSION_ID="$(uuidgen)"
```

---

## Step 3 — Verify the connection

Ask Claude or run the Python client:

```
"What campaigns do I have in MuntuAI?"
```

Or:

```bash
python clients/python/muntu_mcp_client.py list-resources
```

You should see a list of available workspace resources.

---

## Step 4 — Run a complete workflow

Once connected, try asking:

> "I want to set up a new sending domain `outreach.example.com` in MuntuAI, verify it, create a sender called `hello@outreach.example.com`, and then create a campaign targeting security professionals."

The agent will walk through:
1. `add_domain` → returns DNS records to publish
2. `trigger_domain_verification` → after you've added DNS records
3. `create_sender` → creates the mailbox
4. `create_campaign` → sets up the campaign
5. `launch_campaign` → starts enrichment → drafting → sending

See [`workflows/launch-first-campaign.md`](workflows/launch-first-campaign.md) for the full step-by-step.

---

## Common First Commands

| Goal | Tool / Resource |
|---|---|
| See all campaigns | Read `muntu://campaigns/{workspaceId}` |
| See all domains | Read `muntu://domains/{workspaceId}` |
| See all senders | Read `muntu://senders/{workspaceId}` |
| Add a domain | `add_domain` |
| Create a sender | `create_sender` |
| Create a campaign | `create_campaign` |
| Launch a campaign | `launch_campaign` |
| Check campaign progress | `get_campaign_performance` |
| Get my key info | `get_agent_key_info` |

---

## Troubleshooting

**401 Unauthorized** — Your key is wrong, expired, or revoked. Check Settings → Agent Keys.

**"Insufficient autonomy level"** — The tool requires a higher level than your key. Create a new key with `copilot` or `autonomous`.

**"Rate limit exceeded"** — Observer keys allow 60 req/min, copilot/autonomous allow 120 req/min. Wait and retry.

**Domain verification not completing** — DNS propagation takes 5–30 minutes after publishing records. Call `check_domain_status` again after waiting.
