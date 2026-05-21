"""
Migración one-shot: agrega la columna 'status' a job_history.
Los registros existentes quedan con status='completed' para mantener consistencia.
Ejecutar UNA sola vez desde la raíz del proyecto:
    python backend/migrate_add_status.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "gema.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Inspeccionamos el esquema actual
cur.execute("PRAGMA table_info(job_history)")
cols = [row[1] for row in cur.fetchall()]
print(f"Columnas actuales en job_history: {cols}")

if "status" not in cols:
    # DEFAULT 'completed' para que los registros históricos no queden como 'pending'
    cur.execute("ALTER TABLE job_history ADD COLUMN status TEXT DEFAULT 'completed'")
    conn.commit()
    print("OK: columna 'status' agregada con DEFAULT 'completed' para registros históricos.")
else:
    print("INFO: columna 'status' ya existe — nada que hacer.")

conn.close()
print("Migración finalizada.")
