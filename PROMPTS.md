# AI Tool / Prompt Work Log

The challenge asks for dated entries explaining what was requested, what the tool produced, what was wrong, and what was done instead. Keep this file honest and update it while working. Replace `TODO` fields with real commit links/results; do not invent commits or claim unrun tests passed.

## 2026-10-24 — Registration and database startup
- **Prompt/request:** Diagnose the missing `vault_document` table after registration and make the starter app runnable.
- **Tool output/approach:** Suggested Django migration commands and a registration-enabled project ZIP.
- **Problem found:** Registration success did not prove that the dashboard's document table existed; the first ZIP path/setup experience was also confusing.
- **Correction/action:** Run `showmigrations`, `makemigrations`, `migrate`, and `check` in the extracted project; preserve existing data and do not delete the database.
- **Evidence:** TODO — record the actual command output and commit URL.

## 2026-10-25 — Access control requirements
- **Prompt/request:** Add document sharing with READ/EDIT permissions and revocation for TrustVault.
- **Tool output/approach:** A starter implementation added share grants, protected download/edit views, and owner-only grant/revoke endpoints.
- **Security review:** UI controls alone are not security; every protected request must check the current database permission. EDIT is explicitly limited to title metadata.
- **Correction/action:** Review server-side guards and test unauthorized download, READ edit denial, owner-only share management, and revocation. Do not claim the suite passes until run locally.
- **Evidence:** TODO — record actual test output and commit URL.

## 2026-10-25 — Hackathon threat model and deployment
- **Prompt/request:** Align the project with the Snovasys judging focus on security, threat thinking, functionality, AI-use evidence, engineering quality, and deployment.
- **Tool output/approach:** Drafted a threat model, deployment checklist, and AI-use log structure.
- **Risk/limitation identified:** A read-only Django admin does not make audit logs tamper-proof against database administrators; extension allowlists do not prove uploaded content is safe.
- **Correction/action:** Document residual risks honestly, add tests for identified authorization boundaries, and avoid claiming production readiness without deployment verification.
- **Evidence:** TODO — add actual test results and commit URL.


## 2026-10-25 — Understanding judging criteria
- **Prompt/request:** Align TrustVault with the Snovasys challenge instructions and security-weighted evaluation.
- **Tool output/approach:** Broke the evaluation into security, threat thinking, functionality, AI-use evidence, engineering quality, and deployment/documentation.
- **Problem found:** A feature checklist alone is not proof of security; claims need test evidence and a stranger must be able to run the deployed project.
- **Correction/action:** Add a threat model and deployment checklist; explicitly mark tests/deployment as unverified until executed.
- **Evidence:** TODO — add actual commit URL and any portal submission evidence.

## 2026-10-25 — Upload validation review
- **Prompt/request:** Improve the project for a security-focused document-sharing assessment.
- **Tool output/approach:** Reviewed the upload form and added a filename-extension allowlist plus a 10 MB limit.
- **Problem found:** Extension and size checks reduce accidental/obvious misuse but do not establish file content safety and do not replace malware scanning.
- **Correction/action:** Document the residual risk in `THREATS.md` and the README; add a test for a disallowed extension. Run the test locally before claiming it passes.
- **Evidence:** TODO — add actual test output and commit URL.

## Future dated entries — add as work happens
For every significant AI-assisted change, add a new dated section with: (1) exact request, (2) output/approach, (3) bug or unsafe assumption found, (4) your correction, (5) tests run and actual results, and (6) commit URL. The challenge asks for at least five dated entries; add two or more focused on authorization/access control/audit trail. Do not backdate work or fabricate history.
