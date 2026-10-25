# TrustVault — Secure Document Sharing with an Audit Trail

TrustVault is a Django web application for private document storage, explicit per-document sharing, READ/EDIT permissions, revocation, and activity auditing. It is a hackathon development project; it has **not** undergone an independent security audit or production acceptance test.

## Implemented features

- User registration, login, and logout using Django authentication.
- Private document upload (10 MB maximum; extension allowlist), owner-only by default.
- Per-document sharing with registered usernames and READ or EDIT permission.
- READ users can download but cannot change title metadata or manage shares.
- EDIT users can download and change title metadata but cannot manage shares.
- Owners can update or revoke grants. Access is checked server-side on each protected request.
- Audit events for upload, download, title edit, grant, update, and revocation.
- Documents are stored in `private_media/`, not exposed via a public media URL.
- CSRF-protected state-changing forms, password validators, unique document/user share constraint, and basic security headers.

**Permission semantics:** EDIT means editing the document's title metadata only. It does not edit the binary contents of a PDF, Word file, image, or other uploaded file. Revocation blocks future server requests but cannot erase copies already downloaded by a recipient.

## Run locally (Windows PowerShell)

From the folder containing `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

Open `http://127.0.0.1:8000/register/`, create two accounts, upload a document with the first account, and use **Share / Access** to grant READ or EDIT to the second account. Test revocation by trying the recipient's download URL after revoking access.

Optional administrator account:

```powershell
python manage.py createsuperuser
```

## Tests

`vault/tests.py` covers registration and login, unauthorized downloads, READ/EDIT restrictions, owner grant/revoke, upload size/type validation, and upload/download/share audit events. Tests use a temporary private-file directory so uploaded test files do not remain in the project's `private_media/`. Run `python manage.py test` before submission. Do not claim tests passed unless you ran them and observed success.

## Git safety

The project `.gitignore` excludes local environment files, the SQLite database, virtual environments, and `private_media/` uploads while keeping `.env.example` available. Ignore rules do not remove files already tracked by Git or erase them from repository history. Before pushing, inspect the staged file list and check repository history for any previously committed secrets or private documents.

## Deployment checklist

1. Use a managed production database and private file storage with restricted filesystem/object-storage permissions.
2. Set a unique, strong `DJANGO_SECRET_KEY`; never commit secrets.
3. Set `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS` to the exact deployed hostname(s), comma-separated.
4. Serve over HTTPS. If your host terminates TLS, set `DJANGO_SECURE_SSL_REDIRECT=0` only when the host already enforces HTTPS correctly.
5. Run `python manage.py migrate` and `python manage.py collectstatic` during deployment; configure static-file serving.
6. Do not expose `private_media/` through a public static/media URL or reverse-proxy alias.
7. Back up the database and private files; set quotas and monitor storage.
8. Add malware scanning and content-based file validation before accepting untrusted public uploads. Extension checks are not sufficient to prove a file is safe.
9. Consider rate limiting, account verification, password reset, and monitoring before real-world use.

## Audit limitations

Audit entries are read-only in Django admin, but a database administrator or compromised application process could still alter them. For stronger tamper evidence, use a remote append-only log, restricted database roles, or a verified hash chain and alerting. Audit details should not contain secrets or document contents.

## Hackathon documentation

- `THREATS.md` describes threats and testable mitigations.
- `PROMPTS.md` is a working log template. Update it as you actually work, with dates, prompts, observed results, corrections, and commit links. The example starting entries are based on the work documented in this conversation; add actual commit hashes and test outcomes rather than inventing them.

## Scope and honesty

This is a working development baseline, not a security certification. The test suite must be executed in the target environment, and deployment must be verified from an unauthenticated browser before submission. Keep the README accurate to the code that is actually deployed.
