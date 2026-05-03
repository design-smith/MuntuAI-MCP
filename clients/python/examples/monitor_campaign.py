#!/usr/bin/env python3
"""
Poll campaign performance until complete, then sample drafts.

Usage:
    export MUNTU_AGENT_KEY="mnt_yourkey"
    python monitor_campaign.py --workflow-id wf_abc123
    python monitor_campaign.py --workflow-id wf_abc123 --send  # auto-send when ready
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from muntu_mcp_client import McpClient, extract_tool_result

BASE_URL = os.getenv("MUNTU_BASE_URL", "https://api.muntuai.com").rstrip("/")
AGENT_KEY = os.getenv("MUNTU_AGENT_KEY", "")

POLL_INTERVAL = 30   # seconds between polls
MAX_POLLS = 60       # stop after this many polls (~30 minutes)
SAMPLE_COUNT = 5     # drafts to sample when ready


def format_counts(counts: dict) -> str:
    parts = []
    for key in ["total", "enriched", "drafted", "sent", "opened", "replied", "bounced"]:
        val = counts.get(key, 0)
        parts.append(f"{key}={val}")
    return "  ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow-id", required=True, help="Workflow ID to monitor")
    parser.add_argument("--send", action="store_true", help="Auto-send all drafts when ready")
    parser.add_argument("--polls", type=int, default=MAX_POLLS)
    parser.add_argument("--interval", type=int, default=POLL_INTERVAL)
    args = parser.parse_args()

    if not AGENT_KEY:
        print("MUNTU_AGENT_KEY is required", file=sys.stderr)
        return 1

    client = McpClient(f"{BASE_URL}/api/mcp", AGENT_KEY)
    workflow_id = args.workflow_id
    drafts_sampled = False

    print(f"Monitoring campaign {workflow_id}")
    print(f"Polling every {args.interval}s (max {args.polls} polls)\n")

    for poll in range(1, args.polls + 1):
        result = client.tools_call("get_campaign_performance", {"workflowId": workflow_id})
        data = extract_tool_result(result)

        status = data.get("status", "unknown")
        stage = data.get("stage", "unknown")
        counts = data.get("leadCounts", {})
        metrics = data.get("metrics", {})

        print(f"[Poll {poll:3d}]  status={status}  stage={stage}")
        print(f"         {format_counts(counts)}")

        if metrics:
            open_rate = metrics.get("openRate", 0)
            reply_rate = metrics.get("replyRate", 0)
            print(f"         open_rate={open_rate:.1%}  reply_rate={reply_rate:.1%}")

        print()

        # Sample drafts once they appear
        if not drafts_sampled and counts.get("drafted", 0) > 0:
            drafts_sampled = True
            print(f"Drafts ready! Sampling {SAMPLE_COUNT}...\n")
            sample_result = client.tools_call(
                "sample_campaign_drafts",
                {"workflowId": workflow_id, "count": SAMPLE_COUNT},
            )
            sample_data = extract_tool_result(sample_result)
            for draft in sample_data.get("drafts", []):
                print(f"  To: {draft.get('email')}")
                print(f"  Subject: {draft.get('subject')}")
                body = draft.get("body", "")
                print(f"  Body: {body[:200]}{'...' if len(body) > 200 else ''}")
                print()

            if args.send:
                print("--send flag set. Sending all drafts...\n")
                send_result = client.tools_call("send_campaign_drafts", {"workflowId": workflow_id})
                send_data = extract_tool_result(send_result)
                print(json.dumps(send_data, indent=2, default=str))

        # Stop if campaign is done
        if status in ("completed", "failed"):
            print(f"Campaign {status}. Final metrics:")
            print(json.dumps(metrics, indent=2, default=str))
            return 0

        if poll < args.polls:
            time.sleep(args.interval)

    print(f"Reached max polls ({args.polls}). Campaign still running.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
