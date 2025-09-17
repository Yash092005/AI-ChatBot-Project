PRAGMA foreign_keys = ON;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT UNIQUE,
  locale TEXT,
  city TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  channel TEXT,
  started_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER,
  sender TEXT,
  text TEXT,
  ts TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE calc_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  inputs_json TEXT,
  result_lpd REAL,
  top_sources_json TEXT,
  ts TEXT DEFAULT (datetime('now'))
);

CREATE TABLE kb_docs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE,
  title TEXT,
  tags TEXT,
  body_md TEXT,
  lang TEXT DEFAULT 'en',
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE reminders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  type TEXT,
  cadence TEXT,
  next_run_at TEXT,
  payload_json TEXT
);

INSERT INTO users (uuid, locale, city) VALUES ('user-demo-1','en','Pune');
INSERT INTO sessions (user_id, channel) VALUES (1,'web');
