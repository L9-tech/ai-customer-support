import imaplib
import os
import smtplib
import ssl

from dotenv import load_dotenv

load_dotenv()

username = os.environ["EMAIL_USERNAME"]
password = os.environ["EMAIL_PASSWORD"]

context = ssl.create_default_context()

with imaplib.IMAP4_SSL(
    os.environ["IMAP_HOST"],
    int(os.environ["IMAP_PORT"]),
    ssl_context=context,
    timeout=20,
) as mailbox:
    mailbox.login(username, password)
    status, _ = mailbox.select("INBOX", readonly=True)
    if status != "OK":
        raise RuntimeError("De inbox kon niet worden geopend.")
    print("IMAP werkt: inloggen en inbox openen gelukt.")


# Controleer de SMTP-login zonder een e-mail te versturen.
with smtplib.SMTP_SSL(
    os.environ["SMTP_HOST"],
    int(os.environ["SMTP_PORT"]),
    context=context,
    timeout=20,
) as server:
    server.login(username, password)
    print("SMTP werkt: inloggen gelukt.")