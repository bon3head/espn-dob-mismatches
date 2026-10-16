CREATE TABLE players (
  player_key TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  league     TEXT NOT NULL,
  espn_id    TEXT,
  nba_id     TEXT,
  bbref_slug TEXT,
  qid        TEXT
);
CREATE TABLE dob_claims (
  claim_id     INTEGER PRIMARY KEY,
  player_key   TEXT NOT NULL REFERENCES players(player_key),
  source       TEXT NOT NULL,
  dob          TEXT NOT NULL,
  retrieved_at TEXT,
  note         TEXT
);
CREATE TABLE mismatch_verdicts (
  player_key       TEXT PRIMARY KEY REFERENCES players(player_key),
  espn_dob         TEXT,
  disputant_dob    TEXT,
  disputant        TEXT,
  difference_class TEXT,
  verdict          TEXT NOT NULL,
  correct_dob      TEXT,
  confidence       TEXT,
  notes            TEXT
);
CREATE TABLE scans (
  scan_id          TEXT PRIMARY KEY,
  name             TEXT,
  ran_at           TEXT,
  players_scanned  INTEGER,
  mismatches_found INTEGER,
  method           TEXT
);
