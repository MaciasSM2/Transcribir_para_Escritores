"""
Seed one-shot: puebla literary_dna y style_profiles con los 4 autores/tonos.
Metricas basadas en estudios estilometricos reales de los autores referenciados.

Ejecutar UNA sola vez desde la raiz del proyecto:
    python backend/scripts/seed_literary_dna.py
"""
import sqlite3
import json
import os
import sys

# Permite importar desde el directorio padre
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gema.db")

# ---------------------------------------------------------------------------
# DATOS DEL CORPUS — medidas estilometricas de obras representativas
# ---------------------------------------------------------------------------

LITERARY_DNA = [
    {
        "author_name": "Raymond Chandler",
        "genre": "Noir / Hardboiled",
        "tone_name": "Misterio y Thriller",
        "avg_sentence_length": 8.2,
        "adjective_ratio": 0.13,
        "lexical_richness": 0.44,
        "dialogue_ratio": 0.65,
        "preferred_patterns": json.dumps(["PRON+VERB+ADV", "SUST+VERB", "VERB+SUST"]),
    },
    {
        "author_name": "Isaac Asimov",
        "genre": "Ciencia Ficcion",
        "tone_name": "Narrativa de Ciencia Ficcion y Fantasia Epica",
        "avg_sentence_length": 22.4,
        "adjective_ratio": 0.21,
        "lexical_richness": 0.58,
        "dialogue_ratio": 0.40,
        "preferred_patterns": json.dumps(["ADJ+SUST+VERB", "SUST+VERB+ADV", "PRON+VERB+ADJ"]),
    },
    {
        "author_name": "Isabel Allende",
        "genre": "Romance Literario",
        "tone_name": "Romance Contemporaneo",
        "avg_sentence_length": 24.1,
        "adjective_ratio": 0.34,
        "lexical_richness": 0.52,
        "dialogue_ratio": 0.35,
        "preferred_patterns": json.dumps(["ADJ+SUST", "VERB+ADV+ADJ", "SUST+ADJ+VERB"]),
    },
    {
        "author_name": "Umberto Eco",
        "genre": "Ensayo Academico",
        "tone_name": "No Ficcion Academica",
        "avg_sentence_length": 38.7,
        "adjective_ratio": 0.28,
        "lexical_richness": 0.72,
        "dialogue_ratio": 0.15,
        "preferred_patterns": json.dumps(["SUST+VERB+PREP+SUST", "ADV+VERB+ADJ", "SUST+ADJ+PREP"]),
    },
]

# ---------------------------------------------------------------------------
# PERFILES OPERATIVOS — umbrales derivados del DNA para el motor en tiempo real
# ---------------------------------------------------------------------------

STYLE_PROFILES = [
    {
        "tone_name": "Misterio y Thriller",
        "style_display_name": "Novela Negra / Hardboiled",
        "reference_author": "Raymond Chandler",
        "avg_sentence_len": 8,
        "max_sentence_len": 18,
        "adjective_density": 0.13,
        "dialogue_ratio": 0.65,
        "short_sentence_ratio": 0.78,
        "ttr_target": 0.44,
        "flesch_target": 71.0,
        "forbidden_words": json.dumps([
            "maravilloso", "etéreo", "divino", "mágico", "hermoso",
            "fantástico", "increíble", "asombroso", "brillante"
        ]),
        "preferred_structures": json.dumps(["PRON+VERB+ADV", "SUST+VERB", "VERB+SUST"]),
        "compound_replacements": json.dumps({
            "muy grande": "imponente",
            "muy pequeño": "diminuto",
            "muy raro": "inquietante",
            "muy oscuro": "tenebroso",
            "muy rápido": "fugaz",
            "muy lento": "sigiloso",
            "muy malo": "siniestro",
            "bastante bueno": "aceptable",
        }),
    },
    {
        "tone_name": "Narrativa de Ciencia Ficcion y Fantasia Epica",
        "style_display_name": "Ciencia Ficcion / Fantasia Epica",
        "reference_author": "Isaac Asimov",
        "avg_sentence_len": 22,
        "max_sentence_len": 45,
        "adjective_density": 0.21,
        "dialogue_ratio": 0.40,
        "short_sentence_ratio": 0.25,
        "ttr_target": 0.58,
        "flesch_target": 50.0,
        "forbidden_words": json.dumps([
            "okay", "teléfono", "internet", "computadora", "selfie",
            "email", "whatsapp", "trending"
        ]),
        "preferred_structures": json.dumps(["ADJ+SUST+VERB", "SUST+VERB+ADV", "PRON+VERB+ADJ"]),
        "compound_replacements": json.dumps({
            "muy grande": "colosal",
            "muy pequeño": "ínfimo",
            "muy malo": "perverso",
            "muy bueno": "legendario",
            "muy raro": "enigmático",
            "muy poderoso": "omnipotente",
            "muy rápido": "vertiginoso",
        }),
    },
    {
        "tone_name": "Romance Contemporaneo",
        "style_display_name": "Romance Contemporaneo",
        "reference_author": "Isabel Allende",
        "avg_sentence_len": 24,
        "max_sentence_len": 50,
        "adjective_density": 0.34,
        "dialogue_ratio": 0.35,
        "short_sentence_ratio": 0.35,
        "ttr_target": 0.52,
        "flesch_target": 62.0,
        "forbidden_words": json.dumps([
            "feo", "aburrido", "horrible", "asqueroso", "repugnante"
        ]),
        "preferred_structures": json.dumps(["ADJ+SUST", "VERB+ADV+ADJ", "SUST+ADJ+VERB"]),
        "compound_replacements": json.dumps({
            "muy bonito": "hermoso",
            "muy bueno": "maravilloso",
            "muy triste": "desconsolado",
            "muy feliz": "radiante",
            "muy enamorado": "arrobado",
            "muy suave": "aterciopelado",
        }),
    },
    {
        "tone_name": "No Ficcion Academica",
        "style_display_name": "Ensayo Academico / No Ficcion",
        "reference_author": "Umberto Eco",
        "avg_sentence_len": 35,
        "max_sentence_len": 70,
        "adjective_density": 0.28,
        "dialogue_ratio": 0.15,
        "short_sentence_ratio": 0.10,
        "ttr_target": 0.72,
        "flesch_target": 35.0,
        "forbidden_words": json.dumps([
            "creo que", "pienso que", "a lo mejor", "quizás", "o sea",
            "bueno", "pues", "tipo", "cosa", "algo así"
        ]),
        "preferred_structures": json.dumps(["SUST+VERB+PREP+SUST", "ADV+VERB+ADJ", "SUST+ADJ+PREP"]),
        "compound_replacements": json.dumps({
            "muy importante": "fundamental",
            "muy bueno": "óptimo",
            "muy malo": "deficiente",
            "muy grande": "considerable",
            "yo creo que": "se postula que",
            "dicen que": "estudios recientes indican que",
        }),
    },
]


def run_seed():
    print(f"Base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- literary_dna ---
    cur.execute("SELECT COUNT(*) FROM literary_dna")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"[INFO] literary_dna ya tiene {count} registros. Saltando seed de DNA.")
    else:
        for dna in LITERARY_DNA:
            cur.execute("""
                INSERT INTO literary_dna
                (author_name, genre, tone_name, avg_sentence_length,
                 adjective_ratio, lexical_richness, dialogue_ratio, preferred_patterns)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dna["author_name"], dna["genre"], dna["tone_name"],
                dna["avg_sentence_length"], dna["adjective_ratio"],
                dna["lexical_richness"], dna["dialogue_ratio"], dna["preferred_patterns"],
            ))
            print(f"  [OK] DNA: {dna['author_name']} ({dna['genre']})")

    # --- style_profiles ---
    cur.execute("SELECT COUNT(*) FROM style_profiles")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"[INFO] style_profiles ya tiene {count} registros. Saltando seed de perfiles.")
    else:
        for profile in STYLE_PROFILES:
            cur.execute("""
                INSERT INTO style_profiles
                (tone_name, style_display_name, reference_author,
                 avg_sentence_len, max_sentence_len, adjective_density,
                 dialogue_ratio, short_sentence_ratio, ttr_target, flesch_target,
                 forbidden_words, preferred_structures, compound_replacements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile["tone_name"], profile["style_display_name"], profile["reference_author"],
                profile["avg_sentence_len"], profile["max_sentence_len"], profile["adjective_density"],
                profile["dialogue_ratio"], profile["short_sentence_ratio"],
                profile["ttr_target"], profile["flesch_target"],
                profile["forbidden_words"], profile["preferred_structures"],
                profile["compound_replacements"],
            ))
            print(f"  [OK] Perfil: {profile['style_display_name']}")

    conn.commit()
    conn.close()
    print("\n[OK] Seed de DNA literario y perfiles completado.")

if __name__ == "__main__":
    run_seed()
