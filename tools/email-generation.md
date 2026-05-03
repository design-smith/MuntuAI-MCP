# Email Generation Tools

Tools for generating and refining email previews and campaign guides before launching.

These tools do not persist anything — they are pure generation utilities for reviewing quality before committing to a full campaign launch.

---

## generate_email_preview

**Min autonomy:** `copilot`

Generate a preview email for a specific lead without persisting it. Use this to show the user a sample of what the AI will write before launching the campaign.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "leadId": "lead_xyz",
  "sampleEmail": "Hi {{firstName}},\n\nI saw you're building in the security space...",
  "outreachGuide": "Focus on the lead's recent company news and connect it to our security automation offering.",
  "messageIntent": "Book a 15-minute demo"
}
```

| Field | Required | Description |
|---|---|---|
| `workflowId` | Yes | The workflow the lead belongs to |
| `leadId` | Yes | The specific lead to generate for |
| `sampleEmail` | Yes | Template email to use as style reference |
| `outreachGuide` | Yes | AI drafting instructions |
| `messageIntent` | Yes | One-line goal |

**Response:**
```json
{
  "subject": "Quick question about your security stack, Alex",
  "body": "Hi Alex,\n\nI noticed Acme Corp recently expanded into enterprise security monitoring...\n\nWould you be open to a quick 15-minute chat?",
  "leadId": "lead_xyz",
  "leadEmail": "alex@acmecorp.com"
}
```

---

## refine_email_preview

**Min autonomy:** `copilot`

Regenerate a preview email for a lead incorporating user feedback. Pass the current subject and body along with revision instructions.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "leadId": "lead_xyz",
  "currentSubject": "Quick question about your security stack, Alex",
  "currentBody": "Hi Alex,\n\nI noticed Acme Corp recently...",
  "revisionInstructions": "Make it shorter. Remove the company news reference. Lead with the specific pain point of manual threat triage.",
  "sampleEmail": "Hi {{firstName}},\n\n...",
  "outreachGuide": "Keep it under 80 words.",
  "messageIntent": "Book a 15-minute demo"
}
```

| Field | Required | Description |
|---|---|---|
| `currentSubject` | Yes | Current subject line to refine |
| `currentBody` | Yes | Current body to refine |
| `revisionInstructions` | Yes | What to change |
| Others | Yes | Same as `generate_email_preview` |

**Response:** Same shape as `generate_email_preview`.

---

## generate_campaign_guide

**Min autonomy:** `copilot`

Generate campaign drafting guidance from a brief. Returns a sample email, campaign guide, and suggested follow-up content aligned to the real workflow configuration. Use this to get AI-generated recommendations for `sampleEmail` and `outreachGuide` before creating the campaign.

**Arguments:**
```json
{
  "workflowId": "wf_abc123",
  "brief": "We're targeting CTOs and security leads at mid-market companies. Our product, Zykr, automates threat investigation so analysts spend less time on manual triage. Goal: book demos.",
  "messageIntent": "Book a 15-minute Zykr demo"
}
```

| Field | Required | Description |
|---|---|---|
| `workflowId` | Yes | The workflow context (for lead data) |
| `brief` | Yes | Description of the campaign goal, target audience, and product |
| `messageIntent` | Yes | One-line goal of the campaign |

**Response:**
```json
{
  "sampleEmail": "Hi {{firstName}},\n\nI saw that {{companyName}} has grown its security team recently...",
  "outreachGuide": "Open with a specific observation about the company's security posture or recent growth. In the second paragraph, connect to how Zykr reduces analyst time on manual triage. Close with a soft ask for 15 minutes.",
  "suggestedSubjectLines": [
    "Quick question about your threat investigation workflow",
    "Reducing manual security triage at {{companyName}}",
    "Security automation for your team"
  ],
  "followUpGuidance": "Follow up 5 days after no response. Reference the initial email. Keep it to 2 sentences."
}
```

**Typical flow:**
1. Call `generate_campaign_guide` with a brief
2. Review the returned `sampleEmail` and `outreachGuide`
3. Use them directly in `create_campaign` or refine with `generate_email_preview`
