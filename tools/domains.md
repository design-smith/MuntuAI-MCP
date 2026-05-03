# Domain Tools

Tools for registering and verifying sending domains.

---

## list_managed_domains

**Min autonomy:** `observer`

List all managed domains for the workspace with verification status, DNS requirements, provider track errors, and a `nextAction` hint.

**Arguments:** None

**Response:**
```json
{
  "domains": [
    {
      "id": "md_abc123",
      "domainName": "outreach.example.com",
      "status": "verified",
      "verified": true,
      "tracks": {
        "sending_infra": { "status": "verified", "errors": [] },
        "mailbox_infra": { "status": "verified", "errors": [] }
      },
      "dnsRequirements": [],
      "nextAction": "none"
    }
  ],
  "total": 2
}
```

**`nextAction` values:**
| Value | Meaning |
|---|---|
| `none` | Domain is verified, no action needed |
| `publish_dns_records_then_trigger_verification` | DNS records need to be added first |
| `trigger_verification` | DNS is live, call `trigger_domain_verification` |
| `review_provider_errors` | Provider returned an error, check track details |
| `resolve_track_failures` | Verification failed, needs investigation |
| `inspect_domain_status` | Unknown state, call `check_domain_status` |

---

## add_domain

**Min autonomy:** `copilot`

Register a new sending domain. Returns the DNS records that must be added to the domain's DNS provider before verification can proceed.

**Arguments:**
```json
{ "domainName": "outreach.example.com" }
```

**Response:**
```json
{
  "success": true,
  "managedDomainId": "md_abc123",
  "domainName": "outreach.example.com",
  "dnsRecords": [
    {
      "type": "TXT",
      "hostname": "outreach.example.com",
      "value": "v=spf1 include:mailersend.net ~all",
      "purpose": "SPF"
    },
    {
      "type": "CNAME",
      "hostname": "mta._domainkey.outreach.example.com",
      "value": "dkim.mailersend.net",
      "purpose": "DKIM"
    }
  ],
  "message": "Add these DNS records, then call trigger_domain_verification"
}
```

**After adding DNS records:** Call `trigger_domain_verification` to start the verification check. DNS propagation typically takes 5–30 minutes.

---

## check_domain_status

**Min autonomy:** `observer`

Check the DNS verification status of a domain across both the sending infrastructure (MailerSend) and mailbox infrastructure tracks. Includes DNS requirements, provider errors, and the next action needed.

**Arguments:**
```json
{ "managedDomainId": "md_abc123" }
```

Or by domain name:
```json
{ "domainName": "outreach.example.com" }
```

**Response:**
```json
{
  "managedDomainId": "md_abc123",
  "domainName": "outreach.example.com",
  "status": "pending",
  "tracks": {
    "sending_infra": {
      "status": "pending",
      "errors": [],
      "dnsRequirements": [
        {
          "type": "CNAME",
          "hostname": "mta._domainkey.outreach.example.com",
          "value": "dkim.mailersend.net",
          "status": "pending",
          "verified": false
        }
      ]
    },
    "mailbox_infra": {
      "status": "verified",
      "errors": []
    }
  },
  "nextAction": "trigger_verification"
}
```

---

## trigger_domain_verification

**Min autonomy:** `copilot`

Trigger a DNS verification check for a domain after DNS records have been published. Returns the refreshed status. If verification still shows pending, the DNS records may not have propagated yet — wait and call `check_domain_status` again.

**Arguments:**
```json
{ "managedDomainId": "md_abc123" }
```

**Response:**
```json
{
  "managedDomainId": "md_abc123",
  "domainName": "outreach.example.com",
  "status": "verified",
  "tracks": {
    "sending_infra": { "status": "verified", "errors": [] },
    "mailbox_infra": { "status": "verified", "errors": [] }
  },
  "nextAction": "none",
  "message": "Domain verified successfully"
}
```

If not yet verified:
```json
{
  "status": "pending",
  "nextAction": "trigger_verification",
  "message": "DNS records not yet detected. Wait for propagation and try again."
}
```
