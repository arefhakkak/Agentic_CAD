# schema_ultra_combo.py
from __future__ import annotations
import os, sqlite3

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- Minimal doc table for scraped CATIA documentation
CREATE TABLE IF NOT EXISTS doc_functions_ultramin (
  function_key   TEXT PRIMARY KEY,   -- e.g., hybridshapefactory.addnewplaneoffset
  api_factory    TEXT NOT NULL,      -- e.g., HybridShapeFactory
  api_method     TEXT NOT NULL,      -- e.g., AddNewPlaneOffset
  action_label   TEXT NOT NULL,      -- e.g., create_plane_offset  (normalized from method)
  doc_url        TEXT,               -- full URL of the page where it was seen
  tokens_json    TEXT NOT NULL       -- JSON array of tokens for matching (factory+method tokens)
);

-- Minimal harvested steps from PDFs (what LLM needs to generate code)
CREATE TABLE IF NOT EXISTS harvested_steps_ultramin (
  step_id        INTEGER PRIMARY KEY,     -- execution order
  action_label   TEXT NOT NULL,           -- normalized function (create_plane_offset, create_spline_through_points, ...)
  description    TEXT NOT NULL,           -- concise description
  params_json    TEXT NOT NULL,           -- parameters and values
  produces_json  TEXT,                    -- features created (dependency roots)
  references_json TEXT,                   -- features/axes/planes referenced (dependencies)
  code_lang      TEXT,                    -- reserved for later (e.g., python-catia)
  generated_code TEXT                     -- to be filled by LLM later
);
"""

def init_db(db_path: str, overwrite: bool=False) -> sqlite3.Connection:
    if overwrite and os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    return conn
