#!/usr/bin/env python3
"""
Minimal Muntu MCP client.

Two ways to use it:

1. Simple notebook / Colab mode:
   - set the config values near the top of the file
   - run the script
   - it will list campaigns, domains, and email accounts
   - optionally add a domain, create an email, and submit/approve/launch a campaign

2. CLI mode:
   - use the explicit subcommands

Transport contract:
- POST /api/mcp
- Authorization: Bearer <agent-key>
- Accept: application/json, text/event-stream
- Content-Type: application/json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from typing import Any, Dict, Optional

import requests


BASE_URL = os.getenv("MUNTU_BASE_URL", "https://api.muntuai.com").rstrip("/")
MCP_URL = f"{BASE_URL}/api/mcp"
AGENT_KEY = os.getenv("MUNTU_AGENT_KEY", "")
SESSION_ID = os.getenv("MUNTU_SESSION_ID", str(uuid.uuid4()))
TIMEOUT = float(os.getenv("MUNTU_TIMEOUT", "20"))

# Simple run configuration for Colab / notebooks.
# Fill these in and run `run_configured_actions()`.
RUN_LIST_CAMPAIGNS = True
RUN_LIST_DOMAINS = True
RUN_LIST_EMAILS = True
RUN_ADD_DOMAIN = False
RUN_CREATE_EMAIL = False
RUN_CREATE_CAMPAIGN = False
RUN_LAUNCH_CAMPAIGN = False
RUN_MONITOR_CAMPAIGN = False
RUN_LIST_CAMPAIGN_DRAFTS = False
RUN_SAMPLE_CAMPAIGN_DRAFTS = False
RUN_SEND_CAMPAIGN_DRAFTS = False
DOMAIN_TO_ADD = "muntu.cosy"
EMAIL_DOMAIN_ID = "md_7t_Wt0MJ-ZWI"
EMAIL_LOCAL_PART = "bill"
EMAIL_DISPLAY_NAME = "Billy"
CAMPAIGN_NAME = "Zykr Security Demo Campaign"
CAMPAIGN_SAMPLE_EMAIL = (
    "Hi {{firstName}},\n\n"
    "I saw you are working in security. Teams in that seat usually spend too much time on"
    " manual triage and threat investigation.\n\n"
    "Zykr helps security teams automate repetitive investigation work so analysts can focus"
    " on higher-impact response and prevention work.\n\n"
    "Would you be open to a quick 15-minute demo next week?\n\n"
    "Regards,\nNathan"
)
CAMPAIGN_OUTREACH_GUIDE = (
    "Keep the opener grounded in enrichment data like location, weather, or sports when available. "
    "Use the recipient's professional context such as job title when it is directly relevant. "
    "From the second paragraph onward, connect the message to the company's website context and explain "
    "how Zykr reduces manual security work for analysts and lean security teams. Keep it concise and direct."
)
CAMPAIGN_MESSAGE_INTENT = "Book a demo for Zykr cybersecurity software"
CAMPAIGN_EMAIL_ACCOUNT_IDS: list[str] = []
CAMPAIGN_EMAIL_ADDRESSES: list[str] = []
CAMPAIGN_LEADS = [
    {
        "email": "grace@example.com",
        "name": "Grace",
        "companyName": "Grace Security",
        "jobTitle": "Security Analyst",
        "website": "https://example.com",
    },
    {
        "email": "bruce@example.com",
        "name": "Bruce",
        "companyName": "Bruce Tech",
        "jobTitle": "Security Operations Manager",
        "website": "https://example.org",
    },
]
CAMPAIGN_SOURCE_URL = ""
CAMPAIGN_AUTO_RESPOND = True
CAMPAIGN_AUTO_SEND_RESPONSES = False
CAMPAIGN_AUTOSEND = False
CAMPAIGN_DAILY_SEND_LIMIT: Optional[int] = 25
CAMPAIGN_FOLLOW_UP_COUNT = 2
CAMPAIGN_FOLLOW_UP_WINDOW = 5
CAMPAIGN_FOLLOW_UP_TRIGGER = "no_action"
CAMPAIGN_SCHEDULE_START = ""
CAMPAIGN_WORKFLOW_ID = ""
CAMPAIGN_MONITOR_POLLS = 8
CAMPAIGN_MONITOR_SLEEP_SECONDS = 10
CAMPAIGN_DRAFT_STATUS = "all"
CAMPAIGN_DRAFT_LIST_LIMIT = 250
CAMPAIGN_DRAFT_SAMPLE_COUNT = 5
CAMPAIGN_SEND_LEAD_IDS: list[str] = []


class McpClient:
    def __init__(
        self,
        endpoint: str,
        agent_key: str,
        timeout: float = 20,
        session_id: Optional[str] = None,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {agent_key}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
        )
        if session_id:
            self.session.headers["mcp-session-id"] = session_id
        self._next_id = 1
        self._initialized = False

    def _decode_mcp_response(self, response: requests.Response) -> Dict[str, Any]:
        content_type = response.headers.get("Content-Type", "")
        body = response.text

        if "text/event-stream" in content_type:
            events: list[str] = []
            for raw_line in body.splitlines():
                line = raw_line.strip()
                if not line.startswith("data: "):
                    continue
                payload = line[6:].strip()
                if payload:
                    events.append(payload)

            if not events:
                raise RuntimeError(f"MCP stream response did not contain any data events: {body[:500]}")

            try:
                return json.loads(events[-1])
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Could not decode MCP event payload: {events[-1][:500]}") from exc

        try:
            return response.json()
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Non-JSON response from MCP server: {body[:500]}") from exc

    def _rpc(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params or {},
        }
        self._next_id += 1

        response = self.session.post(self.endpoint, data=json.dumps(payload), timeout=timeout or self.timeout)
        response.raise_for_status()
        parsed = self._decode_mcp_response(response)

        if "error" in parsed:
            error = parsed["error"]
            raise RuntimeError(f"MCP error {error.get('code')}: {error.get('message')}")

        return parsed.get("result")

    def _notify(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        response = self.session.post(self.endpoint, data=json.dumps(payload), timeout=self.timeout)
        response.raise_for_status()

    def initialize(self) -> Any:
        result = self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "clientInfo": {"name": "muntu-mcp-client", "version": "0.1.0"},
                "capabilities": {},
            },
        )
        self._notify("notifications/initialized")
        self._initialized = True
        return result

    def ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize()

    def resources_list(self) -> Any:
        self.ensure_initialized()
        return self._rpc("resources/list")

    def resources_read(self, uri: str) -> Any:
        self.ensure_initialized()
        return self._rpc("resources/read", {"uri": uri})

    def tools_list(self) -> Any:
        self.ensure_initialized()
        return self._rpc("tools/list")

    def tools_call(self, name: str, arguments: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> Any:
        self.ensure_initialized()
        return self._rpc("tools/call", {"name": name, "arguments": arguments or {}}, timeout=timeout)


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str))


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def extract_json_content(result: Dict[str, Any]) -> Any:
    contents = result.get("contents") or result.get("content") or []
    if not contents:
        return result

    first = contents[0]
    text = first.get("text")
    if not isinstance(text, str):
        return result

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def extract_tool_result(result: Dict[str, Any]) -> Any:
    structured = result.get("structuredContent")
    if structured is not None:
        return structured
    return extract_json_content(result)


def discover_workspace_resources(client: McpClient) -> Dict[str, str]:
    result = client.resources_list()
    resources = result.get("resources", [])
    discovered: Dict[str, str] = {}

    for resource in resources:
        name = resource.get("name")
        uri = resource.get("uri")
        if isinstance(name, str) and isinstance(uri, str):
            discovered[name] = uri

    if not discovered:
        raise RuntimeError("No workspace resources were returned by resources/list")

    return discovered


def list_resource(client: McpClient, resource_name: str) -> Any:
    resources = discover_workspace_resources(client)
    uri = resources.get(resource_name)
    if not uri:
        raise RuntimeError(f"Resource '{resource_name}' not available for this key")

    result = client.resources_read(uri)
    return extract_json_content(result)


def maybe_set(target: Dict[str, Any], key: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str):
        if value.strip():
            target[key] = value.strip()
        return
    if isinstance(value, list):
        if value:
            target[key] = value
        return
    target[key] = value


def build_create_campaign_payload() -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "name": CAMPAIGN_NAME.strip(),
        "sampleEmail": CAMPAIGN_SAMPLE_EMAIL.strip(),
        "outreachGuide": CAMPAIGN_OUTREACH_GUIDE.strip(),
        "messageIntent": CAMPAIGN_MESSAGE_INTENT.strip(),
        "autoRespond": bool(CAMPAIGN_AUTO_RESPOND),
        "autoSendResponses": bool(CAMPAIGN_AUTO_SEND_RESPONSES),
        "autosend": bool(CAMPAIGN_AUTOSEND),
        "followUpCount": int(CAMPAIGN_FOLLOW_UP_COUNT),
        "followUpWindow": int(CAMPAIGN_FOLLOW_UP_WINDOW),
        "followUpTrigger": CAMPAIGN_FOLLOW_UP_TRIGGER,
    }
    maybe_set(payload, "dailySendLimit", CAMPAIGN_DAILY_SEND_LIMIT)
    maybe_set(payload, "emailAccountIds", CAMPAIGN_EMAIL_ACCOUNT_IDS)
    maybe_set(payload, "emailAddresses", CAMPAIGN_EMAIL_ADDRESSES)
    maybe_set(payload, "leads", CAMPAIGN_LEADS)
    maybe_set(payload, "sourceUrl", CAMPAIGN_SOURCE_URL)
    maybe_set(payload, "scheduleStart", CAMPAIGN_SCHEDULE_START)
    return payload


def build_launch_campaign_payload(workflow_id: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "workflowId": workflow_id.strip(),
        "autosend": bool(CAMPAIGN_AUTOSEND),
    }
    maybe_set(payload, "messageIntent", CAMPAIGN_MESSAGE_INTENT)
    maybe_set(payload, "outreachGuide", CAMPAIGN_OUTREACH_GUIDE)
    maybe_set(payload, "dailySendLimit", CAMPAIGN_DAILY_SEND_LIMIT)
    return payload


def extract_workflow_id(value: Any) -> str:
    if isinstance(value, dict):
        success = value.get("success")
        if success is False:
            return ""
        workflow_id = value.get("workflowId")
        if isinstance(workflow_id, str) and workflow_id.strip():
            return workflow_id.strip()
    raise RuntimeError(f"Could not determine workflowId from result: {value}")


def run_configured_actions() -> int:
    if not AGENT_KEY:
        print("MUNTU_AGENT_KEY is required", file=sys.stderr)
        return 1

    client = McpClient(MCP_URL, AGENT_KEY, TIMEOUT, SESSION_ID)

    if RUN_LIST_CAMPAIGNS:
        print_section("Campaigns")
        print_json(list_resource(client, "campaigns"))

    if RUN_LIST_DOMAINS:
        print_section("Domains")
        print_json(list_resource(client, "domains"))

    if RUN_LIST_EMAILS:
        print_section("Email Accounts")
        print_json(list_resource(client, "senders"))

    if RUN_ADD_DOMAIN:
        if not DOMAIN_TO_ADD.strip():
            raise RuntimeError("RUN_ADD_DOMAIN is enabled but DOMAIN_TO_ADD is empty")
        print_section(f"Add Domain: {DOMAIN_TO_ADD}")
        result = client.tools_call("add_domain", {"domainName": DOMAIN_TO_ADD.strip()})
        print_json(extract_tool_result(result))

    if RUN_CREATE_EMAIL:
        if not EMAIL_DOMAIN_ID.strip():
            raise RuntimeError("RUN_CREATE_EMAIL is enabled but EMAIL_DOMAIN_ID is empty")
        if not EMAIL_LOCAL_PART.strip():
            raise RuntimeError("RUN_CREATE_EMAIL is enabled but EMAIL_LOCAL_PART is empty")

        payload: Dict[str, Any] = {
            "managedDomainId": EMAIL_DOMAIN_ID.strip(),
            "localPart": EMAIL_LOCAL_PART.strip(),
        }
        if EMAIL_DISPLAY_NAME.strip():
            payload["displayName"] = EMAIL_DISPLAY_NAME.strip()

        print_section(f"Create Email: {EMAIL_LOCAL_PART.strip()}")
        result = client.tools_call("create_sender", payload)
        print_json(extract_tool_result(result))

    workflow_id = CAMPAIGN_WORKFLOW_ID.strip()

    if RUN_CREATE_CAMPAIGN:
        if not CAMPAIGN_NAME.strip():
            raise RuntimeError("RUN_CREATE_CAMPAIGN is enabled but CAMPAIGN_NAME is empty")
        if not CAMPAIGN_SAMPLE_EMAIL.strip():
            raise RuntimeError("RUN_CREATE_CAMPAIGN is enabled but CAMPAIGN_SAMPLE_EMAIL is empty")
        if not CAMPAIGN_OUTREACH_GUIDE.strip():
            raise RuntimeError("RUN_CREATE_CAMPAIGN is enabled but CAMPAIGN_OUTREACH_GUIDE is empty")
        if not CAMPAIGN_LEADS and not CAMPAIGN_SOURCE_URL.strip():
            raise RuntimeError("RUN_CREATE_CAMPAIGN is enabled but no leads or source URL were provided")
        if not CAMPAIGN_EMAIL_ACCOUNT_IDS and not CAMPAIGN_EMAIL_ADDRESSES:
            raise RuntimeError("RUN_CREATE_CAMPAIGN is enabled but no email accounts were configured")

        payload = build_create_campaign_payload()
        print_section("Create Campaign")
        result = client.tools_call("create_campaign", payload)
        structured = extract_tool_result(result)
        print_json(structured)
        workflow_id = extract_workflow_id(structured)
        if not workflow_id:
            print("Campaign creation was blocked. Resolve the reported issue and retry.")
            return 0

    if RUN_LAUNCH_CAMPAIGN:
        if not workflow_id:
            raise RuntimeError("RUN_LAUNCH_CAMPAIGN is enabled but CAMPAIGN_WORKFLOW_ID is empty")

        print_section("Launch Campaign")
        payload = build_launch_campaign_payload(workflow_id)
        result = client.tools_call("launch_campaign", payload)
        print_json(extract_tool_result(result))

    if RUN_MONITOR_CAMPAIGN:
        if not workflow_id:
            raise RuntimeError("RUN_MONITOR_CAMPAIGN is enabled but no workflowId is available")

        for poll in range(1, CAMPAIGN_MONITOR_POLLS + 1):
            print_section(f"Campaign Performance Poll {poll}")
            result = client.tools_call("get_campaign_performance", {"workflowId": workflow_id})
            print_json(extract_tool_result(result))
            if poll < CAMPAIGN_MONITOR_POLLS:
                time.sleep(CAMPAIGN_MONITOR_SLEEP_SECONDS)

    if RUN_LIST_CAMPAIGN_DRAFTS:
        if not workflow_id:
            raise RuntimeError("RUN_LIST_CAMPAIGN_DRAFTS is enabled but no workflowId is available")

        print_section("List Campaign Drafts")
        result = client.tools_call(
            "list_campaign_drafts",
            {
                "workflowId": workflow_id,
                "status": CAMPAIGN_DRAFT_STATUS,
                "limit": int(CAMPAIGN_DRAFT_LIST_LIMIT),
                "offset": 0,
            },
        )
        print_json(extract_tool_result(result))

    if RUN_SAMPLE_CAMPAIGN_DRAFTS:
        if not workflow_id:
            raise RuntimeError("RUN_SAMPLE_CAMPAIGN_DRAFTS is enabled but no workflowId is available")

        print_section("Sample Campaign Drafts")
        result = client.tools_call(
            "sample_campaign_drafts",
            {
                "workflowId": workflow_id,
                "status": CAMPAIGN_DRAFT_STATUS,
                "count": int(CAMPAIGN_DRAFT_SAMPLE_COUNT),
            },
        )
        print_json(extract_tool_result(result))

    if RUN_SEND_CAMPAIGN_DRAFTS:
        if not workflow_id:
            raise RuntimeError("RUN_SEND_CAMPAIGN_DRAFTS is enabled but no workflowId is available")

        payload: Dict[str, Any] = {"workflowId": workflow_id}
        if CAMPAIGN_SEND_LEAD_IDS:
            payload["leadIds"] = CAMPAIGN_SEND_LEAD_IDS

        print_section("Send Campaign Drafts")
        result = client.tools_call("send_campaign_drafts", payload)
        print_json(extract_tool_result(result))

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal Muntu MCP client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-campaigns")
    subparsers.add_parser("list-domains")
    subparsers.add_parser("list-emails")
    subparsers.add_parser("list-tools")
    subparsers.add_parser("list-resources")

    add_domain_parser = subparsers.add_parser("add-domain")
    add_domain_parser.add_argument("--domain", required=True, help="Domain to add, e.g. outreach.example.com")

    create_email_parser = subparsers.add_parser("create-email")
    create_email_parser.add_argument("--domain-id", required=True, help="Managed domain ID")
    create_email_parser.add_argument("--local-part", required=True, help="Local part before @")
    create_email_parser.add_argument("--display-name", help="Optional sender display name")

    create_campaign_parser = subparsers.add_parser("create-campaign")
    create_campaign_parser.add_argument("--name", required=True, help="Campaign name")
    create_campaign_parser.add_argument("--sample-email", required=True, help="Sample email body")
    create_campaign_parser.add_argument("--outreach-guide", required=True, help="Campaign guide")
    create_campaign_parser.add_argument("--message-intent", required=True, help="Campaign goal")
    create_campaign_parser.add_argument("--email-account-ids-json", help='Optional JSON array of sender IDs')
    create_campaign_parser.add_argument("--email-addresses-json", help='Optional JSON array of sender email addresses')
    create_campaign_parser.add_argument("--leads-json", help='JSON array of leads')
    create_campaign_parser.add_argument("--source-url", help="Public CSV URL if importing from a file")
    create_campaign_parser.add_argument("--auto-respond", choices=["true", "false"], default="true")
    create_campaign_parser.add_argument("--auto-send-responses", choices=["true", "false"], default="false")
    create_campaign_parser.add_argument("--autosend", choices=["true", "false"], default="false")
    create_campaign_parser.add_argument("--daily-send-limit", type=int, default=25)
    create_campaign_parser.add_argument("--follow-up-count", type=int, default=2)
    create_campaign_parser.add_argument("--follow-up-window", type=int, default=5)
    create_campaign_parser.add_argument("--follow-up-trigger", default="no_action")
    create_campaign_parser.add_argument("--schedule-start", help="Optional ISO schedule start")

    launch_campaign_parser = subparsers.add_parser("launch-campaign")
    launch_campaign_parser.add_argument("--workflow-id", required=True, help="Workflow ID to launch")
    launch_campaign_parser.add_argument("--message-intent", help="Optional message intent")
    launch_campaign_parser.add_argument("--outreach-guide", help="Optional outreach guide")
    launch_campaign_parser.add_argument("--daily-send-limit", type=int, help="Optional daily send limit")
    launch_campaign_parser.add_argument("--autosend", choices=["true", "false"], help="Optional autosend flag")

    monitor_campaign_parser = subparsers.add_parser("monitor-campaign")
    monitor_campaign_parser.add_argument("--workflow-id", required=True, help="Workflow ID to monitor")
    monitor_campaign_parser.add_argument("--polls", type=int, default=8, help="How many times to poll performance")
    monitor_campaign_parser.add_argument("--sleep-seconds", type=int, default=10, help="Seconds between polls")

    list_drafts_parser = subparsers.add_parser("list-campaign-drafts")
    list_drafts_parser.add_argument("--workflow-id", required=True, help="Workflow ID")
    list_drafts_parser.add_argument("--status", choices=["drafted", "pending_review", "all"], default="all")
    list_drafts_parser.add_argument("--limit", type=int, default=250)
    list_drafts_parser.add_argument("--offset", type=int, default=0)

    sample_drafts_parser = subparsers.add_parser("sample-campaign-drafts")
    sample_drafts_parser.add_argument("--workflow-id", required=True, help="Workflow ID")
    sample_drafts_parser.add_argument("--status", choices=["drafted", "pending_review", "all"], default="all")
    sample_drafts_parser.add_argument("--count", type=int, default=5)

    send_drafts_parser = subparsers.add_parser("send-campaign-drafts")
    send_drafts_parser.add_argument("--workflow-id", required=True, help="Workflow ID")
    send_drafts_parser.add_argument("--lead-ids-json", help='Optional JSON array of lead IDs to send')

    return parser


def default_argv(explicit_argv: Optional[list[str]] = None) -> list[str]:
    args = explicit_argv if explicit_argv is not None else sys.argv[1:]

    # Notebook runtimes inject their own kernel args. If the first argument is not
    # one of our commands, ignore ambient argv and require explicit command input.
    valid_commands = {
        "list-campaigns",
        "list-domains",
        "list-emails",
        "list-tools",
        "list-resources",
        "add-domain",
        "create-email",
        "create-campaign",
        "launch-campaign",
        "monitor-campaign",
        "list-campaign-drafts",
        "sample-campaign-drafts",
        "send-campaign-drafts",
    }

    if not args:
        return []

    if args[0] in valid_commands:
        return args

    return []


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    argv = default_argv(argv)

    if not argv:
        return run_configured_actions()

    args = parser.parse_args(argv)

    if not AGENT_KEY:
        print("MUNTU_AGENT_KEY is required", file=sys.stderr)
        return 1

    client = McpClient(MCP_URL, AGENT_KEY, TIMEOUT, SESSION_ID)

    if args.command == "list-campaigns":
        print_json(list_resource(client, "campaigns"))
        return 0

    if args.command == "list-domains":
        print_json(list_resource(client, "domains"))
        return 0

    if args.command == "list-emails":
        print_json(list_resource(client, "senders"))
        return 0

    if args.command == "list-tools":
        print_json(client.tools_list())
        return 0

    if args.command == "list-resources":
        print_json(client.resources_list())
        return 0

    if args.command == "add-domain":
        result = client.tools_call("add_domain", {"domainName": args.domain})
        print_json(extract_tool_result(result))
        return 0

    if args.command == "create-email":
        payload: Dict[str, Any] = {
            "managedDomainId": args.domain_id,
            "localPart": args.local_part,
        }
        if args.display_name:
            payload["displayName"] = args.display_name
        result = client.tools_call("create_sender", payload)
        print_json(extract_tool_result(result))
        return 0

    if args.command == "create-campaign":
        payload: Dict[str, Any] = {
            "name": args.name,
            "sampleEmail": args.sample_email,
            "outreachGuide": args.outreach_guide,
            "messageIntent": args.message_intent,
            "autoRespond": args.auto_respond == "true",
            "autoSendResponses": args.auto_send_responses == "true",
            "autosend": args.autosend == "true",
            "dailySendLimit": args.daily_send_limit,
            "followUpCount": args.follow_up_count,
            "followUpWindow": args.follow_up_window,
            "followUpTrigger": args.follow_up_trigger,
        }
        if args.email_account_ids_json:
            payload["emailAccountIds"] = json.loads(args.email_account_ids_json)
        if args.email_addresses_json:
            payload["emailAddresses"] = json.loads(args.email_addresses_json)
        if args.leads_json:
            payload["leads"] = json.loads(args.leads_json)
        if args.source_url:
            payload["sourceUrl"] = args.source_url
        if args.schedule_start:
            payload["scheduleStart"] = args.schedule_start
        result = client.tools_call("create_campaign", payload)
        print_json(extract_tool_result(result))
        return 0

    if args.command == "launch-campaign":
        payload: Dict[str, Any] = {
            "workflowId": args.workflow_id,
        }
        if args.message_intent:
            payload["messageIntent"] = args.message_intent
        if args.outreach_guide:
            payload["outreachGuide"] = args.outreach_guide
        if args.daily_send_limit is not None:
            payload["dailySendLimit"] = args.daily_send_limit
        if args.autosend is not None:
            payload["autosend"] = args.autosend == "true"
        result = client.tools_call("launch_campaign", payload)
        print_json(extract_tool_result(result))
        return 0

    if args.command == "monitor-campaign":
        for poll in range(1, args.polls + 1):
            print_section(f"Campaign Performance Poll {poll}")
            result = client.tools_call("get_campaign_performance", {"workflowId": args.workflow_id})
            print_json(extract_tool_result(result))
            if poll < args.polls:
                time.sleep(args.sleep_seconds)
        return 0

    if args.command == "list-campaign-drafts":
        result = client.tools_call(
            "list_campaign_drafts",
            {
                "workflowId": args.workflow_id,
                "status": args.status,
                "limit": args.limit,
                "offset": args.offset,
            },
        )
        print_json(extract_tool_result(result))
        return 0

    if args.command == "sample-campaign-drafts":
        result = client.tools_call(
            "sample_campaign_drafts",
            {
                "workflowId": args.workflow_id,
                "status": args.status,
                "count": args.count,
            },
        )
        print_json(extract_tool_result(result))
        return 0

    if args.command == "send-campaign-drafts":
        payload: Dict[str, Any] = {"workflowId": args.workflow_id}
        if args.lead_ids_json:
            payload["leadIds"] = json.loads(args.lead_ids_json)
        result = client.tools_call("send_campaign_drafts", payload)
        print_json(extract_tool_result(result))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        raise SystemExit(exit_code)
