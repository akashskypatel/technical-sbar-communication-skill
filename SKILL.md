---
name: technical-sbar-communication
description: Structure or review technical communication using Situation, Background, Assessment, Recommendation (SBAR). Use for engineering status updates, incident escalation, bug triage, blockers, implementation handoffs, code-review findings, and technical decision requests where an audience needs a clear, actionable summary. Do not apply automatically to ordinary coding, research, or explanations that do not call for an actionable communication artifact.
---

# Technical SBAR Communication

Create focused, evidence-grounded technical messages that explain **what happened, what matters, what it means, and what action is needed**.

## When to use

Use when the user asks to draft, rewrite, summarize, critique, or organize an engineering communication: an incident report, escalation, bug report, investigation update, cross-team handoff, review finding, blocker, decision memo, or sub-agent status report.

Do **not** turn unrelated implementation, debugging, teaching, or research requests into SBAR messages. When the user requests a specific format, honor that format; SBAR can inform the content without forcing four visible headings.

## Procedure

1. **Identify the reader and purpose.** Determine who must understand or act, what decision/action is needed, and whether urgency changes the ordering or detail.
2. **Extract the evidence.** Distinguish confirmed observations, source links, reproductions, test/build output, hypotheses, unknowns, and constraints. Never fabricate metrics, execution, verification, owners, or dates.
3. **Situation (S):** State the issue or decision in 1-2 sentences. Include system/component, current impact or blocker, scope, onset/time when known, and urgency when justified.
4. **Background (B):** Give only the relevant baseline, recent changes, environment, chronology, and observable evidence needed to understand the situation. Prefer specific versions, affected paths, repro steps, logs, and links when available.
5. **Assessment (A):** Explain the current interpretation and implications. Separate evidence from inference; state confidence, competing explanations, material risks, and what remains unverified. Do not present an unconfirmed root cause as established.
6. **Recommendation (R):** State the next **specific** action or decision requested and why. Include owner, priority/deadline, validation or exit condition, and fallback only when known or useful. If evidence is insufficient, recommend a bounded investigation rather than inventing a fix.
7. **Edit for the audience.** Put the impact and ask first for urgent escalations. Reduce background for executives; preserve reproducibility and evidence for engineers. Use links rather than large unfiltered log dumps.
8. **Check accuracy.** Ensure the ask logically follows the assessment; label unknowns explicitly; preserve unresolved blockers, unsuccessful attempts, and verification gaps.

## Output contract

- Default: four short sections headed **Situation**, **Background**, **Assessment**, **Recommendation**, in that order.
- For urgent incidents: lead with a one-line impact and immediate ask; then expand into SBAR.
- For a chat message or PR comment: concise inline labels are acceptable.
- For a larger document: add an executive summary only when helpful; keep the four SBAR concepts intact.
- If a recipient, owner, priority, severity, date, result, or log link is unknown, omit it or say `unknown` / `not yet verified`; do not guess.
- If the user asks to **evaluate** a message, report missing evidence or ambiguous asks before offering a rewrite.
- If the user asks to **draft** a message, supply the complete draft rather than instructions for writing it.


## Optional template validation

When the user explicitly requests a structural completeness check of a saved SBAR message, run `python scripts/validate_sbar.py <file> --template <name>`. The available template names are `quick-update`, `incident-escalation`, `engineering-handoff`, `decision-request`, and `review-finding`. By default, the script requires all four non-placeholder SBAR sections and the required labeled fields in the selected template; `--sections-only` checks the four sections without exact field labels. A passing result **does not** verify factual accuracy, technical correctness, or evidence sufficiency; evaluate those separately.

## Progressive references

- [Usage patterns and quality criteria](references/usage-patterns.md) - audience guidance, severity handling, source hygiene, and anti-patterns.
- [Worked technical examples](references/examples.md) - incident, bug, review, design decision, and agent handoff.
- [Quick SBAR template](templates/quick-update.md) - generic short messages.
- [Incident escalation template](templates/incident-escalation.md) - live operational issues.
- [Engineering handoff template](templates/engineering-handoff.md) - blockers and work transfer.
- [Technical decision template](templates/decision-request.md) - choices needing approval.
- [Review finding template](templates/review-finding.md) - actionable code/design review findings.

The SBAR concept is adapted to software engineering. This package does not reproduce the source document or its clinical forms; see [provenance](SOURCE.md).
