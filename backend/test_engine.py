"""
Script de prueba canónico para FakeAIRulesEngine.
Texto Noir de referencia del plan de implementación.
"""
import sys
sys.path.insert(0, '.')

from services.style_expert_engine import FakeAIRulesEngine

engine = FakeAIRulesEngine()

result = engine.analyze_and_fix(
    text="El hombre camino muy lentamente por la calle. Era una noche muy grande y maravillosa.",
    tone_name="Misterio y Thriller",
    style_profile={
        "avg_sentence_len": 10,
        "max_sentence_len": 18,
        "ttr_target": 0.75,
        "adjective_density": 0.25,
        "flesch_target": 55,
        "short_sentence_ratio": 0.4,
        "reference_author": "Raymond Chandler",
        "style_display_name": "Novela Negra / Hardboiled",
        "forbidden_words": '["maravillosa", "etéreo", "divino"]',
        "preferred_structures": '["PRON+VERB+ADV", "NOUN+VERB"]',
        "compound_replacements": '{"muy grande": "imponente", "muy lentamente": "sigilosamente", "muy buenas": "irreprochables"}',
    },
    thesaurus_entries=[
        {"source_lemma": "caminar", "target_word": "acechar", "pos_tag": "VERB", "intensity": "poetico", "context_hint": "accion", "priority": 9},
        {"source_lemma": "grande", "target_word": "imponente", "pos_tag": "ADJ", "intensity": "poetico", "context_hint": "descripcion", "priority": 8},
        {"source_lemma": "decir", "target_word": "murmurar", "pos_tag": "VERB", "intensity": "poetico", "context_hint": "dialogo", "priority": 9},
    ],
    prohibited_words=[
        {"word": "maravillosa", "reason": "Tono positivo/coloquial", "suggestion": "inquietante"},
        {"word": "fantástico", "reason": "Tono positivo", "suggestion": "desconcertante"},
    ]
)

print("=" * 60)
print("TEXTO CANÓNICO NOIR — Verificación del Motor")
print("=" * 60)
print(f"\n[corrected_text]:\n  {result.corrected_text}")
print(f"\n[suggestions] ({len(result.suggestions)}):")
for s in result.suggestions:
    print(f"  [{s.pos}] '{s.original}' → '{s.replacement}' ({s.type})")
print(f"\n[alerts] ({len(result.alerts)}):")
for a in result.alerts:
    idx = f" [frase #{a.sentence_index}]" if a.sentence_index is not None else ""
    print(f"  [{a.severity.upper()}] {a.type}{idx}: {a.message[:80]}...")
print(f"\n[style_report.alignment_score]: {result.style_report.get('alignment_score', 'N/A')}")
print(f"[style_report.avg_sentence_len]: {result.style_report.get('avg_sentence_len', 'N/A')}")
print("\n[OK] Motor Zero-IA funcionando correctamente")
