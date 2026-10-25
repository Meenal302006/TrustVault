TRUSTVAULT — SECURE DOCUMENT SHARING
====================================

Start with README.md for full setup, feature scope, tests, deployment checklist, and security limitations.

WINDOWS QUICK START (from the folder containing manage.py)
1. py -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. python -m pip install -r requirements.txt
4. python manage.py check
5. python manage.py migrate
6. python manage.py test
7. python manage.py runserver
8. Open http://127.0.0.1:8000/register/ and create two accounts to test sharing.

Do not claim security certification or passing tests without running them. See THREATS.md and PROMPTS.md.
