import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

def now(): return datetime.now(timezone.utc).isoformat()
def ident(): return str(uuid.uuid4())

SCHEMA = [
'''CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, sender TEXT NOT NULL, subject TEXT NOT NULL, state TEXT NOT NULL, category TEXT NOT NULL DEFAULT '', draft TEXT NOT NULL DEFAULT '', reason TEXT NOT NULL DEFAULT '', proposed_action TEXT NOT NULL DEFAULT '', sources TEXT NOT NULL DEFAULT '[]', version INTEGER NOT NULL DEFAULT 0, latest_key TEXT NOT NULL, updated_at TEXT NOT NULL)''',
'''CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, ticket_id TEXT NOT NULL REFERENCES tickets(id), source_key TEXT NOT NULL UNIQUE, direction TEXT NOT NULL, sender TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL, message_id TEXT NOT NULL, refs TEXT NOT NULL DEFAULT '[]', attachments INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)''',
'''CREATE TABLE IF NOT EXISTS events (source_key TEXT PRIMARY KEY, state TEXT NOT NULL, attempts INTEGER NOT NULL, error TEXT NOT NULL DEFAULT '', ticket_id TEXT, input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0, engine TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''',
'''CREATE TABLE IF NOT EXISTS knowledge_base (id TEXT PRIMARY KEY, section TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL)''',
'''CREATE TABLE IF NOT EXISTS audit (id TEXT PRIMARY KEY, ticket_id TEXT, action TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL)''',
'''CREATE TABLE IF NOT EXISTS mailbox_baselines (prefix TEXT PRIMARY KEY, start_uid BIGINT NOT NULL, created_at TEXT NOT NULL)''',
'''CREATE INDEX IF NOT EXISTS messages_thread ON messages(ticket_id,created_at)''',
'''CREATE INDEX IF NOT EXISTS messages_reference ON messages(message_id)'''
]
class Database:
    def __init__(self, url):
        self.url = url; self.sqlite = url.startswith('sqlite:///')
    @contextmanager
    def connection(self):
        if self.sqlite:
            path = Path(self.url.removeprefix('sqlite:///')); path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys=ON'); conn.execute('PRAGMA journal_mode=WAL'); conn.execute('BEGIN IMMEDIATE')
        else:
            import psycopg
            from psycopg.rows import dict_row
            conn = psycopg.connect(self.url, row_factory=dict_row, connect_timeout=15)
        try:
            yield conn; conn.commit()
        except Exception:
            conn.rollback(); raise
        finally: conn.close()
    def execute(self, c, sql, args=()): return c.execute(sql if self.sqlite else sql.replace('?', '%s'), args)
    def init(self):
        with self.connection() as c:
            for statement in SCHEMA: self.execute(c, statement)
            if not self.sqlite:
                for table in ['tickets','messages','events','knowledge_base','audit','mailbox_baselines']:
                    self.execute(c, f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
    def all(self, sql, args=()):
        with self.connection() as c: return [dict(r) for r in self.execute(c, sql, args).fetchall()]
    def one(self, sql, args=()):
        rows = self.all(sql, args); return rows[0] if rows else None
    def audit(self, ticket, action, detail):
        with self.connection() as c:self.execute(c, 'INSERT INTO audit VALUES (?,?,?,?,?)', (ident(),ticket,action,detail,now()))
    def mailbox_baseline(self, prefix, identifiers):
        """Keep the initial UID boundary; restarts never silently import old mail."""
        latest=max((int(uid) for uid in identifiers), default=0)
        with self.connection() as c:
            created=self.execute(c, 'INSERT INTO mailbox_baselines VALUES (?,?,?) ON CONFLICT(prefix) DO NOTHING RETURNING prefix', (prefix,latest,now())).fetchone()
            row=self.execute(c, 'SELECT start_uid FROM mailbox_baselines WHERE prefix=?', (prefix,)).fetchone()
            return int(row['start_uid']), created is not None
    def handled(self, key):
        row = self.one('SELECT state, attempts FROM events WHERE source_key=?', (key,))
        return bool(row and (row['state'] != 'failed' or row['attempts'] >= 3))
    def claim(self, key):
        stamp=now()
        with self.connection() as c:
            return self.execute(c, '''INSERT INTO events (source_key,state,attempts,created_at,updated_at) VALUES (?,'processing',1,?,?) ON CONFLICT(source_key) DO UPDATE SET state='processing', attempts=events.attempts+1, error='',updated_at=excluded.updated_at WHERE events.state='failed' AND events.attempts<3 RETURNING source_key''', (key,stamp,stamp)).fetchone() is not None
    def finish(self, key, state, ticket=None, decision=None, error=''):
        with self.connection() as c:
            self.execute(c, 'UPDATE events SET state=?,ticket_id=?,error=?,input_tokens=?,output_tokens=?,engine=?,updated_at=? WHERE source_key=?', (state,ticket,error,getattr(decision,'input_tokens',0),getattr(decision,'output_tokens',0),getattr(decision,'engine',''),now(),key))
    def ingest(self, message):
        with self.connection() as c:
            old = self.execute(c, 'SELECT ticket_id FROM messages WHERE source_key=?',(message.key,)).fetchone()
            if old:return old['ticket_id']
            ticket=None
            for ref in reversed(message.references):
                row=self.execute(c,'SELECT t.id FROM tickets t JOIN messages m ON m.ticket_id=t.id WHERE m.message_id=? AND t.sender=?',(ref,message.sender)).fetchone()
                if row:ticket=row['id'];break
            stamp=now()
            if ticket is None:
                ticket=ident();self.execute(c, 'INSERT INTO tickets (id,sender,subject,state,latest_key,updated_at) VALUES (?,?,?,?,?,?)',(ticket,message.sender,message.subject,'processing',message.key,stamp))
            else:
                self.execute(c,"UPDATE tickets SET latest_key=?,version=version+1,updated_at=?,draft='',state=CASE WHEN state IN ('escalated','sending','delivery_unknown') THEN state ELSE 'processing' END WHERE id=?",(message.key,stamp,ticket))
            self.execute(c,'INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?)',(ident(),ticket,message.key,'in',message.sender,message.subject,message.body,message.message_id,json.dumps(message.references),int(message.attachments),stamp))
            return ticket
    def decide(self, ticket, source_key, d):
        with self.connection() as c:
            self.execute(c,"UPDATE tickets SET state=?,category=?,draft=?,reason=?,proposed_action=?,sources=?,version=version+1,updated_at=? WHERE id=? AND latest_key=? AND state NOT IN ('sending','delivery_unknown')",(d.state,d.category,d.draft,d.reason,d.proposed_action,json.dumps(d.sources),now(),ticket,source_key))
    def ticket(self, id):return self.one('SELECT * FROM tickets WHERE id=?',(id,))
    def messages(self, id):return self.all('SELECT * FROM messages WHERE ticket_id=? ORDER BY created_at,id',(id,))
    def latest(self, ticket):
        row=self.one('SELECT * FROM messages WHERE source_key=?',(ticket['latest_key'],))
        row['references']=json.loads(row.pop('refs'));return row
    def edit(self, id, text, version):
        with self.connection() as c:
            row=self.execute(c,"UPDATE tickets SET draft=?,version=version+1,updated_at=? WHERE id=? AND version=? AND state IN ('review','escalated') RETURNING *",(text,now(),id,version)).fetchone()
            return dict(row) if row else None
    def claim_send(self,id,version):
        with self.connection() as c:
            row=self.execute(c,"UPDATE tickets SET state='sending',version=version+1,updated_at=? WHERE id=? AND version=? AND state IN ('review','escalated') AND draft<>'' RETURNING *",(now(),id,version)).fetchone()
            return dict(row) if row else None
    def sent(self,ticket,outid,warning,sender):
        with self.connection() as c:
            self.execute(c,"UPDATE tickets SET state=CASE WHEN latest_key=? THEN 'sent' ELSE 'escalated' END,reason=?,updated_at=? WHERE id=?",(ticket['latest_key'],warning or 'Antwoord verstuurd. Controleer eventuele nieuw binnengekomen berichten.',now(),ticket['id']))
            self.execute(c,'INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?)',(ident(),ticket['id'],outid,'out',sender,'Re: '+ticket['subject'],ticket['draft'],outid,'[]',0,now()))
    def delivery_unknown(self,id):
        with self.connection() as c:self.execute(c,"UPDATE tickets SET state='delivery_unknown',reason=?,updated_at=? WHERE id=?",('SMTP resultaat onzeker. Controleer de mailbox voordat je opnieuw handelt.',now(),id))
    def seed(self, entries):
        with self.connection() as c:
            for e in entries:self.execute(c,'INSERT INTO knowledge_base (id,section,title,content,updated_at) VALUES (?,?,?,?,?) ON CONFLICT(id) DO NOTHING',(e['id'],e['section'],e['title'],e['content'],now()))
    def knowledge(self):return self.all('SELECT * FROM knowledge_base ORDER BY section,title')
    def update_entry(self,id,title,content,revision):
        with self.connection() as c:
            row=self.execute(c,'UPDATE knowledge_base SET title=?,content=?,revision=revision+1,updated_at=? WHERE id=? AND revision=? RETURNING *',(title,content,now(),id,revision)).fetchone()
            return dict(row) if row else None
