#!/usr/bin/env python3
"""
List all campaigns in the workspace and print their status.

Usage:
    export MUNTU_AGENT_KEY="mnt_yourkey"
    python list_campaigns.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from muntu_mcp_client import McpClient, discover_workspace_resources, extract_json_content

BASE_URL = os.getenv("MUNTU_BASE_URL", "https://api.muntuai.com").rstrip("/")
AGENT_KEY = os.getenv("MUNTU_AGENT_KEY", "")


def main() -> int:
    if not AGENT_KEY:
        print("MUNTU_AGENT_KEY is required", file=sys.stderr)
        return 1

    client = McpClient(f"{BASE_URL}/api/mcp", AGENT_KEY)

    # Discover resource URIs for this workspace
    resources = discover_workspace_resources(client)

    campaigns_uri = resources.get("campaigns")
    if not campaigns_uri:
        print("No campaigns resource available for this key", file=sys.stderr)
        return 1

    # Read campaigns (first page)
    result = client.resources_read(campaigns_uri)
    data = extract_json_content(result)

    campaigns = data.get("campaigns", [])
    total = data.get("total", 0)

    print(f"Campaigns ({total} total):\n")

    if not campaigns:
        print("  No campaigns found.")
        return 0

    for c in campaigns:
        status = c.get("status", "unknown")
        source = c.get("source", "")
        created = c.get("createdAt", "")[:10]
        print(f"  [{status:15}]  {c['name']:<40}  {c['id']}  ({source}, {created})")

    next_cursor = data.get("nextCursor")
    if next_cursor:
        print(f"\n  ... and more. Use ?cursor={next_cursor} for next page.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
