# TrustVault Threat Model

## Assets

- Uploaded documents and their metadata.
- User credentials and authenticated sessions.
- Document-sharing grants and permission state.
- Audit events used to investigate document activity.

## Trust boundaries

A browser is untrusted. All permissions must be checked in Django on every request. A document ID, hidden button, username, or previously issued URL is not proof of authorization. Private file storage must not be directly web-accessible.

## Threats and mitigations

| Threat | Example attack | Mitigation in this project | Verification |
|---|---|---|---|
| IDOR / unauthorized download | User B changes `/documents/1/download/` to another ID | `get_accessible_document` checks owner or current share before opening the file; unauthorized document is returned as not found | `test_unshared_user_cannot_download` |
| READ privilege escalation | READ user POSTs to title edit endpoint | Edit view requires OWNER or EDIT permission on the server | `test_read_user_can_download_but_cannot_edit_metadata` |
| Unauthorized share management | Recipient opens share/revoke endpoint directly | Share/revoke views require document ownership; revoke is POST-only and CSRF protected | `test_non_owner_cannot_manage_shares` and grant/revoke test |
| Stale access after revocation | Recipient reuses the same document URL | Permission is looked up from the database for each request; deleting the grant blocks future requests | `test_owner_can_grant_and_revoke_access` checks a post-revocation download |
| Malicious or oversized upload | Upload unexpected extension or >10 MB file | Extension allowlist and size check reject common disallowed inputs | `test_upload_rejects_disallowed_extension` and `test_upload_rejects_files_over_10_mb` |
| CSRF on state-changing operations | Third-party page tries to submit a revoke/share request | Django CSRF middleware and `{% csrf_token %}` on POST forms | Use Django client with CSRF checks enabled or browser test |
| Audit log manipulation | User tries to edit event in admin | Audit fields are read-only in Django admin | Inspect admin configuration; this is not protection from database administrators |
| Missing audit evidence | Upload, download, or share operation is omitted from the activity history | Views create an audit event for each supported operation | `test_upload_download_and_share_actions_are_audited` |
| Public file exposure | Guess media URL to retrieve private file | Private storage root is not configured as public media serving | Inspect URL config and deployment web-server config |
| Weak deployment configuration | Debug page leaks settings; secret key is known | Production settings require secret key and support `DJANGO_DEBUG=0`, allowed hosts, HTTPS cookies/security headers | Run deployment checklist and Django deploy checks |

## Known residual risks

- No independent penetration test has been performed.
- Audit records are not cryptographically tamper-evident against database-level access.
- Extension checks do not validate file contents and do not scan malware.
- The demo does not implement MFA, email verification, rate limiting, or a password-reset workflow.
- Revocation cannot delete previously downloaded copies.
- EDIT permission currently allows editing title metadata, not the file's binary content.
- Production deployment, storage isolation, TLS termination, backups, and the live site must be tested in the actual hosting environment.

## Security test rule

A test is evidence only when it has actually been executed and its result recorded. Never describe an unrun test as passing. For the hackathon, record each additional threat test and its actual output here and in the commit history.

The Django test client does not enforce CSRF checks unless configured to do so. CSRF protection is enabled in middleware and forms, but it should be verified separately with a CSRF-enforcing client or browser test before claiming test coverage for it.
