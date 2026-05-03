# MuntuAI MCP

This repository contains the public documentation, manifest, and reference clients for the live MuntuAI MCP server. The runnable server implementation lives in the main Muntu backend.

The official Model Context Protocol (MCP) server for [MuntuAI](https://muntuai.com) — giving AI agents programmatic access to email outreach campaigns, lead management, domain infrastructure, and real-time workspace events.

---

## What This Is

MuntuAI is an AI-native email outreach platform. This MCP server lets external agents (Claude, Cursor, custom scripts) connect to a MuntuAI workspace and perform actions: create campaigns, import leads, verify domains, send emails, and subscribe to webhook events — all through a standard MCP interface over HTTP.

**Protocol:** [Model Context Protocol](https://modelcontextprotocol.io) over HTTP (JSON-RPC 2.0)  
**Transport:** Streamable HTTP (`text/event-stream` or `application/json`)  
**Server protocol revision:** `2025-03-26`  
**Server URL:** `https://api.muntuai.com/api/mcp`

---

## Quick Start

### 1. Get an agent key

Log in to [app.muntuai.com](https://app.muntuai.com), go to **Settings → Agent Keys**, and create a key. Choose the autonomy level that matches what your agent needs:

| Level | What it can do |
|---|---|
| `observer` | Read anything — campaigns, leads, domains, senders, events |
| `copilot` | Read + create and modify — campaigns, domains, senders, leads, webhooks |
| `autonomous` | Everything above + pause, resume, delete |

You will see the raw key once: `mnt_<keyId>.<secret>`. Copy it immediately.

### 2. Configure your client

Security note: store the raw agent key in an environment variable or secret manager. Do not commit it to source control or paste it into shared files.

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
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

**Cursor** (`.cursor/mcp.json` or Settings → MCP):
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

**Python:**
```bash
pip install requests
export MUNTU_AGENT_KEY="mnt_YOUR_KEY_HERE"
python clients/python/muntu_mcp_client.py list-campaigns
```

Recommended:

```bash
export MUNTU_SESSION_ID="$(uuidgen)"
```

Muntu uses the optional `MUNTU_SESSION_ID` to group requests into one logical MCP session for session-scoped safety controls and budgeting.

### 3. Make your first call

Once connected, ask your agent:

> "List all campaigns in my MuntuAI workspace"

The agent will call `resources/read` on `muntu://campaigns/{workspaceId}` and return the campaign list.

Or via Python CLI:
```bash
python clients/python/muntu_mcp_client.py list-campaigns
python clients/python/muntu_mcp_client.py list-domains
python clients/python/muntu_mcp_client.py list-emails
```

---

## What Agents Can Do

### Resources (read-only views)
| Resource | URI | Description |
|---|---|---|
| workspace | `muntu://workspace/{id}` | Profile, policy, infrastructure counts |
| domains | `muntu://domains/{id}?cursor=0&limit=50` | All domains with DNS and verification state |
| senders | `muntu://senders/{id}?cursor=0&limit=50` | All email accounts with status |
| campaigns | `muntu://campaigns/{id}?cursor=0&limit=20` | Unified campaign list |
| campaign-plans | `muntu://campaign-plans/{id}?cursor=0&limit=20` | Draft review queue |
| events | `muntu://events/{id}?cursor=0` | Recent system events (filterable) |

### Tools (30 total)
Grouped by domain — see [`tools/README.md`](tools/README.md) for the full index.

- **Campaigns** — create, launch, pause, resume, monitor, review drafts, send
- **Leads** — import from array or CSV URL, enrich, sample
- **Senders** — create, delete, health check, assign to campaign
- **Domains** — add, verify, check status
- **Email generation** — preview, refine, generate campaign guide
- **Webhooks** — subscribe to workspace events
- **Meta** — get agent key info

---

## Repository Structure

```
muntuai-mcp/
├── README.md                    # This file
├── QUICKSTART.md                # 5-minute setup guide
├── docs/
│   ├── authentication.md        # Token format, headers, rate limits
│   ├── autonomy-levels.md       # Permission model
│   ├── resources.md             # All 6 resources with schemas
│   ├── events.md                # All event types and payloads
│   ├── webhooks.md              # Register, sign, verify
│   └── errors.md                # Error codes and handling
├── tools/
│   ├── README.md                # Full tool index
│   ├── campaigns.md
│   ├── leads.md
│   ├── senders.md
│   ├── domains.md
│   ├── email-generation.md
│   └── meta.md
├── workflows/
│   ├── README.md                # What workflows are
│   ├── launch-first-campaign.md
│   ├── review-and-send-drafts.md
│   ├── domain-setup.md
│   └── monitor-campaign.md
├── reference/
│   ├── event-types.md
│   ├── resource-schemas.md
│   └── tool-schemas.md
├── clients/
│   └── python/
│       ├── muntu_mcp_client.py  # Reference Python client
│       ├── README.md
│       └── examples/
├── agent-guides/
│   ├── for-claude.md
│   ├── for-cursor.md
│   └── decision-guide.md
└── .well-known/
    └── mcp-manifest.json        # Machine-readable capabilities manifest
```

---

## Key Concepts

**Workspace** — All data in MuntuAI is scoped to a workspace. Your agent key is bound to one workspace and can only access data within it.

**Autonomy levels** — Every tool has a minimum required level. If your key's level is below the requirement, the call is rejected and the attempt is logged. See [`docs/autonomy-levels.md`](docs/autonomy-levels.md).

**Campaign lifecycle** — `uploaded → enriching → drafting → sending → completed`. Agents can observe this lifecycle through `get_campaign_performance` and the events resource. See [`workflows/monitor-campaign.md`](workflows/monitor-campaign.md).

**Domain verification** — Before sending, a domain must be verified with the email provider. This involves publishing DNS records and triggering verification. See [`workflows/domain-setup.md`](workflows/domain-setup.md).

---

## Support

- **Documentation issues:** Open an issue in this repo
- **Platform support:** [support@muntuai.com](mailto:support@muntuai.com)
- **Website:** [muntuai.com](https://muntuai.com)
