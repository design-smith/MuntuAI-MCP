# Python MCP Client

A minimal Python client for the MuntuAI MCP API. Works in scripts, notebooks (Jupyter, Colab), and CLI mode.

**Requirements:** Python 3.9+, `requests`
Security note: use `MUNTU_AGENT_KEY` from the environment. Do not hardcode a live key in the file or in a notebook you plan to save or share.

---

## Installation

```bash
pip install requests
```

No other dependencies.

---

## Quick Start

```python
import os
from muntu_mcp_client import McpClient, extract_tool_result, discover_workspace_resources

client = McpClient(
    endpoint="https://api.muntuai.com/api/mcp",
    agent_key=os.environ["MUNTU_AGENT_KEY"],
)

# List campaigns
resources = discover_workspace_resources(client)
import json
result = client.resources_read(resources["campaigns"])
campaigns = json.loads(result["contents"][0]["text"])
print(campaigns)

# Call a tool
result = client.tools_call("get_agent_key_info")
key_info = extract_tool_result(result)
print(key_info)
```

---

## Environment Variables

Optional: set `MUNTU_SESSION_ID` to one stable value for the lifetime of a single logical MCP session. If omitted, the reference client now auto-generates one.

| Variable | Default | Description |
|---|---|---|
| `MUNTU_AGENT_KEY` | — | Required. Your `mnt_...` agent key. |
| `MUNTU_BASE_URL` | `https://api.muntuai.com` | API base URL |
| `MUNTU_TIMEOUT` | `20` | Default request timeout in seconds |

---

## McpClient API

### `McpClient(endpoint, agent_key, timeout=20)`

```python
client = McpClient(
    endpoint="https://api.muntuai.com/api/mcp",
    agent_key="mnt_yourkey",
    timeout=20,
)
```

### `client.initialize() → dict`

Send MCP `initialize` handshake. Called automatically on first request.

### `client.resources_list() → dict`

List all available workspace resources with their URIs.

### `client.resources_read(uri) → dict`

Read a resource by URI.

```python
result = client.resources_read("muntu://campaigns/ws_abc123")
```

### `client.tools_list() → dict`

List all available tools.

### `client.tools_call(name, arguments=None, timeout=None) → dict`

Call a tool. `timeout` overrides the instance default for this call.

```python
result = client.tools_call(
    "get_campaign_performance",
    {"workflowId": "wf_abc123"},
    timeout=60,
)
```

---

## Helper Functions

### `extract_tool_result(result) → Any`

Extract the structured result from a tool call response. Prefers `structuredContent`, falls back to parsing `content[0].text` as JSON.

### `extract_json_content(result) → Any`

Extract JSON from a resource read response.

### `discover_workspace_resources(client) → dict[str, str]`

Call `resources/list` and return a mapping of resource name → URI.

```python
resources = discover_workspace_resources(client)
# {
#   "workspace": "muntu://workspace/ws_abc",
#   "campaigns": "muntu://campaigns/ws_abc",
#   "domains": "muntu://domains/ws_abc",
#   ...
# }
```

### `list_resource(client, resource_name) → Any`

Convenience wrapper: discover resources, read by name, return parsed JSON.

```python
campaigns = list_resource(client, "campaigns")
```

---

## CLI Mode

```bash
export MUNTU_AGENT_KEY="mnt_yourkey"

# List campaigns, domains, email accounts
python muntu_mcp_client.py list-campaigns
python muntu_mcp_client.py list-domains
python muntu_mcp_client.py list-emails

# Add a domain
python muntu_mcp_client.py add-domain --domain outreach.example.com

# Create a sender
python muntu_mcp_client.py create-email --domain-id md_abc --local-part outreach --display-name "Team"

# Create and launch a campaign
python muntu_mcp_client.py create-campaign \
  --name "Q2 Outreach" \
  --sample-email "Hi {{firstName}}, ..." \
  --outreach-guide "Focus on pain points." \
  --message-intent "Book a demo" \
  --email-account-ids-json '["sa_abc"]' \
  --leads-json '[{"email":"test@example.com","name":"Test"}]'

python muntu_mcp_client.py launch-campaign --workflow-id wf_abc123

# Monitor
python muntu_mcp_client.py monitor-campaign --workflow-id wf_abc123 --polls 10 --sleep-seconds 30

# Review drafts
python muntu_mcp_client.py sample-campaign-drafts --workflow-id wf_abc123 --count 5
python muntu_mcp_client.py send-campaign-drafts --workflow-id wf_abc123
```

---

## Notebook / Colab Mode

Edit the config block at the top of `muntu_mcp_client.py`:

```python
AGENT_KEY = "mnt_yourkey"  # or use os.getenv("MUNTU_AGENT_KEY")
RUN_LIST_CAMPAIGNS = True
RUN_LIST_DOMAINS = True
RUN_CREATE_CAMPAIGN = True
CAMPAIGN_NAME = "My Campaign"
CAMPAIGN_SAMPLE_EMAIL = "Hi {{firstName}}, ..."
# ...
```

Then run the script. It executes whichever `RUN_*` flags are enabled.

---

## Examples

See [examples/](examples/) for:
- [list_campaigns.py](examples/list_campaigns.py) — list and print campaigns
- [launch_campaign.py](examples/launch_campaign.py) — create and launch end-to-end
- [monitor_campaign.py](examples/monitor_campaign.py) — poll performance until complete
