"""
etudiants.py — Routes CRUD pour les étudiants
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import math

from ..database import get_connection, get_cursor
from ..models.schemas import PaginatedEtudiants, EtudiantResume

router = APIRouter(prefix="/etudiants", tags=["Étudiants"])

# ── GET /etudiants — Liste paginée avec filtres ────────────────
@router.get("", response_model=PaginatedEtudiants)
def get_etudiants(
    page:     int            = Query(1,    ge=1),
    per_page: int            = Query(5,    ge=1, le=100),
    search:   Optional[str]  = Query(None),
    classe:   Optional[str]  = Query(None),
    source:   Optional[str]  = Query(None),
    archive:  bool           = Query(False),
):
    conn = get_connection()
    cur  = get_cursor(conn)

    # ── Construction dynamique de la requête SQL ───────────────
    conditions = ["est_archive = %s"]
    params     = [archive]

    if search:
        conditions.append("""
            (LOWER(nom)    LIKE LOWER(%s)
          OR LOWER(prenom) LIKE LOWER(%s)
          OR LOWER(numero) LIKE LOWER(%s)
          OR LOWER(code)   LIKE LOWER(%s))
        """)
        like = f"%{search}%"
        params += [like, like, like, like]

    if classe:
        conditions.append("classe = %s")
        params.append(classe)

    if source:
        conditions.append("source = %s")
        params.append(source)

    where = "WHERE " + " AND ".join(conditions)

    # ── Compte le total ────────────────────────────────────────
    cur.execute(f"SELECT COUNT(*) AS total FROM etudiants {where}", params)
    total = cur.fetchone()['total']

    # ── Calcul pagination ──────────────────────────────────────
    pages  = math.ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page

    # ── Récupère les données ───────────────────────────────────
    cur.execute(f"""
        SELECT id, code, numero, nom, prenom,
               TO_CHAR(date_naissance, 'DD/MM/YYYY') AS date_naissance,
               classe, moyenne_generale, est_archive, source
        FROM etudiants
        {where}
        ORDER BY nom, prenom
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    pages,
        "data":     [dict(r) for r in rows],
    }
