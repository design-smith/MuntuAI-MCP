# Tool Schemas Reference

Input and output schemas for all 30 MuntuAI MCP tools. For usage guidance, see the [tools/ directory](../tools/).

---

## Notation

- `?` suffix = optional field
- `string[]` = array of strings
- `Lead` = lead object (see below)

**Lead object:**
```typescript
{
  email: string;           // required
  name?: string;
  companyName?: string;
  jobTitle?: string;
  website?: string;
  linkedinUrl?: string;
}
```

---

## Campaign Tools

### create_campaign
```typescript
// Input
{
  name: string;
  sampleEmail: string;
  outreachGuide: string;
  messageIntent: string;
  emailAccountIds?: string[];     // sa_... IDs
  emailAddresses?: string[];      // email addresses
  leads?: Lead[];
  sourceUrl?: string;
  autoRespond?: boolean;          // default: true
  autoSendResponses?: boolean;    // default: false
  autosend?: boolean;             // default: false
  dailySendLimit?: number;
  followUpCount?: number;         // 0-5
  followUpWindow?: number;        // days between follow-ups
  followUpTrigger?: "no_action" | "no_open";
  scheduleStart?: string;         // ISO 8601
}

// Output
{
  success: boolean;
  workflowId: string | null;
  leadCount?: number;
  blocked?: boolean;
  reasons?: string[];
  message: string;
}
```

### update_campaign_settings
```typescript
// Input
{
  workflowId: string;
  // + any fields from create_campaign (all optional)
}

// Output
{
  success: boolean;
  workflowId: string;
}
```

### launch_campaign
```typescript
// Input
{
  workflowId: string;
  autosend?: boolean;
  messageIntent?: string;
  outreachGuide?: string;
  dailySendLimit?: number;
}

// Output
{
  success: boolean;
  workflowId: string;
  message: string;
}
```

### pause_campaign
```typescript
// Input
{ workflowId: string; }

// Output
{ success: boolean; workflowId: string; status: string; }
```

### resume_campaign
```typescript
// Input
{ workflowId: string; }

// Output
{ success: boolean; workflowId: string; status: string; }
```

### get_campaign_performance
```typescript
// Input
{ workflowId: string; }

// Output
{
  workflowId: string;
  workflowName: string;
  status: string;
  stage: "enrichment" | "drafting" | "sending" | "complete";
  leadCounts: {
    total: number;
    enriched: number;
    drafted: number;
    sent: number;
    opened: number;
    replied: number;
    bounced: number;
    failed: number;
  };
  metrics: {
    openRate: number;
    replyRate: number;
    bounceRate: number;
    clickRate: number;
  };
}
```

### list_campaign_drafts
```typescript
// Input
{
  workflowId: string;
  status?: "drafted" | "pending_review" | "all";  // default: "all"
  limit?: number;    // default: 250
  offset?: number;   // default: 0
}

// Output
{
  workflowId: string;
  total: number;
  drafts: Array<{
    leadId: string;
    email: string;
    subject: string;
    body: string;
    status: string;
  }>;
}
```

### sample_campaign_drafts
```typescript
// Input
{
  workflowId: string;
  status?: "drafted" | "pending_review" | "all";
  count?: number;    // default: 5
}

// Output — same shape as list_campaign_drafts
```

### send_campaign_drafts
```typescript
// Input
{
  workflowId: string;
  leadIds?: string[];  // omit to send all
}

// Output
{
  success: boolean;
  workflowId: string;
  queued: number;
}
```

### submit_campaign_plan
```typescript
// Input: legacy plan artifact (see older agent contract docs)
// Output: { planId: string; status: string; }
```

### approve_campaign_plan
```typescript
// Input: { planId: string; }
// Output: { workflowId: string; status: string; }
```

---

## Lead Tools

### import_leads
```typescript
// Input
{
  workflowId?: string;
  leads?: Lead[];
  sourceUrl?: string;
}

// Output
{
  success: boolean;
  workflowId: string;
  imported: number;
  skipped: number;
  message: string;
}
```

### get_lead_group_details
```typescript
// Input
{
  workflowId?: string;
  workflowName?: string;
}

// Output
{
  workflowId: string;
  workflowName: string;
  status: string;
  leadCounts: {
    total: number;
    uploaded: number;
    enriched: number;
    drafted: number;
    sent: number;
    opened: number;
    replied: number;
    bounced: number;
    failed: number;
    pending: number;
  };
}
```

### get_lead_sample
```typescript
// Input
{
  workflowId: string;
  count?: number;           // default: 5, max: 20
  preferEnriched?: boolean; // default: true
}

// Output
{
  workflowId: string;
  leads: Array<{
    id: string;
    email: string;
    name: string | null;
    companyName: string | null;
    jobTitle: string | null;
    status: string;
    enrichmentData: Record<string, unknown> | null;
  }>;
}
```

### enrich_lead_sample
```typescript
// Input
{
  workflowId: string;
  leadIds?: string[];  // max 5; defaults to first 3
}

// Output
{
  success: boolean;
  workflowId: string;
  queued: number;
  message: string;
}
```

---

## Sender Tools

### list_ready_senders
```typescript
// Input: {}

// Output
{
  senders: Array<{
    id: string;
    email: string;
    displayName: string | null;
    domainName: string;
    status: string;
    connectionStatus: string;
  }>;
  total: number;
}
```

### get_sender_health
```typescript
// Input
{ senderAccountId: string; }

// Output
{
  senderAccountId: string;
  email: string;
  status: string;
  connectionStatus: string;
  healthGates: {
    domainVerified: boolean;
    warmupComplete: boolean;
    spfValid: boolean;
    dkimValid: boolean;
    connectionValid: boolean;
  };
  ready: boolean;
  lastCheckedAt: string;
}
```

### create_sender
```typescript
// Input
{
  managedDomainId: string;
  localPart: string;
  displayName?: string;
}

// Output
{
  success: boolean;
  senderAccountId: string;
  email: string;
  status: string;
  message: string;
}
```

### assign_sender_to_campaign
```typescript
// Input
{
  workflowId: string;
  senderAccountId: string;
}

// Output
{
  success: boolean;
  workflowId: string;
  senderAccountId: string;
  email: string;
}
```

### pause_sender
```typescript
// Input: { senderAccountId: string; }
// Output: { success: boolean; senderAccountId: string; status: string; }
```

### delete_sender
```typescript
// Input: { senderAccountId: string; }
// Output: { success: boolean; senderAccountId: string; deleted: boolean; }
```

---

## Domain Tools

### list_managed_domains
```typescript
// Input: {}
// Output: { domains: ManagedDomain[]; total: number; }
// (See resource-schemas.md for ManagedDomain shape)
```

### add_domain
```typescript
// Input
{ domainName: string; }

// Output
{
  success: boolean;
  managedDomainId: string;
  domainName: string;
  dnsRecords: Array<{
    type: string;
    hostname: string;
    value: string;
    purpose: string;
  }>;
  message: string;
}
```

### check_domain_status
```typescript
// Input
{
  managedDomainId?: string;
  domainName?: string;
}

// Output
{
  managedDomainId: string;
  domainName: string;
  status: string;
  tracks: Record<string, {
    status: string;
    errors: string[];
    dnsRequirements: Array<{
      type: string;
      hostname: string;
      value: string;
      status: string;
      verified: boolean;
    }>;
  }>;
  nextAction: string;
}
```

### trigger_domain_verification
```typescript
// Input
{ managedDomainId: string; }

// Output: same as check_domain_status + message
```

---

## Email Generation Tools

### generate_email_preview
```typescript
// Input
{
  workflowId: string;
  leadId: string;
  sampleEmail: string;
  outreachGuide: string;
  messageIntent: string;
}

// Output
{
  subject: string;
  body: string;
  leadId: string;
  leadEmail: string;
}
```

### refine_email_preview
```typescript
// Input
{
  workflowId: string;
  leadId: string;
  currentSubject: string;
  currentBody: string;
  revisionInstructions: string;
  sampleEmail: string;
  outreachGuide: string;
  messageIntent: string;
}

// Output: same as generate_email_preview
```

### generate_campaign_guide
```typescript
// Input
{
  workflowId: string;
  brief: string;
  messageIntent: string;
}

// Output
{
  sampleEmail: string;
  outreachGuide: string;
  suggestedSubjectLines: string[];
  followUpGuidance: string;
}
```

---

## Meta Tools

### get_agent_key_info
```typescript
// Input: {}

// Output
{
  workspaceId: string;
  name: string;
  autonomyLevel: "observer" | "copilot" | "autonomous";
  keyPrefix: string;
  lastUsedAt: string | null;
  expiresAt: string | null;
  createdAt: string;
}
```

### subscribe_events
```typescript
// Input
{
  url: string;           // HTTPS only
  secret: string;        // min 16 chars
  eventTypes?: string[]; // empty = all events
}

// Output
{
  success: boolean;
  endpointId: string;
  url: string;
  eventTypes: string[];
  message: string;
}
```
