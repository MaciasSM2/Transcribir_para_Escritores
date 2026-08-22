"""
Seed one-shot: puebla literary_thesaurus y prohibited_words para los 4 tonos.
Tesauro organizado por LEMA (forma infinitiva/base), no por forma flexionada.

Ejecutar UNA sola vez desde la raiz del proyecto:
    python backend/scripts/seed_thesaurus.py
"""
import sqlite3
import uuid
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gema.db")

# ---------------------------------------------------------------------------
# TESAURO: (tone_name, source_lemma, target_word, pos_tag, intensity, context, priority)
# ---------------------------------------------------------------------------

THESAURUS_ENTRIES = [

    # ── MISTERIO Y THRILLER (Chandler / Noir) ──────────────────────────────
    ("Misterio y Thriller", "caminar",   "acechar",          "VERB", "poetico",  "accion",      9),
    ("Misterio y Thriller", "caminar",   "deslizarse",       "VERB", "poetico",  "descripcion", 7),
    ("Misterio y Thriller", "decir",     "murmurar",         "VERB", "poetico",  "dialogo",     9),
    ("Misterio y Thriller", "decir",     "mascullar",        "VERB", "neutro",   "dialogo",     7),
    ("Misterio y Thriller", "ver",       "vislumbrar",       "VERB", "poetico",  "descripcion", 8),
    ("Misterio y Thriller", "ver",       "detectar",         "VERB", "tecnico",  "accion",      6),
    ("Misterio y Thriller", "mirar",     "escrutar",         "VERB", "poetico",  "descripcion", 8),
    ("Misterio y Thriller", "correr",    "precipitarse",     "VERB", "poetico",  "accion",      7),
    ("Misterio y Thriller", "golpear",   "asestar",          "VERB", "poetico",  "accion",      8),
    ("Misterio y Thriller", "grande",    "imponente",        "ADJ",  "poetico",  "descripcion", 8),
    ("Misterio y Thriller", "grande",    "descomunal",       "ADJ",  "neutro",   "descripcion", 6),
    ("Misterio y Thriller", "raro",      "inquietante",      "ADJ",  "poetico",  "descripcion", 9),
    ("Misterio y Thriller", "raro",      "sospechoso",       "ADJ",  "neutro",   "descripcion", 7),
    ("Misterio y Thriller", "oscuro",    "tenebroso",        "ADJ",  "poetico",  "descripcion", 9),
    ("Misterio y Thriller", "viejo",     "decrépito",        "ADJ",  "poetico",  "descripcion", 7),
    ("Misterio y Thriller", "malo",      "siniestro",        "ADJ",  "poetico",  "descripcion", 8),
    ("Misterio y Thriller", "calle",     "callejón",         "NOUN", "poetico",  "descripcion", 8),
    ("Misterio y Thriller", "casa",      "guarida",          "NOUN", "poetico",  "descripcion", 7),
    ("Misterio y Thriller", "noche",     "penumbra",         "NOUN", "poetico",  "descripcion", 7),
    ("Misterio y Thriller", "hombre",    "individuo",        "NOUN", "neutro",   "descripcion", 6),
    ("Misterio y Thriller", "ciudad",    "laberinto urbano", "NOUN", "poetico",  "descripcion", 7),

    # ── CIENCIA FICCIÓN Y FANTASÍA ÉPICA (Asimov) ─────────────────────────
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "decir",    "proclamar",         "VERB", "poetico",  "dialogo",     9),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "decir",    "transmitir",        "VERB", "tecnico",  "dialogo",     7),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "ir",       "aventurarse",       "VERB", "poetico",  "accion",      8),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "luchar",   "librar una batalla","VERB", "poetico",  "accion",      9),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "pensar",   "calcular",          "VERB", "tecnico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "ver",      "percibir",          "VERB", "tecnico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "grande",   "colosal",           "ADJ",  "poetico",  "descripcion", 9),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "grande",   "monumental",        "ADJ",  "neutro",   "descripcion", 7),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "malo",     "perverso",          "ADJ",  "poetico",  "descripcion", 9),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "bueno",    "legendario",        "ADJ",  "poetico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "poderoso", "omnipotente",       "ADJ",  "poetico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "antiguo",  "ancestral",         "ADJ",  "poetico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "nave",     "crucero estelar",   "NOUN", "tecnico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "planeta",  "mundo",             "NOUN", "neutro",   "descripcion", 6),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "espacio",  "vacío interestelar","NOUN", "poetico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "rey",      "soberano",          "NOUN", "poetico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "guerra",   "cataclismo bélico", "NOUN", "poetico",  "descripcion", 7),

    # ── ROMANCE CONTEMPORANEO (Allende) ────────────────────────────────────
    ("Romance Contemporáneo", "decir",    "susurrar",                    "VERB", "poetico",  "dialogo",     9),
    ("Romance Contemporáneo", "decir",    "confesar",                    "VERB", "poetico",  "dialogo",     8),
    ("Romance Contemporáneo", "ver",      "contemplar con ternura",      "VERB", "poetico",  "descripcion", 9),
    ("Romance Contemporáneo", "sentir",   "experimentar un latido",      "VERB", "poetico",  "descripcion", 8),
    ("Romance Contemporáneo", "abrazar",  "estrechar",                   "VERB", "poetico",  "accion",      8),
    ("Romance Contemporáneo", "mirar",    "devorar con la mirada",       "VERB", "poetico",  "descripcion", 7),
    ("Romance Contemporáneo", "bonito",   "hermoso",                     "ADJ",  "poetico",  "descripcion", 9),
    ("Romance Contemporáneo", "bueno",    "maravilloso",                 "ADJ",  "poetico",  "descripcion", 8),
    ("Romance Contemporáneo", "triste",   "desconsolado",                "ADJ",  "poetico",  "descripcion", 8),
    ("Romance Contemporáneo", "feliz",    "radiante",                    "ADJ",  "poetico",  "descripcion", 9),
    ("Romance Contemporáneo", "suave",    "aterciopelado",               "ADJ",  "poetico",  "descripcion", 8),
    ("Romance Contemporáneo", "amor",     "pasión desbordante",          "NOUN", "poetico",  "descripcion", 8),
    ("Romance Contemporáneo", "beso",     "roce de labios",              "NOUN", "poetico",  "descripcion", 7),
    ("Romance Contemporáneo", "corazón",  "pecho ardiente",              "NOUN", "poetico",  "descripcion", 6),

    # ── NO FICCION ACADEMICA (Eco) ──────────────────────────────────────────
    ("No Ficción Académica", "decir",   "afirmar",                      "VERB", "tecnico",  "dialogo",     9),
    ("No Ficción Académica", "decir",   "postular",                     "VERB", "tecnico",  "descripcion", 8),
    ("No Ficción Académica", "hacer",   "desarrollar",                  "VERB", "tecnico",  "accion",      9),
    ("No Ficción Académica", "hacer",   "implementar",                  "VERB", "tecnico",  "accion",      8),
    ("No Ficción Académica", "ver",     "observar",                     "VERB", "tecnico",  "descripcion", 8),
    ("No Ficción Académica", "pensar",  "inferir",                      "VERB", "tecnico",  "descripcion", 9),
    ("No Ficción Académica", "mostrar", "evidenciar",                   "VERB", "tecnico",  "descripcion", 8),
    ("No Ficción Académica", "bueno",   "óptimo",                       "ADJ",  "tecnico",  "descripcion", 9),
    ("No Ficción Académica", "malo",    "deficiente",                   "ADJ",  "tecnico",  "descripcion", 9),
    ("No Ficción Académica", "grande",  "considerable",                 "ADJ",  "tecnico",  "descripcion", 8),
    ("No Ficción Académica", "pequeño", "reducido",                     "ADJ",  "tecnico",  "descripcion", 7),
    ("No Ficción Académica", "importante","fundamental",                 "ADJ",  "tecnico",  "descripcion", 8),
    ("No Ficción Académica", "estudio", "investigación",                "NOUN", "tecnico",  "descripcion", 8),
    ("No Ficción Académica", "cosa",    "elemento",                     "NOUN", "tecnico",  "descripcion", 9),
    ("No Ficción Académica", "resultado","hallazgo",                    "NOUN", "tecnico",  "descripcion", 8),
]

# ---------------------------------------------------------------------------
# PALABRAS PROHIBIDAS: (tone_name, word, reason, suggestion)
# ---------------------------------------------------------------------------

PROHIBITED = [
    # Noir — rompen la atmósfera oscura con positividad o modernidad
    ("Misterio y Thriller", "maravilloso",  "Tono positivo/coloquial",    "inquietante"),
    ("Misterio y Thriller", "fantástico",   "Tono positivo/coloquial",    "desconcertante"),
    ("Misterio y Thriller", "increíble",    "Tono coloquial",             "inusual"),
    ("Misterio y Thriller", "hermoso",      "Tono romantico inapropiado", "perturbador"),
    ("Misterio y Thriller", "adorable",     "Tono romantico inapropiado", "sospechoso"),
    ("Misterio y Thriller", "brillante",    "Tono elogioso inapropiado",  "calculado"),

    # Sci-Fi / Epico — anacronismos tecnologicos o coloquialismos
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "okay",       "Anglicismo coloquial",   "de acuerdo"),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "teléfono",   "Tecnologia obsoleta",    "comunicador"),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "internet",   "Tecnologia obsoleta",    "la red"),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "selfie",     "Coloquialismo moderno",  "autorretrato"),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "email",      "Tecnologia obsoleta",    "mensaje digital"),
    ("Narrativa de Ciencia Ficción y Fantasía Épica", "trending",   "Anglicismo coloquial",   "predominante"),

    # Romance — negatividad que rompe el tono emocional
    ("Romance Contemporáneo", "feo",         "Termino negativo abrupto",  "peculiar"),
    ("Romance Contemporáneo", "horrible",    "Termino negativo abrupto",  "desconcertante"),
    ("Romance Contemporáneo", "aburrido",    "Termino coloquial negativo","sin chispa"),
    ("Romance Contemporáneo", "asqueroso",   "Termino repulsivo",         "inapropiado"),

    # Académico — informalidad que debilita la autoridad académica
    ("No Ficción Académica", "creo que",    "Opinion subjetiva",          "se postula que"),
    ("No Ficción Académica", "pienso que",  "Opinion subjetiva",          "los datos sugieren que"),
    ("No Ficción Académica", "o sea",       "Coloquialismo",              "es decir"),
    ("No Ficción Académica", "bueno",       "Coloquialismo vago",         "óptimo"),
    ("No Ficción Académica", "cosa",        "Sustantivo vago",            "elemento"),
    ("No Ficción Académica", "tipo",        "Coloquialismo",              "categoria"),
    ("No Ficción Académica", "algo así",    "Vaguedad",                   "aproximadamente"),
]


def run_seed():
    print(f"Base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- literary_thesaurus ---
    cur.execute("SELECT COUNT(*) FROM literary_thesaurus")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"[INFO] literary_thesaurus ya tiene {count} entradas. Saltando seed.")
    else:
        for entry in THESAURUS_ENTRIES:
            tone, lemma, target, pos, intensity, context, priority = entry
            cur.execute("""
                INSERT INTO literary_thesaurus
                (id, tone_name, source_lemma, target_word, pos_tag, intensity, context_hint, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), tone, lemma, target, pos, intensity, context, priority))
        print(f"  [OK] {len(THESAURUS_ENTRIES)} entradas de tesauro insertadas.")

    # --- prohibited_words ---
    cur.execute("SELECT COUNT(*) FROM prohibited_words")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"[INFO] prohibited_words ya tiene {count} entradas. Saltando seed.")
    else:
        for entry in PROHIBITED:
            tone, word, reason, suggestion = entry
            cur.execute("""
                INSERT INTO prohibited_words (id, tone_name, word, reason, suggestion)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), tone, word, reason, suggestion))
        print(f"  [OK] {len(PROHIBITED)} palabras prohibidas insertadas.")

    conn.commit()
    conn.close()
    print("\n[OK] Seed de tesauro y palabras prohibidas completado.")

if __name__ == "__main__":
    run_seed()
