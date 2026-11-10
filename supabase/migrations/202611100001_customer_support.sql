-- Project schema. Apply with a migration owner on your own PostgreSQL database.
CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, sender TEXT NOT NULL, subject TEXT NOT NULL, state TEXT NOT NULL, category TEXT NOT NULL DEFAULT '', draft TEXT NOT NULL DEFAULT '', reason TEXT NOT NULL DEFAULT '', proposed_action TEXT NOT NULL DEFAULT '', sources TEXT NOT NULL DEFAULT '[]', version INTEGER NOT NULL DEFAULT 0, latest_key TEXT NOT NULL, updated_at TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, ticket_id TEXT NOT NULL REFERENCES tickets(id), source_key TEXT NOT NULL UNIQUE, direction TEXT NOT NULL, sender TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL, message_id TEXT NOT NULL, refs TEXT NOT NULL DEFAULT '[]', attachments INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS events (source_key TEXT PRIMARY KEY, state TEXT NOT NULL, attempts INTEGER NOT NULL, error TEXT NOT NULL DEFAULT '', ticket_id TEXT, input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0, engine TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS knowledge_base (id TEXT PRIMARY KEY, section TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS audit (id TEXT PRIMARY KEY, ticket_id TEXT, action TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL);

CREATE INDEX IF NOT EXISTS messages_thread ON messages(ticket_id,created_at);

CREATE INDEX IF NOT EXISTS messages_reference ON messages(message_id);

ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit ENABLE ROW LEVEL SECURITY;
