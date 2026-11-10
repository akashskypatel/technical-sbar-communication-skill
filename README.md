# Technical SBAR Communication

A portable agent skill for clear, actionable technical/software-engineering communication based on the **Situation – Background – Assessment – Recommendation** structure.

## What is included

- `SKILL.md`: activation cues, process, and output contract.
- `references/usage-patterns.md`: how to tailor SBAR to technical audiences.
- `references/examples.md`: five original illustrative examples.
- `templates/`: ready-to-fill engineering communication templates.

## Installation

Copy the `technical-sbar-communication/` folder, with its `SKILL.md`, into the skills directory supported by your agent or assistant. The precise discovery path depends on the host platform. No scripts, packages, network access, or dependencies are required.

## Example prompts

- “Rewrite this on-call escalation in technical SBAR format. Keep unknown root causes explicit.”
- “Prepare an SBAR handoff from these investigation logs and list unresolved blockers.”
- “Review this pull-request comment for missing evidence and an unclear recommendation.”
- “Turn these architecture tradeoffs into a decision request with a specific ask.”

## Defaults

Keep communication brief; cite actual logs, files, and tests when provided. Separate observations from conclusions. Finish with a clear action, decision, or evidence-gathering request. Do not overstructure routine answers.
