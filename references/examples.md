# Original illustrative examples

All examples are hypothetical. Names, numbers, timestamps and outcomes below are **illustrative only**, not observations of a real system.

## 1. Production incident escalation

**Situation:** Since 14:05 UTC, the checkout API's p95 latency increased from approximately 220 ms to 1.8 s. Roughly 8% of checkout requests currently return 5xx. The service is degraded; the on-call responder needs a mitigation decision.

**Background:** A connection-pool configuration change was deployed at 14:00 UTC. Error traces show repeated connection-acquisition timeouts. Earlier deploys are not known to have the same errors. No rollback has been attempted.

**Assessment:** The timing and traces make pool exhaustion a plausible cause, but resource metrics and a rollback comparison have not yet confirmed causality. Waiting risks continued failed checkouts.

**Recommendation:** Request incident commander approval to roll back the pool configuration via the standard procedure. The on-call responder should compare error rate and p95 latency before/after rollback and retain logs. If the rollback does not improve either metric, escalate to database/infra responders and continue diagnosis.

## 2. Reproducible desktop-app bug

**Situation:** Saving a document with a non-ASCII filename fails on Windows; saving the same content under an ASCII filename succeeds.

**Background:** Reproducible on build 2.4.1 with Windows 11: open an unsaved document, choose `C:\\Temp\\résumé.txt`, click Save, observe “Path unavailable”. The document is not written. No Linux/macOS outcome has been checked.

**Assessment:** Encoding or normalization within the save-path conversion is suspected, not established. Scope beyond the Windows save path is unknown.

**Recommendation:** Assign the save-path owner to trace encoding at the UI/native boundary, identify the first incorrect path representation, and correct the shared conversion. Validate a save and reopen using representative Unicode filenames; report platform coverage rather than asserting it.

## 3. Code-review finding

**Situation:** The new worker callback writes to `activeJobs` while the UI thread iterates it. The submitted change does not show coordination between these operations.

**Background:** The write occurs in `Worker::onComplete`; the read occurs in `Dashboard::render`. Both use the same mutable collection. I have not executed a concurrency reproducer.

**Assessment:** Concurrent mutation may invalidate iteration or cause a data race depending on actual thread scheduling and ownership. This is a correctness concern, not a style preference.

**Recommendation:** Please establish the threading contract or marshal updates to the owning thread, then add an appropriate verification case if the repository's existing tests cover this flow. Document the mechanism used to ensure safe access.

## 4. Architecture decision request

**Situation:** We need a storage engine for a single-node, offline-first desktop application before the sync subsystem is implemented.

**Background:** Requirements currently include local transactions, migration support, and zero mandatory server dependency. The shortlisted choices are SQLite and a remotely managed database. Cross-device sync is planned but not yet designed.

**Assessment:** SQLite aligns with the stated offline and deployment constraints. A remote database could ease centralized coordination but introduces connectivity and operation requirements. Future sync complexity remains unresolved either way.

**Recommendation:** Approve SQLite as the local system of record, with a boundary around persistence access. Revisit sync topology when conflict resolution and multi-device requirements are specified. Record this as a reversible choice, not a claim that sync is solved.

## 5. Sub-agent / engineering handoff

**Situation:** The CLI's file-glob parser refactor is partially implemented. It is not ready for merge because the Windows drive-letter case remains unresolved.

**Background:** The parsing change is on branch `feature/glob-parser` at a recorded revision (insert actual commit hash). Existing Unix-like glob scenarios were manually inspected. The integration suite has not been run. The old parser accepted `C:\\src\\*.cpp`; the current refactor unexpectedly treats `C:` as a special prefix in a local reproduction.

**Assessment:** The new tokenization appears to conflict with native drive prefixes, but the exact source of the behavior is unverified. Further speculative work risks breaking existing Windows inputs.

**Recommendation:** Continue from the cited revision: establish the intended grammar and find the first incorrect tokenization for drive-letter paths. Implement the smallest compatible correction, run the relevant existing checks, and report observed pass/fail outcomes plus any remaining gaps. Do not report the refactor complete before verification.
