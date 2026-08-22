"""
Migración one-shot: actualiza nombres de tono en DB de versión sin acentos a versión con acentos,
para coincidir con los schemas Pydantic y el frontend.

Ejecutar desde la raiz del proyecto:
    python backend/migrate_fix_tone_accents.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gema.db")

TONE_MAP = {
    "Narrativa de Ciencia Ficcion y Fantasia Epica": "Narrativa de Ciencia Ficción y Fantasía Épica",
    "Romance Contemporaneo": "Romance Contemporáneo",
    "No Ficcion Academica": "No Ficción Académica",
}

TABLES_AND_COLUMNS = [
    ("literary_dna", "tone_name"),
    ("style_profiles", "tone_name"),
    ("literary_thesaurus", "tone_name"),
    ("prohibited_words", "tone_name"),
    ("document_history", "tone_name"),
    ("tone_settings", "tone_name"),
]

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"[INFO] No se encontró DB en {DB_PATH}. Nada que migrar.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    total_updates = 0

    for table, column in TABLES_AND_COLUMNS:
        for old_name, new_name in TONE_MAP.items():
            cur.execute(f"UPDATE {table} SET {column} = ? WHERE {column} = ?", (new_name, old_name))
            affected = cur.rowcount
            if affected > 0:
                print(f"  [OK] {table}.{column}: '{old_name}' → '{new_name}' ({affected} filas)")
                total_updates += affected

    conn.commit()
    conn.close()

    if total_updates > 0:
        print(f"\n[OK] Migración completada. {total_updates} registros actualizados.")
    else:
        print(f"\n[INFO] No se encontraron registros sin acentos. La DB ya está actualizada.")

if __name__ == "__main__":
    run_migration()
