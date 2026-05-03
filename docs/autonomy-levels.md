# Autonomy Levels

Every agent key has an autonomy level that controls which tools it can invoke. The level is set at key creation and cannot be changed — create a new key to upgrade or downgrade.

---

## The Three Levels

### observer

Read-only access. Can inspect all workspace data but cannot create, modify, or delete anything.

**Use when:** You want an agent to monitor campaigns, check domain status, or report on performance without risk of side effects.

### copilot

Read + create + modify. Can perform most actions an agent needs to run campaigns autonomously, but is blocked from destructive or high-impact operations.

**Use when:** You want an agent to manage campaigns end-to-end — from domain setup through email delivery — with a human still in control of pause/delete/resume.

### autonomous

Full access. Can pause, resume, and delete resources in addition to everything copilot can do.

**Use when:** You trust the agent to act fully independently without human approval on destructive actions.

---

## Permission Matrix

| Capability | observer | copilot | autonomous |
|---|---|---|---|
| Read campaigns, domains, senders, events | ✓ | ✓ | ✓ |
| Read lead groups, samples, drafts | ✓ | ✓ | ✓ |
| Get campaign performance metrics | ✓ | ✓ | ✓ |
| Get sender health | ✓ | ✓ | ✓ |
| Get agent key info | ✓ | ✓ | ✓ |
| Import leads | — | ✓ | ✓ |
| Create campaign | — | ✓ | ✓ |
| Update campaign settings | — | ✓ | ✓ |
| Launch campaign | — | ✓ | ✓ |
| Send campaign drafts | — | ✓ | ✓ |
| Enrich lead sample | — | ✓ | ✓ |
| Generate email preview / guide | — | ✓ | ✓ |
| Add domain | — | ✓ | ✓ |
| Trigger domain verification | — | ✓ | ✓ |
| Create sender | — | ✓ | ✓ |
| Assign sender to campaign | — | ✓ | ✓ |
| Register webhook | — | ✓ | ✓ |
| Pause campaign | — | — | ✓ |
| Resume campaign | — | — | ✓ |
| Pause sender | — | — | ✓ |
| Delete sender | — | — | ✓ |
| Delete webhook | — | — | ✓ |

---

## What Happens When the Level Is Insufficient

The server rejects the call and returns an MCP error:

```json
{
  "error": {
    "code": -32603,
    "message": "Insufficient autonomy level"
  }
}
```

The blocked attempt is also recorded in the workspace system event log with the reason `autonomy_level_insufficient`.

---

## Choosing the Right Level

**For monitoring and reporting agents:** `observer`

**For campaign automation agents (the most common case):** `copilot`  
This covers: domain setup, sender creation, lead import, campaign creation, launch, draft review, and sending.

**For fully autonomous agents that manage infrastructure:** `autonomous`  
Only use this if the agent needs to pause, resume, or delete resources without human intervention.

---

## Workspace Policy Ceiling

The workspace owner can set an `autonomyCeiling` in workspace policy. If the ceiling is set to `copilot`, then even a key with `autonomous` level will be restricted to copilot-level actions within that workspace. The key's level is always capped at the workspace ceiling.
