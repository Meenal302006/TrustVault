# TrustVault
TrustVault is a Django-based secure document-sharing platform that protects confidential files through private storage and server-side access control. Users can upload documents, share them with authorized users using READ and EDIT permissions, revoke access, and track document activities through an audit trail.
# TrustVault — Secure Document Sharing

## Overview

TrustVault is a Django-based secure document-sharing platform designed to protect confidential files through private storage, server-side access control, and activity logging. Users can upload documents, share them with authorized users, and manage permissions.

## Features

- **User Authentication:** Register, log in, and log out securely.
- **Private Document Storage:** Store uploaded files outside publicly accessible media URLs.
- **Role-Based Access:** Owners can manage their documents and sharing permissions.
- **READ Permission:** Authorized users can view or download shared documents.
- **EDIT Permission:** Authorized users can download documents and edit permitted metadata.
- **Access Revocation:** Owners can update or revoke sharing permissions.
- **Audit Trail:** Record important actions, including uploads, downloads, edits, and permission changes.
- **Security Controls:** CSRF protection, password validation, file-extension restrictions, and server-side permission checks.

## Technology Stack

- Python
- Django
- SQLite for local development
- HTML and CSS
- Django Authentication System

## Project Structure

```text
TrustVault/
├── manage.py
├── requirements.txt
├── README.md
├── THREATS.md
├── PROMPTS.md
├── trustvault/
├── vault/
├── templates/
├── static/
├── sample_documents/
└── private_media/
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd TrustVault_Starter
```

Replace the placeholder with your actual public repository URL.

### 2. Create a virtual environment

**Windows:**

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Run system checks and tests

```bash
python manage.py check
python manage.py test
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## How to Use

1. Register an account or log in.
2. Upload a document.
3. Share it with another registered user.
4. Assign READ or EDIT permission.
5. Review document activity in the audit trail.
6. Update or revoke access when required.

## Security Considerations

- Document access must be verified on the server for every protected request.
- Private files should not be served through publicly accessible URLs.
- Revoking access prevents future authorized access but cannot delete copies already downloaded.
- Audit logs provide accountability but are not guaranteed to be tamper-proof against database administrators or a compromised application.
- Production deployment requires a strong secret key, HTTPS, appropriate allowed hosts, persistent private file storage, a production database, backups, and additional security testing.

## AI Usage Transparency

AI-assisted development should be documented honestly in `PROMPTS.md`, including prompts, generated suggestions, errors discovered, corrections made, and relevant commit references.

## Project Documentation

- `README.md` — Setup, features, and usage.
- `THREATS.md` — Security threats and mitigations.
- `PROMPTS.md` — AI-assisted development log.

## Limitations

This project is a security-focused prototype and should not be considered independently audited or production-secure without further testing and deployment hardening.

## License

Add a license file if you intend to distribute this project under a specific open-source license.
3
