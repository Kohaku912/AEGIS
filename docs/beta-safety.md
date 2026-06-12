# Beta Safety — Simplified Safety Model

## Overview

Beta version uses a simplified safety model based on action categories
rather than per-site or per-capability rules.

## Safety Categories

### 1. READ (Auto-Allowed)

Reading and extracting information from:
- Web pages
- User-owned accounts (SNS, email, notifications)
- System status
- Device state

**No approval needed. Always audited.**

### 2. DRAFT (Auto-Allowed)

Creating content locally:
- Reply drafts
- Post drafts
- Blog article drafts
- Email drafts

**No approval needed. Content stays local. Never sent externally.**

### 3. EXTERNAL_SEND (Approval Required)

Sending or publishing content externally:
- SNS post
- DM send
- Email send
- Blog publish
- Comment post

**Always requires Approval UI.**

### 4. PAYMENT (Blocked or Approval)

Financial operations:
- Purchases
- Paid subscriptions
- Payment info entry

**Blocked by default. Requires explicit approval if needed.**

### 5. BLOCKED (Always Denied)

Operations that are never allowed:
- CAPTCHA solving/bypass
- Bot detection evasion
- Stealth browser/proxy abuse
- Spam/bulk operations
- Bulk account creation
- Identity document upload
- Age verification bypass

**Always denied. No approval possible.**

## Enforcement Points

### LLM Task Interpreter
- Classifies task risk level
- Adds safety constraints to task plan
- Blocks obviously dangerous tasks

### Browser-Use Safety Boundary
- Checks task description for blocked patterns
- Adds safety instructions to browser-use tasks
- Prevents execution of blocked operations

### PolicyEngine (Structural)
- Final safety gate for all tool invocations
- Cannot be bypassed by any code path
- Deterministic rules, not LLM-based

### Approval UI
- User approves/denies EXTERNAL_SEND operations
- One-time or session approval
- All decisions logged to audit

## What Changed from Alpha

| Alpha | Beta |
|-------|------|
| Per-site browser functions | Browser-use natural language tasks |
| Keyword intent classifier | LLM Task Interpreter |
| Permissive autonomy profile | Simple read/draft/send model |
| Fine-grained signup functions | Browser-use task executor |
| Complex approval patterns | Category-based safety |

## Still Enforced

- PolicyEngine cannot be bypassed
- Approval UI required for external send
- AuditLog records all actions
- CAPTCHA/bot evasion never implemented
- Payment auto-execution never allowed
