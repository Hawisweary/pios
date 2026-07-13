-- PIOS derived index (pios.db)
-- Constitution Article 9: this entire database is a CACHE.
-- Sources of truth: events/*.jsonl, proposals/*.jsonl, vault/**/*.md (git).
-- `pios rebuild` must reproduce it exactly from those sources.

CREATE TABLE IF NOT EXISTS events (
  id          TEXT PRIMARY KEY,
  ts          TEXT NOT NULL,           -- ISO-8601
  kind        TEXT NOT NULL,           -- commit / paper_read / exercise / lecture /
                                       -- quiz / trade / journal / decision / idea /
                                       -- experiment / belief_revision / review_recall ...
  source      TEXT NOT NULL,           -- manual / github / zotero / broker / quiz ...
  entity_ids  TEXT NOT NULL DEFAULT '[]',  -- JSON array of entity ids
  depth       INTEGER,                 -- evidence depth 1-5 (epistemic ladder), NULL if n/a
  payload     TEXT NOT NULL DEFAULT '{}'   -- JSON
);
CREATE INDEX IF NOT EXISTS idx_events_ts   ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);

-- Entities: mirrors vault frontmatter. Types:
-- concept / paper / project / person / idea / decision / experiment /
-- milestone / skill / course / role_profile
CREATE TABLE IF NOT EXISTS entities (
  id    TEXT PRIMARY KEY,              -- e.g. concept:attention
  type  TEXT NOT NULL,
  name  TEXT NOT NULL,
  doc   TEXT,                          -- vault-relative path
  meta  TEXT NOT NULL DEFAULT '{}'     -- JSON (frontmatter mirror)
);

-- Edges: one graph, five views. Relations:
-- prerequisite_of / part_of / cites / applies / implements / motivated_by /
-- authored_by / influenced_by / informed_decision / superseded_by /
-- alternative_to / sparked_by / spawned
CREATE TABLE IF NOT EXISTS edges (
  src TEXT NOT NULL,
  dst TEXT NOT NULL,
  rel TEXT NOT NULL,
  PRIMARY KEY (src, dst, rel)
);

-- Proposals: AI suggestions + human verdicts. Facts (Article 3) —
-- source of truth is proposals/*.jsonl; this table is the queryable mirror.
CREATE TABLE IF NOT EXISTS proposals (
  id         TEXT PRIMARY KEY,
  ts         TEXT NOT NULL,
  kind       TEXT NOT NULL,            -- reschedule / new_topic / review_insert /
                                       -- merge_idea / exploration / decision_review_due
  rationale  TEXT NOT NULL,            -- reasoning chain
  diff       TEXT NOT NULL DEFAULT '{}',  -- proposed change (JSON)
  status     TEXT NOT NULL DEFAULT 'pending',  -- pending/accepted/rejected/expired
  decided_ts TEXT
);
