"""
Migración one-shot: crea las 4 tablas del motor estilométrico.
No toca las tablas existentes (job_history, tone_settings, document_history).

Ejecutar UNA sola vez desde la raíz del proyecto:
    python backend/migrate_add_style_tables.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gema.db")

TABLES = {
    "literary_dna": """
        CREATE TABLE IF NOT EXISTS literary_dna (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            author_name          TEXT NOT NULL,
            genre                TEXT NOT NULL,
            tone_name            TEXT NOT NULL,
            avg_sentence_length  REAL,
            adjective_ratio      REAL,
            lexical_richness     REAL,
            dialogue_ratio       REAL,
            preferred_patterns   TEXT
        )
    """,
    "style_profiles": """
        CREATE TABLE IF NOT EXISTS style_profiles (
            tone_name             TEXT PRIMARY KEY,
            style_display_name    TEXT,
            reference_author      TEXT,
            avg_sentence_len      INTEGER,
            max_sentence_len      INTEGER,
            adjective_density     REAL,
            dialogue_ratio        REAL,
            short_sentence_ratio  REAL,
            ttr_target            REAL,
            flesch_target         REAL,
            forbidden_words       TEXT,
            preferred_structures  TEXT,
            compound_replacements TEXT
        )
    """,
    "literary_thesaurus": """
        CREATE TABLE IF NOT EXISTS literary_thesaurus (
            id           TEXT PRIMARY KEY,
            tone_name    TEXT NOT NULL,
            source_lemma TEXT NOT NULL,
            target_word  TEXT NOT NULL,
            pos_tag      TEXT NOT NULL,
            intensity    TEXT,
            context_hint TEXT,
            priority     INTEGER DEFAULT 5
        )
    """,
    "prohibited_words": """
        CREATE TABLE IF NOT EXISTS prohibited_words (
            id         TEXT PRIMARY KEY,
            tone_name  TEXT NOT NULL,
            word       TEXT NOT NULL,
            reason     TEXT,
            suggestion TEXT
        )
    """,
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_dna_tone ON literary_dna (tone_name)",
    "CREATE INDEX IF NOT EXISTS idx_thesaurus_tone_lemma ON literary_thesaurus (tone_name, source_lemma)",
    "CREATE INDEX IF NOT EXISTS idx_prohibited_tone_word ON prohibited_words (tone_name, word)",
]

def run_migration():
    print(f"Base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for table_name, ddl in TABLES.items():
        cur.execute(ddl)
        print(f"  [OK] Tabla '{table_name}' lista.")

    for idx_sql in INDEXES:
        cur.execute(idx_sql)

    conn.commit()
    conn.close()
    print("\n[OK] Migracion completada. Las 4 tablas estilometricas estan listas.")

if __name__ == "__main__":
    run_migration()
