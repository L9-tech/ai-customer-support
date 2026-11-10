"""Hostinger adapter. Reading never changes Seen; database owns processing status."""
import hashlib
import imaplib
import re
import smtplib
import ssl
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import parseaddr, make_msgid, formatdate
from html.parser import HTMLParser
from app.models import Incoming

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
        if tag in ('br', 'p', 'div', 'li'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def parse_message(raw: bytes, key: str) -> Incoming:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    part = message.get_body(preferencelist=('plain', 'html'))
    body = ''
    if part:
        body = part.get_content()
        if not isinstance(body, str): body = body.decode('utf-8', errors='replace')
        if part.get_content_type() == 'text/html':
            parser = TextOnly(); parser.feed(body); body = ''.join(parser.parts)
    ids = re.findall(r'<[^<>\s]+>', str(message.get('References', '')) + ' ' + str(message.get('In-Reply-To', '')))
    msgid = re.findall(r'<[^<>\s]+>', str(message.get('Message-ID', '')))
    sender = parseaddr(str(message.get('From', '')))[1].lower()
    automatic = str(message.get('Auto-Submitted', 'no')).lower() != 'no' or bool(message.get('List-Id')) or str(message.get('Precedence', '')).lower() in ('bulk', 'list', 'junk')
    automatic = automatic or sender.split('@')[0] in ('mailer-daemon', 'postmaster', 'no-reply', 'noreply')
    return Incoming(key, sender, str(message.get('Subject', 'Geen onderwerp')), body[:24000], msgid[0] if msgid else '', list(dict.fromkeys(ids)), any(p.get_content_disposition() == 'attachment' for p in message.walk()), automatic, str(message.get('Date', '')))

class HostingerMail:
    def __init__(self, settings): self.settings = settings; self.mail = None
    def __enter__(self):
        s = self.settings
        self.mail = imaplib.IMAP4_SSL(s.imap_host, s.imap_port, ssl_context=ssl.create_default_context(), timeout=20)
        try:
            self.mail.login(s.email_username, s.email_password)
            status, _ = self.mail.select(s.imap_folder, readonly=True)
            if status != 'OK': raise RuntimeError('INBOX selecteren mislukt')
            _, values = self.mail.response('UIDVALIDITY')
            if not values or not values[0]: raise RuntimeError('UIDVALIDITY ontbreekt')
            self.validity = values[0].decode('ascii')
            account = hashlib.sha256(s.email_username.lower().encode()).hexdigest()[:20]
            self.prefix = f'{account}:{s.imap_folder}:{self.validity}:'
            return self
        except Exception:
            self.__exit__(None, None, None); raise
    def __exit__(self, *args):
        if self.mail:
            try: self.mail.logout()
            except Exception: pass
    def identifiers(self):
        status, data = self.mail.uid('SEARCH', None, 'ALL')
        if status != 'OK': raise RuntimeError('Zoeken mislukt')
        return (data[0] or b'').split() if data else []
    def key(self, uid): return self.prefix + uid.decode('ascii')
    def get_message(self, uid):
        status, size_data = self.mail.uid('FETCH', uid, '(RFC822.SIZE)')
        size = re.search(rb'RFC822.SIZE\s+(\d+)', b' '.join(x for x in size_data or [] if isinstance(x, bytes)))
        if status != 'OK' or not size: raise RuntimeError('Berichtgrootte ontbreekt')
        if int(size[1]) > self.settings.max_message_bytes: raise ValueError('message_too_large')
        status, parts = self.mail.uid('FETCH', uid, '(BODY.PEEK[])')
        if status != 'OK': raise RuntimeError('Bericht ophalen mislukt')
        raw = next((p[1] for p in parts if isinstance(p, tuple) and isinstance(p[1], bytes)), None)
        if raw is None: raise ValueError('message_body_missing')
        return parse_message(raw, self.key(uid))
    def send_reply(self, incoming, text, outgoing_id):
        s = self.settings
        if s.app_mode != 'live' or not s.enable_sending: raise RuntimeError('Verzenden staat uit')
        recipient = incoming['sender']
        if not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+', recipient): raise ValueError('Ongeldig adres')
        msg = EmailMessage()
        msg['From'] = s.email_username; msg['To'] = recipient
        msg['Subject'] = 'Re: ' + incoming['subject'].replace('\r', '').replace('\n', '')[:200]
        msg['Date'] = formatdate(localtime=False); msg['Message-ID'] = outgoing_id
        msg['Auto-Submitted'] = 'auto-replied'
        if incoming['message_id']:
            msg['In-Reply-To'] = incoming['message_id']
            msg['References'] = ' '.join(incoming['references'][-15:] + [incoming['message_id']])
        msg.set_content(text)
        with smtplib.SMTP_SSL(s.smtp_host, s.smtp_port, context=ssl.create_default_context(), timeout=25) as smtp:
            smtp.login(s.email_username, s.email_password)
            refused = smtp.send_message(msg)
            if refused: raise RuntimeError('Ontvanger geweigerd')
        # SMTP success is authoritative. A Sent-copy failure must never resend mail.
        warning = ''
        try:
            with imaplib.IMAP4_SSL(s.imap_host, s.imap_port, ssl_context=ssl.create_default_context(), timeout=20) as mailbox:
                mailbox.login(s.email_username, s.email_password)
                status, _ = mailbox.append(s.imap_sent_folder, '\\Seen', None, msg.as_bytes())
                if status != 'OK': warning = 'Verstuurd; kopie in Sent mislukt'
        except Exception: warning = 'Verstuurd; kopie in Sent mislukt'
        return warning
