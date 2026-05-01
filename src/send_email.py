"""
send_email.py
Sends the HTML digest as a rich HTML email via Gmail SMTP.
Uses Gmail App Password (not your main account password).
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone

GMAIL_USER     = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "")
RECIPIENT      = os.environ.get("DIGEST_RECIPIENT", "vignesh.bhaskarraj@gmail.com")


def send_digest(html_content: str, session_label: str = "Morning"):
    """Send the HTML digest email."""

    if not GMAIL_USER or not GMAIL_APP_PASS:
        print("[Email] Gmail credentials not set — skipping email send.")
        return False

    now      = datetime.now(timezone.utc)
    date_str = now.strftime("%b %d, %Y")
    emoji    = "🌅" if session_label == "Morning" else "🌆"
    subject  = f"{emoji} AI Digest — {session_label} Edition · {date_str}"

    # Plain text fallback
    plain = (
        f"AI Digest — {session_label} Edition\n"
        f"{date_str}\n\n"
        "Open this email in an HTML-capable client to view the full digest.\n\n"
        "Or view the live dashboard: https://vigneshbhaskarraj.github.io/ai-digest\n"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"AI Digest <{GMAIL_USER}>"
    msg["To"]      = RECIPIENT

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())
        print(f"[Email] Sent {session_label} digest to {RECIPIENT}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send: {e}")
        return False


if __name__ == "__main__":
    # Quick test — sends a plain test email
    test_html = "<html><body><h1>Test Digest</h1><p>Email delivery is working.</p></body></html>"
    send_digest(test_html, "Morning")
