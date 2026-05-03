#!/usr/bin/env python3
"""
Create and launch a campaign end-to-end.

Requires a ready sender and verified domain already set up.

Usage:
    export MUNTU_AGENT_KEY="mnt_yourkey"
    python launch_campaign.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from muntu_mcp_client import McpClient, extract_tool_result

BASE_URL = os.getenv("MUNTU_BASE_URL", "https://api.muntuai.com").rstrip("/")
AGENT_KEY = os.getenv("MUNTU_AGENT_KEY", "")

# ─── Campaign configuration ──────────────────────────────────────────────────
CAMPAIGN_NAME = "Q2 Security Outreach"

SAMPLE_EMAIL = """\
Hi {{firstName}},

I noticed you're leading security at {{companyName}}. Teams in that role often \
tell us they spend too much time on manual threat triage.

Zykr automates that investigation work so analysts can focus on response and \
prevention — without adding headcount.

Would you be open to a quick 15-minute demo next week?

Best,
Nathan\
"""

OUTREACH_GUIDE = (
    "Open with a specific observation about the company's security posture or recent "
    "growth. In the second paragraph, connect to how Zykr reduces analyst time on "
    "manual triage. Keep it under 100 words. Do not use the word 'innovative'."
)

MESSAGE_INTENT = "Book a 15-minute Zykr cybersecurity demo"

# Fill in your sender IDs (sa_...) — get them from list_ready_senders
EMAIL_ACCOUNT_IDS = ["sa_REPLACE_ME"]

# Leads — or use sourceUrl for a CSV
LEADS = [
    {
        "email": "cto@example.com",
        "name": "Alex Chen",
        "companyName": "Acme Corp",
        "jobTitle": "CTO",
        "website": "https://acmecorp.com",
    },
    {
        "email": "security@example.org",
        "name": "Jamie Rivera",
        "companyName": "TechCo",
        "jobTitle": "Head of Security",
        "website": "https://techco.example.org",
    },
]

AUTOSEND = False           # False = stop after draft generation for review
DAILY_SEND_LIMIT = 25
FOLLOW_UP_COUNT = 2
FOLLOW_UP_WINDOW = 5       # days
FOLLOW_UP_TRIGGER = "no_action"
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    if not AGENT_KEY:
        print("MUNTU_AGENT_KEY is required", file=sys.stderr)
        return 1

    if "REPLACE_ME" in EMAIL_ACCOUNT_IDS[0]:
        print("Set EMAIL_ACCOUNT_IDS to your real sender IDs before running.", file=sys.stderr)
        return 1

    client = McpClient(f"{BASE_URL}/api/mcp", AGENT_KEY)

    # ── Step 1: Create campaign ───────────────────────────────────────────────
    print("Creating campaign...")
    result = client.tools_call(
        "create_campaign",
        {
            "name": CAMPAIGN_NAME,
            "sampleEmail": SAMPLE_EMAIL,
            "outreachGuide": OUTREACH_GUIDE,
            "messageIntent": MESSAGE_INTENT,
            "emailAccountIds": EMAIL_ACCOUNT_IDS,
            "leads": LEADS,
            "autosend": AUTOSEND,
            "dailySendLimit": DAILY_SEND_LIMIT,
            "followUpCount": FOLLOW_UP_COUNT,
            "followUpWindow": FOLLOW_UP_WINDOW,
            "followUpTrigger": FOLLOW_UP_TRIGGER,
        },
    )

    data = extract_tool_result(result)
    print(json.dumps(data, indent=2, default=str))

    if not data.get("success"):
        print("\nCampaign creation blocked.")
        reasons = data.get("reasons", [])
        for r in reasons:
            print(f"  - {r}")
        return 1

    workflow_id = data["workflowId"]
    print(f"\nCampaign created: {workflow_id}")

    # ── Step 2: Launch campaign ───────────────────────────────────────────────
    print("\nLaunching campaign...")
    result = client.tools_call(
        "launch_campaign",
        {
            "workflowId": workflow_id,
            "autosend": AUTOSEND,
        },
    )

    launch_data = extract_tool_result(result)
    print(json.dumps(launch_data, indent=2, default=str))

    if not launch_data.get("success"):
        print("Launch failed.")
        return 1

    print(f"\nCampaign launched: {workflow_id}")
    print("Monitor with: python monitor_campaign.py")
    print(f"Workflow ID:   {workflow_id}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
