from fastapi import APIRouter, Depends
from diff_match_patch import diff_match_patch
from sqlalchemy.orm import Session
from services.history.orchestrator import SnapshotOrchestrator
from services.history.repositories import SQLAlchemyChapterRepository, SQLAlchemySnapshotRepository
from database import get_db

router = APIRouter()
dmp = diff_match_patch()

def get_orchestrator(db: Session = Depends(get_db)):
    chapter_repo = SQLAlchemyChapterRepository(db)
    snapshot_repo = SQLAlchemySnapshotRepository(db)
    return SnapshotOrchestrator(db, chapter_repo, snapshot_repo)

@router.get("/compare/{chapter_id}/{v_old}/{v_new}")
async def compare_manuscript_versions(
    chapter_id: str, 
    v_old: int, 
    v_new: int, 
    orchestrator: SnapshotOrchestrator = Depends(get_orchestrator)
):
    """
    Obtiene dos versiones de SQLite, calcula el diff semántico
    y devuelve el HTML listo para el DiffOverlay.
    """
    # 1. Recuperar textos de la DB local
    text_old = orchestrator.rollback_to_snapshot(chapter_id, v_old)
    text_new = orchestrator.rollback_to_snapshot(chapter_id, v_new)

    # 2. Calcular Diferencias
    diffs = dmp.diff_main(text_old, text_new)
    
    # 3. Limpieza Semántica (Crucial para que sea legible por humanos)
    dmp.diff_cleanupSemantic(diffs)
    
    # 4. Generar HTML enriquecido
    diff_html = dmp.diff_prettyHtml(diffs)
    
    return {"diff_html": diff_html}
