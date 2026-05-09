"""
send_email.py
NOT ACTIVE — email delivery is intentionally skipped for now.
The digest is consumed via the live GitHub Pages URL and PWA install.

Future: wire into main.py / india_main.py / tn_main.py when needed.
Credentials required (GitHub Actions secrets):
  GMAIL_USER        — sender Gmail address
  GMAIL_APP_PASS    — Gmail App Password (not account password)
  DIGEST_RECIPIENT  — recipient email address
"""


def send_digest(html_content: str, session_label: str = "Morning") -> bool:
    """Stub — returns False without sending anything."""
    print("[Email] Delivery disabled — see send_email.py for re-activation steps.")
    return False
