-- R Theory database — single source of truth for theorems + prose.
-- The website builds from this DB's exported feeds; a status change or prose
-- edit is made once, here, and propagates to every page that cites it.
--
-- Scope discipline (Kit's rule): every theorem carries one status code from
-- status_codes; the code is what the math has actually established.

PRAGMA journal_mode = WAL;

-- ---------------------------------------------------------------- status key
-- Canonical scope codes. Mirrors status_registry.json's key; the LEDGER
-- column is the theorem_ledger.md prose status each code maps to.
CREATE TABLE IF NOT EXISTS status_codes (
  code          TEXT PRIMARY KEY,   -- CP SC NC ST MA AX IN IC
  label         TEXT NOT NULL,      -- short human label
  meaning       TEXT NOT NULL,      -- full meaning, shown on the ledger page
  ledger_status TEXT                -- PROVED/CHECKED/STANDARD/MANUSCRIPT/AXIOM/INCOMPLETE/INVALID
);

-- ---------------------------------------------------------------- theorems
-- One row per audited claim. `id` is a stable slug shared with the site's
-- data-claim spans and the old status_registry.json ids.
CREATE TABLE IF NOT EXISTS theorems (
  id          TEXT PRIMARY KEY,
  book        INTEGER,              -- 0..6 (Volume I audit); NULL = cross-book
  section     TEXT,                 -- manuscript section, e.g. "Modules 2–5"
  label       TEXT,                 -- manuscript label, e.g. "2.VII.T1"
  statement   TEXT NOT NULL,        -- the claim, plain text
  status_code TEXT NOT NULL REFERENCES status_codes(code),
  evidence    TEXT,                 -- scripts/logs/tolerances backing the status
  source      TEXT,                 -- 'theorem_ledger.md' | 'manual' | ...
  version     INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL,
  notes       TEXT
);

-- Theorem dependency DAG (mirrors DEPENDENCY_CHAIN.md at row granularity).
CREATE TABLE IF NOT EXISTS theorem_deps (
  theorem_id  TEXT NOT NULL REFERENCES theorems(id) ON DELETE CASCADE,
  depends_on  TEXT NOT NULL REFERENCES theorems(id) ON DELETE CASCADE,
  kind        TEXT,                 -- uses | corroborates | refutes | supersedes
  PRIMARY KEY (theorem_id, depends_on)
);

-- ---------------------------------------------------------------- prose
-- Editorial content blocks that feed the website. A page section is built by
-- assembling prose rows for its page+section; edit once here, rebuild site.
CREATE TABLE IF NOT EXISTS prose (
  id          TEXT PRIMARY KEY,     -- slug, e.g. 'book2-spine-summary'
  title       TEXT NOT NULL,
  page        TEXT,                 -- site page fed, e.g. 'book2'
  section     TEXT,                 -- anchor/section within the page
  body        TEXT NOT NULL,        -- markdown source
  audience    TEXT NOT NULL DEFAULT 'intuition-first',
  status      TEXT NOT NULL DEFAULT 'draft',  -- draft | review | live
  version     INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);

-- Which theorems a prose block cites (rendered as status pills on the page).
CREATE TABLE IF NOT EXISTS prose_theorems (
  prose_id    TEXT NOT NULL REFERENCES prose(id) ON DELETE CASCADE,
  theorem_id  TEXT NOT NULL REFERENCES theorems(id) ON DELETE CASCADE,
  PRIMARY KEY (prose_id, theorem_id)
);

-- ---------------------------------------------------------------- notation
-- Centralized notation/terms so symbol changes propagate like prose.
CREATE TABLE IF NOT EXISTS terms (
  slug        TEXT PRIMARY KEY,
  symbol      TEXT,
  definition  TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'live',
  version     INTEGER NOT NULL DEFAULT 1,
  updated_at  TEXT NOT NULL
);

-- ---------------------------------------------------------------- prose chunks
-- Text extracted from the site pages, chunked with pgai's
-- ai.chunking_recursive_character_text_splitter (vendored in
-- vendor/pgai_chunking.py). Finer granularity than `prose`; prose_id links
-- a chunk to its section row once the prose table is populated.
CREATE TABLE IF NOT EXISTS prose_chunks (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  page        TEXT NOT NULL,        -- e.g. 'book2'
  chunk_index INTEGER NOT NULL,
  body        TEXT NOT NULL,
  char_start  INTEGER,              -- offset in the page's extracted text
  char_end    INTEGER,
  chunker     TEXT NOT NULL DEFAULT 'ai.chunking_recursive_character_text_splitter',
  chunk_size  INTEGER NOT NULL,
  chunk_overlap INTEGER NOT NULL,
  prose_id    TEXT REFERENCES prose(id),
  created_at  TEXT NOT NULL,
  UNIQUE (page, chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_prose_chunks_page ON prose_chunks(page);

-- ---------------------------------------------------------------- desmos graphs
-- Every live Desmos calculator embedded in the site: what it shows (the
-- LaTeX expressions = the actual graph content), its fallback image, its
-- figure caption, and where it belongs in the prose (section anchor +
-- the prose chunk containing its figure heading).
CREATE TABLE IF NOT EXISTS desmos_graphs (
  id             TEXT PRIMARY KEY,   -- e.g. 'book2-d1'
  page           TEXT NOT NULL,      -- e.g. 'book2'
  graph_id       TEXT NOT NULL,      -- mount div id, e.g. 'd1'
  fallback_id    TEXT,               -- e.g. 'f1'
  fallback_src   TEXT,               -- e.g. 'graphs/b2_quartet.png'
  fallback_alt   TEXT,
  figure_title   TEXT,               -- h3 text, e.g. 'Figure 1 — ...'
  figure_anchor  TEXT,               -- h3 id
  section        TEXT,               -- nearest preceding h2
  caption        TEXT,               -- plain-text caption
  viewport       TEXT,               -- JSON {left,right,bottom,top}
  expressions    TEXT,               -- JSON [{latex,color,...}] (the Desmos content)
  prose_chunk_id INTEGER REFERENCES prose_chunks(id),
  created_at     TEXT NOT NULL,
  UNIQUE (page, graph_id)
);
CREATE INDEX IF NOT EXISTS idx_desmos_page ON desmos_graphs(page);

-- ---------------------------------------------------------------- embeddings
-- Dense vectors for the prose chunks, computed by Ollama's embedding model
-- on Toetop (see embed_chunks_toetop.py). Vector stored as float32 bytes.
CREATE TABLE IF NOT EXISTS embeddings (
  chunk_id   INTEGER PRIMARY KEY REFERENCES prose_chunks(id),
  model      TEXT NOT NULL,      -- e.g. 'nomic-embed-text'
  dims       INTEGER NOT NULL,   -- e.g. 768
  vector     BLOB NOT NULL,      -- dims float32, little-endian
  created_at TEXT NOT NULL
);

-- Section-level vectors (prose rows from extract_sections.py), same model.
CREATE TABLE IF NOT EXISTS prose_embeddings (
  prose_id   TEXT PRIMARY KEY REFERENCES prose(id) ON DELETE CASCADE,
  model      TEXT NOT NULL,
  dims       INTEGER NOT NULL,
  vector     BLOB NOT NULL,      -- dims float32, little-endian
  created_at TEXT NOT NULL
);

-- ---------------------------------------------------------------- audit log
CREATE TABLE IF NOT EXISTS changelog (
  seq         INTEGER PRIMARY KEY AUTOINCREMENT,
  at          TEXT NOT NULL,
  actor       TEXT NOT NULL,
  table_name  TEXT NOT NULL,
  row_id      TEXT NOT NULL,
  action      TEXT NOT NULL,        -- insert | update | status-change
  detail      TEXT
);

-- Views the site build consumes directly.
CREATE VIEW IF NOT EXISTS v_theorems AS
SELECT t.id, t.book, t.section, t.label, t.statement,
       t.status_code AS code, c.label AS code_label, c.meaning AS code_meaning,
       c.ledger_status, t.evidence, t.source, t.version, t.updated_at, t.notes
FROM theorems t JOIN status_codes c ON c.code = t.status_code;

CREATE VIEW IF NOT EXISTS v_prose_live AS
SELECT id, title, page, section, body, audience, version, updated_at
FROM prose WHERE status = 'live';
