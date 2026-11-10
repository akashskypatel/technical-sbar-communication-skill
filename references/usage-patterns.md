# Technical SBAR: usage patterns and quality criteria

## Information model

| Section | Engineering question | Include | Avoid |
|---|---|---|---|
| **Situation** | What needs attention now? | Component, behavior/problem, scope, impact, urgency/onset | A long history before the point |
| **Background** | What context is necessary? | Versions, prior expected behavior, recent changes, reproduction, logs, previous attempts | Unsupported explanations, unrelated details |
| **Assessment** | What do the facts suggest? | Root-cause hypotheses labeled as hypotheses, confidence, alternatives, risks, missing evidence | Declaring an unverified cause or fix as certain |
| **Recommendation** | What happens next? | Specific request, proposed action or decision, owner if known, priority, success/exit condition | “Investigate further” without scope, invented ownership/ETA |

## Adapt by use case

**Incident escalation.** Lead with user/customer impact, affected service, when it started, and an actionable mitigation decision. State whether mitigation is proposed, authorized, attempted, or verified. Distinguish impact estimates from measured impact. Use the incident escalation template.

**Bug report/triage.** Include expected vs. observed behavior, a minimal reproduction (or explicitly state that it is not yet reproduced), relevant runtime/version, error outputs, suspected mechanism, and a decision about priority or ownership.

**Engineering handoff.** Include current branch/revision, what changed, what has actually been run, outcomes and failures, open blockers, risky assumptions, and precisely what the next person needs to decide or accomplish. Do not call partial or untested work complete.

**Code/design review.** State the affected code path, observed defect or potential risk, evidence and reachability, confidence, and an implementable request or question. Separate correctness concerns from style preferences.

**Architecture/technical decision.** State the decision to be made and why now; list constraints, alternatives and decision-relevant tradeoffs; assess risk/reversibility; request a choice or authorization with acceptance criteria.

**Agent-to-agent coordination.** Communicate confirmed progress, evidence references, unresolved blockers, authority/permission limits, and desired next outcome. The receiving agent should be able to investigate independently rather than simply executing speculative commands.

## Escalation and urgency

Use urgency only when supported by impact, deadlines, safety/security considerations, or operational consequences. Never transfer healthcare-specific contact channels, severity rules, or fixed escalation intervals to engineering.

If prompt or organization-specific incident policies apply, follow those policies. If the best action is uncertain, request an explicit owner or a bounded diagnostic step. Treat all proposed production changes, destructive operations, credential access, and security-sensitive actions as subject to authorization and established procedures.

## Evidence rules

- Label statements as **observed**, **inferred**, **reported**, or **unknown** where confusion is likely.
- Say *not run*, *failed*, *not reproduced*, or *not verified* accurately. A passing test only supports what it meaningfully exercises; it does not prove overall correctness.
- Preserve exact error snippets, version identifiers, filenames, timestamps and links when supplied. Quote sparingly and contextualize them.
- Do not claim an incident is resolved until the agreed verification is reported.
- State relevant preconditions, platform differences, rollout exposure, rollback constraints, and security consequences.
- Avoid exposing secrets, tokens, PII, internal credentials, or confidential log payloads.

## Compression

**Ultra-brief:** four labeled sentences for chat, each providing useful content.

**Standard:** 1-2 sentences for Situation; 2-5 relevant bullets for Background; concise interpretation and uncertainty in Assessment; one primary ask and verification in Recommendation.

**Detailed:** include issue links and evidence attachments, numbered reproduction, alternatives, failure modes and operational constraints only as needed for an independent decision.

## Review checklist

A useful SBAR message lets the reader answer all of these:

1. What exactly is wrong or undecided, and who/what is affected?
2. What evidence supports the description?
3. Which parts are established facts vs. interpretations?
4. What remains unknown or blocked?
5. What specific action or decision is requested?
6. How will the recipient know the requested action worked?
7. Are priority, ownership, and authorization claims grounded?

If the answer to any essential question is missing, flag the gap rather than filling it with invented detail.
