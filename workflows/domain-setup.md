# Workflow: Domain Setup

Register a sending domain and walk through DNS verification.

**Required autonomy level:** `copilot`  
**Time:** 10–60 minutes (depends on DNS propagation)

---

## Overview

```
1. Check existing domains
2. Add domain → get DNS records
3. User publishes DNS records
4. Trigger verification
5. Confirm verified
6. Create senders on the domain
```

---

## Step 1 — Check existing domains

```json
// resources/read
{ "uri": "muntu://domains/{workspaceId}" }
```

If a domain already shows `status: "verified"` and `nextAction: "none"`, no setup is needed.

If a domain shows a non-`none` `nextAction`, pick up from that step:
- `publish_dns_records_then_trigger_verification` → Step 3
- `trigger_verification` → Step 4
- `review_provider_errors` / `resolve_track_failures` → Step 4 (re-trigger)

---

## Step 2 — Add domain

```json
// tools/call: add_domain
{
  "domainName": "outreach.yourdomain.com"
}
```

**Response includes `dnsRecords`:**
```json
{
  "success": true,
  "managedDomainId": "md_abc123",
  "domainName": "outreach.yourdomain.com",
  "dnsRecords": [
    {
      "type": "TXT",
      "hostname": "outreach.yourdomain.com",
      "value": "v=spf1 include:mailersend.net ~all",
      "purpose": "SPF"
    },
    {
      "type": "CNAME",
      "hostname": "mta._domainkey.outreach.yourdomain.com",
      "value": "dkim.mailersend.net",
      "purpose": "DKIM"
    },
    {
      "type": "CNAME",
      "hostname": "mlsnd._domainkey.outreach.yourdomain.com",
      "value": "dkim2.mailersend.net",
      "purpose": "DKIM2"
    }
  ]
}
```

**Show these records to the user** and ask them to add them at their DNS provider (Cloudflare, Route53, Namecheap, etc.).

**Important:** Subdomain recommended (e.g., `outreach.yourdomain.com`, not `yourdomain.com`) to keep outreach sending separate from primary domain reputation.

---

## Step 3 — Wait for DNS propagation

DNS changes typically take 5–30 minutes. For some providers it can take up to 24 hours.

**Do not trigger verification immediately** — the check will fail if DNS hasn't propagated.

You can confirm propagation by checking the domain status before triggering:

```json
// tools/call: check_domain_status
{
  "managedDomainId": "md_abc123"
}
```

Look at `tracks.sending_infra.dnsRequirements` — each record will show `"status": "detected"` once propagated.

---

## Step 4 — Trigger verification

Once DNS is live:

```json
// tools/call: trigger_domain_verification
{
  "managedDomainId": "md_abc123"
}
```

**Possible outcomes:**

| Response `status` | Meaning | Next step |
|---|---|---|
| `verified` | All tracks verified | Proceed to Step 5 |
| `pending` | DNS not yet detected | Wait and retry Step 4 |
| `failed` | Provider rejected records | Check `tracks[*].errors` |

**On failure**, check which track failed and what error the provider returned:

```json
{
  "tracks": {
    "sending_infra": {
      "status": "failed",
      "errors": ["SPF record format invalid — must start with 'v=spf1'"]
    }
  }
}
```

Fix the DNS record and re-trigger verification.

---

## Step 5 — Confirm verified

```json
// resources/read
{ "uri": "muntu://domains/{workspaceId}" }
```

Check that the domain shows:
```json
{
  "status": "verified",
  "verified": true,
  "nextAction": "none"
}
```

The domain is now ready to use for senders and campaigns.

---

## Step 6 — Create senders

Create one or more email accounts on the verified domain:

```json
// tools/call: create_sender
{
  "managedDomainId": "md_abc123",
  "localPart": "hello",
  "displayName": "Hello Team"
}
```

```json
// tools/call: create_sender
{
  "managedDomainId": "md_abc123",
  "localPart": "outreach",
  "displayName": "Outreach Team"
}
```

New senders start in `provisioning` status and go through automated warm-up.

**Listen for `sender.ready` event** (webhook) or poll `get_sender_health` until `ready: true`.

---

## Tips

- **Use a subdomain** — never use your primary domain for outreach to protect brand reputation
- **One domain, multiple senders** — you can create many email accounts on the same domain
- **Verification expiry** — domains can de-verify if DNS records are removed; `domain.verification_expired` event fires when this happens
