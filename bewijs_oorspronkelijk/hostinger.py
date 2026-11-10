import imaplib
import ssl 
from config import settings

mail = settings.email_username
password = settings.email_password
imap_host = settings.imap_host
imap_port = settings.imap_port

context = ssl.create_default_context()

with imaplib.IMAP4_SSL(
    imap_host,
    imap_port,
    ssl_context=context
) as mailinbox:
    mailinbox.login(mail, password)
    status, messages = mailinbox.select("INBOX", readonly=True)
    if status != "OK":
        raise RuntimeError("Failed to select INBOX")
    print(f"Selected INBOX with {messages[0]} messages")
    bericht = mailinbox.uid("SEARCH", None, "ALL")
    if bericht[0] != "OK":
        raise RuntimeError("Failed to search INBOX")
    print(bericht)
    for uid in bericht[1][0].split():
        print(f"Message UID: {uid.decode()}")
        

