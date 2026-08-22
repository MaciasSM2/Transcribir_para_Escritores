import os
import sqlite3
import re

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DB_PATH = os.path.join(BACKEND_DIR, "gema.db")

def fix_database_tildes():
    """Corrige C2: Sincroniza las tildes en la base de datos existente."""
    if not os.path.exists(DB_PATH):
        print("[AVISO] No se encontro gema.db en backend/. Saltando...")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lista de correcciones de nombres de tonos para resolver el problema de las tildes
    correcciones = [
        ("Narrativa de Ciencia Ficcion y Fantasia Epica", "Narrativa de Ciencia Ficción y Fantasía Épica"),
        ("Romance Contemporaneo", "Romance Contemporáneo")
    ]
    
    for incorrecto, correcto in correcciones:
        # Se actualizan todas las tablas que utilicen tone_name
        print(f"[*] Corrigiendo de '{incorrecto}' a '{correcto}'...")
        cursor.execute("UPDATE style_profiles SET tone_name = ? WHERE tone_name = ?", (correcto, incorrecto))
        cursor.execute("UPDATE literary_thesaurus SET tone_name = ? WHERE tone_name = ?", (correcto, incorrecto))
        cursor.execute("UPDATE prohibited_words SET tone_name = ? WHERE tone_name = ?", (correcto, incorrecto))
        cursor.execute("UPDATE literary_dna SET tone_name = ? WHERE tone_name = ?", (correcto, incorrecto))
    
    conn.commit()
    conn.close()
    print("[OK] C2: Tildes corregidas en la base de datos (tablas: style_profiles, literary_thesaurus, prohibited_words, literary_dna).")

def patch_vosk_worker():
    """Corrige C1: Evita el error silencioso de importación."""
    worker_path = os.path.join(BACKEND_DIR, "services", "transcription", "vosk_worker.py")
    if not os.path.exists(worker_path):
        print("[AVISO] No se encontro vosk_worker.py. Saltando...")
        return
        
    with open(worker_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    old_code = "except ImportError:\n    pass"
    new_code = "except ImportError:\n    raise ImportError('Vosk no esta instalado. Ejecuta: pip install vosk')"
    
    if old_code in content:
        with open(worker_path, "w", encoding="utf-8") as f:
            f.write(content.replace(old_code, new_code))
        print("[OK] C1: Importacion de Vosk ahora es segura en vosk_worker.py.")
    else:
        print("[OK] C1: vosk_worker.py ya tenia la excepcion de importacion corregida.")

def fix_nlp_capitalization():
    """Corrige M2: Capitalización por oraciones en nlp_processor.py."""
    nlp_path = os.path.join(BACKEND_DIR, "nlp_processor.py")
    if not os.path.exists(nlp_path):
        print("[AVISO] No se encontro nlp_processor.py. Saltando...")
        return
        
    with open(nlp_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Si ya contiene la capitalización de oraciones, evitamos duplicarlo o corromper el archivo.
    if "(?<=[.!?])" in content or "M2: Capitalizar cada oracion" in content or "M2: Capitalizar cada oración" in content:
        print("[OK] M2: Capitalizacion ya estaba corregida por oraciones en nlp_processor.py.")
        return

    # Regex para detectar el bloque de capitalización viejo
    old_cap = r"if len\(corrected_text\) > 0:\n\s+corrected_text = corrected_text\[0\].upper\(\) \+ corrected_text\[1:\]"
    new_cap = "import re\n        # M2: Capitalizar cada oracion\n        corrected_text = re.sub(r'(?<=[.!?])\\s*\\w', lambda m: m.group(0).upper(), corrected_text)\n        if corrected_text: corrected_text = corrected_text[0].upper() + corrected_text[1:]"
    
    updated_content = re.sub(old_cap, new_cap, content)
    with open(nlp_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print("[OK] M2: Capitalizacion corregida (ahora por oraciones).")

if __name__ == "__main__":
    print("[START] Iniciando saneamiento de Gema...")
    fix_database_tildes()
    patch_vosk_worker()
    fix_nlp_capitalization()
    print("[SUCCESS] Saneamiento del backend completado con exito.")
