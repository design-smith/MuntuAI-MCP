# Resource Schemas Reference

Full response schemas for all 6 MuntuAI MCP resources.

---

## workspace

**URI:** `muntu://workspace/{workspaceId}`

```typescript
{
  workspace: {
    id: string;          // "ws_abc123"
    name: string;        // "Acme Corp"
    createdAt: string;   // ISO 8601
  };
  policy: {
    approvalMode: "always_require" | "never_require" | "policy_based";
    autonomyCeiling: "observer" | "copilot" | "autonomous";
    maxDailySendLimit: number;
    riskThresholdLeadCount: number;
  };
  counts: {
    domains: number;
    emailAccounts: number;
    workspaceMembers: number;
  };
}
```

**Example:**
```json
{
  "workspace": {
    "id": "ws_abc123",
    "name": "Acme Corp",
    "createdAt": "2025-01-15T10:00:00Z"
  },
  "policy": {
    "approvalMode": "never_require",
    "autonomyCeiling": "autonomous",
    "maxDailySendLimit": 500,
    "riskThresholdLeadCount": 100
  },
  "counts": {
    "domains": 3,
    "emailAccounts": 7,
    "workspaceMembers": 2
  }
}
```

---

## domains

**URI:** `muntu://domains/{workspaceId}?cursor=0&limit=50`

**Pagination:** default limit 50, max 200

```typescript
{
  workspaceId: string;
  total: number;
  cursor: number;
  nextCursor: string | null;
  domains: Array<{
    domainName: string;
    status: "verified" | "pending" | "failed" | "expired";
    verified: boolean;
    sources: Array<"muntu_managed" | "outreach" | "connected_account">;
    managedDomain?: {
      id: string;           // "md_xyz"
      status: string;
    };
    verification: {
      aggregateStatus: string;
      campaignAssignmentAllowed: boolean;
      tracks: Array<{
        trackKey: string;
        status: string;
        errors: string[];
        dnsRequirements: Array<{
          type: string;     // "TXT" | "CNAME" | "MX"
          hostname: string;
          value: string;
          status: string;   // "detected" | "pending"
          verified: boolean;
        }>;
      }>;
    };
    dnsRequirements: Array<{
      type: string;
      hostname: string;
      value: string;
      purpose: string;
      status: string;
      verified: boolean;
    }>;
    dnsPlanSummary: {
      pendingCount: number;
      verifiedCount: number;
    };
    nextAction:
      | "none"
      | "publish_dns_records_then_trigger_verification"
      | "trigger_verification"
      | "review_provider_errors"
      | "resolve_track_failures"
      | "inspect_domain_status";
  }>;
}
```

---

## senders

**URI:** `muntu://senders/{workspaceId}?cursor=0&limit=50`

**Pagination:** default limit 50, max 200

```typescript
{
  workspaceId: string;
  total: number;
  cursor: number;
  nextCursor: string | null;
  emailAccounts: Array<{
    id: string;                // "sa_xyz"
    email: string;             // "hello@outreach.example.com"
    displayName: string | null;
    source: "muntu_created" | "imported";
    imported: boolean;
    status: "active" | "provisioning" | "paused" | "suspended" | "disabled";
    connectionStatus: "connected" | "disconnected" | "unknown";
    domainName: string;
  }>;
}
```

---

## campaigns

**URI:** `muntu://campaigns/{workspaceId}?cursor=0&limit=20`

**Pagination:** default limit 20, max 100

```typescript
{
  workspaceId: string;
  total: number;
  cursor: number;
  nextCursor: string | null;
  campaigns: Array<{
    id: string;         // "wf_abc" (workflows) or "cp_abc" (plans)
    name: string;
    status:
      | "draft"
      | "active"
      | "paused"
      | "completed"
      | "failed"
      | "pending_review"
      | "approved"
      | "rejected";
    source: "workflow" | "plan";
    createdAt: string;
  }>;
}
```

---

## campaign-plans

**URI:** `muntu://campaign-plans/{workspaceId}?cursor=0&limit=20`

**Pagination:** default limit 20, max 100

The draft review queue — campaign plans submitted for approval.

```typescript
{
  workspaceId: string;
  total: number;
  cursor: number;
  nextCursor: string | null;
  plans: Array<{
    id: string;           // "cp_xyz"
    workflowId: string | null;
    approvalState: "pending_review" | "approved" | "rejected";
    strategy: string;
    emailSequence: Array<{
      sequenceIndex: number;
      subject: string;
      body: string;
    }>;
    createdAt: string;
  }>;
}
```

---

## events

**URI:** `muntu://events/{workspaceId}?cursor=0`

**Pagination:** 50 per page, cursor-based

**Filter params:** `eventType`, `resourceType`, `actorType`

```typescript
{
  workspaceId: string;
  total: number;
  cursor: number;
  nextCursor: string | null;
  events: Array<{
    id: string;           // "ev_abc"
    eventType: string;    // e.g. "campaign.launched"
    workspaceId: string;
    actorType: "system" | "user" | "agent";
    actorId: string | null;
    agentKeyId: string | null;  // set when actorType === "agent"
    resourceType: string;
    resourceId: string | null;
    payload: Record<string, unknown>;
    createdAt: string;
  }>;
}
```

---

## Pagination

All paginated resources return the same cursor fields:

```typescript
{
  total: number;           // total record count across all pages
  cursor: number;          // offset used for this page
  nextCursor: string | null;  // offset for next page, or null if last page
}
```

To paginate:
```
muntu://domains/{id}?cursor=0&limit=50    // page 1
muntu://domains/{id}?cursor=50&limit=50   // page 2
muntu://domains/{id}?cursor=100&limit=50  // page 3
```

Continue until `nextCursor` is `null`.
