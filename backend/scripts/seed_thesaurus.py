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

    # ── CIENCIA FICCION Y FANTASIA EPICA (Asimov) ──────────────────────────
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "decir",    "proclamar",         "VERB", "poetico",  "dialogo",     9),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "decir",    "transmitir",        "VERB", "tecnico",  "dialogo",     7),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "ir",       "aventurarse",       "VERB", "poetico",  "accion",      8),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "luchar",   "librar una batalla","VERB", "poetico",  "accion",      9),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "pensar",   "calcular",          "VERB", "tecnico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "ver",      "percibir",          "VERB", "tecnico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "grande",   "colosal",           "ADJ",  "poetico",  "descripcion", 9),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "grande",   "monumental",        "ADJ",  "neutro",   "descripcion", 7),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "malo",     "perverso",          "ADJ",  "poetico",  "descripcion", 9),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "bueno",    "legendario",        "ADJ",  "poetico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "poderoso", "omnipotente",       "ADJ",  "poetico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "antiguo",  "ancestral",         "ADJ",  "poetico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "nave",     "crucero estelar",   "NOUN", "tecnico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "planeta",  "mundo",             "NOUN", "neutro",   "descripcion", 6),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "espacio",  "vacío interestelar","NOUN", "poetico",  "descripcion", 7),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "rey",      "soberano",          "NOUN", "poetico",  "descripcion", 8),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "guerra",   "cataclismo bélico", "NOUN", "poetico",  "descripcion", 7),

    # ── ROMANCE CONTEMPORANEO (Allende) ────────────────────────────────────
    ("Romance Contemporaneo", "decir",    "susurrar",                    "VERB", "poetico",  "dialogo",     9),
    ("Romance Contemporaneo", "decir",    "confesar",                    "VERB", "poetico",  "dialogo",     8),
    ("Romance Contemporaneo", "ver",      "contemplar con ternura",      "VERB", "poetico",  "descripcion", 9),
    ("Romance Contemporaneo", "sentir",   "experimentar un latido",      "VERB", "poetico",  "descripcion", 8),
    ("Romance Contemporaneo", "abrazar",  "estrechar",                   "VERB", "poetico",  "accion",      8),
    ("Romance Contemporaneo", "mirar",    "devorar con la mirada",       "VERB", "poetico",  "descripcion", 7),
    ("Romance Contemporaneo", "bonito",   "hermoso",                     "ADJ",  "poetico",  "descripcion", 9),
    ("Romance Contemporaneo", "bueno",    "maravilloso",                 "ADJ",  "poetico",  "descripcion", 8),
    ("Romance Contemporaneo", "triste",   "desconsolado",                "ADJ",  "poetico",  "descripcion", 8),
    ("Romance Contemporaneo", "feliz",    "radiante",                    "ADJ",  "poetico",  "descripcion", 9),
    ("Romance Contemporaneo", "suave",    "aterciopelado",               "ADJ",  "poetico",  "descripcion", 8),
    ("Romance Contemporaneo", "amor",     "pasión desbordante",          "NOUN", "poetico",  "descripcion", 8),
    ("Romance Contemporaneo", "beso",     "roce de labios",              "NOUN", "poetico",  "descripcion", 7),
    ("Romance Contemporaneo", "corazón",  "pecho ardiente",              "NOUN", "poetico",  "descripcion", 6),

    # ── NO FICCION ACADEMICA (Eco) ──────────────────────────────────────────
    ("No Ficcion Academica", "decir",   "afirmar",                      "VERB", "tecnico",  "dialogo",     9),
    ("No Ficcion Academica", "decir",   "postular",                     "VERB", "tecnico",  "descripcion", 8),
    ("No Ficcion Academica", "hacer",   "desarrollar",                  "VERB", "tecnico",  "accion",      9),
    ("No Ficcion Academica", "hacer",   "implementar",                  "VERB", "tecnico",  "accion",      8),
    ("No Ficcion Academica", "ver",     "observar",                     "VERB", "tecnico",  "descripcion", 8),
    ("No Ficcion Academica", "pensar",  "inferir",                      "VERB", "tecnico",  "descripcion", 9),
    ("No Ficcion Academica", "mostrar", "evidenciar",                   "VERB", "tecnico",  "descripcion", 8),
    ("No Ficcion Academica", "bueno",   "óptimo",                       "ADJ",  "tecnico",  "descripcion", 9),
    ("No Ficcion Academica", "malo",    "deficiente",                   "ADJ",  "tecnico",  "descripcion", 9),
    ("No Ficcion Academica", "grande",  "considerable",                 "ADJ",  "tecnico",  "descripcion", 8),
    ("No Ficcion Academica", "pequeño", "reducido",                     "ADJ",  "tecnico",  "descripcion", 7),
    ("No Ficcion Academica", "importante","fundamental",                 "ADJ",  "tecnico",  "descripcion", 8),
    ("No Ficcion Academica", "estudio", "investigación",                "NOUN", "tecnico",  "descripcion", 8),
    ("No Ficcion Academica", "cosa",    "elemento",                     "NOUN", "tecnico",  "descripcion", 9),
    ("No Ficcion Academica", "resultado","hallazgo",                    "NOUN", "tecnico",  "descripcion", 8),
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
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "okay",       "Anglicismo coloquial",   "de acuerdo"),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "teléfono",   "Tecnologia obsoleta",    "comunicador"),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "internet",   "Tecnologia obsoleta",    "la red"),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "selfie",     "Coloquialismo moderno",  "autorretrato"),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "email",      "Tecnologia obsoleta",    "mensaje digital"),
    ("Narrativa de Ciencia Ficcion y Fantasia Epica", "trending",   "Anglicismo coloquial",   "predominante"),

    # Romance — negatividad que rompe el tono emocional
    ("Romance Contemporaneo", "feo",         "Termino negativo abrupto",  "peculiar"),
    ("Romance Contemporaneo", "horrible",    "Termino negativo abrupto",  "desconcertante"),
    ("Romance Contemporaneo", "aburrido",    "Termino coloquial negativo","sin chispa"),
    ("Romance Contemporaneo", "asqueroso",   "Termino repulsivo",         "inapropiado"),

    # Academico — informalidad que debilita la autoridad academica
    ("No Ficcion Academica", "creo que",    "Opinion subjetiva",          "se postula que"),
    ("No Ficcion Academica", "pienso que",  "Opinion subjetiva",          "los datos sugieren que"),
    ("No Ficcion Academica", "o sea",       "Coloquialismo",              "es decir"),
    ("No Ficcion Academica", "bueno",       "Coloquialismo vago",         "óptimo"),
    ("No Ficcion Academica", "cosa",        "Sustantivo vago",            "elemento"),
    ("No Ficcion Academica", "tipo",        "Coloquialismo",              "categoria"),
    ("No Ficcion Academica", "algo así",    "Vaguedad",                   "aproximadamente"),
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
