"""
etudiants.py — Routes CRUD complètes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import math

from ..database import get_connection, get_cursor
from ..models.schemas import (
    PaginatedEtudiants, Etudiant, EtudiantCreate, EtudiantUpdate
)

router = APIRouter(prefix="/etudiants", tags=["Étudiants"])

# ──────────────────────────────────────────────────────────────
# GET /etudiants — Liste paginée avec filtres
# ──────────────────────────────────────────────────────────────
@router.get("", response_model=PaginatedEtudiants)
def get_etudiants(
    page:     int           = Query(1,     ge=1),
    per_page: int           = Query(5,     ge=1, le=100),
    search:   Optional[str] = Query(None),
    classe:   Optional[str] = Query(None),
    source:   Optional[str] = Query(None),
    archive:  bool          = Query(False),
):
    conn = get_connection()
    cur  = get_cursor(conn)

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

    cur.execute(f"SELECT COUNT(*) AS total FROM etudiants {where}", params)
    total = cur.fetchone()['total']

    pages  = math.ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page

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

# ──────────────────────────────────────────────────────────────
# GET /etudiants/classes — Liste des classes distinctes
# ──────────────────────────────────────────────────────────────
@router.get("/classes")
def get_classes():
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT DISTINCT classe
        FROM etudiants
        WHERE classe IS NOT NULL AND est_archive = FALSE
        ORDER BY classe
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r['classe'] for r in rows]

# ──────────────────────────────────────────────────────────────
# GET /etudiants/{id} — Détail complet avec matières
# ──────────────────────────────────────────────────────────────
@router.get("/{etudiant_id}")
def get_etudiant(etudiant_id: int):
    conn = get_connection()
    cur  = get_cursor(conn)

    # Récupère l'étudiant
    cur.execute("""
        SELECT id, code, numero, nom, prenom,
               TO_CHAR(date_naissance, 'DD/MM/YYYY') AS date_naissance,
               classe, moyenne_generale, est_archive, source
        FROM etudiants
        WHERE id = %s
    """, (etudiant_id,))
    etudiant = cur.fetchone()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    etudiant = dict(etudiant)

    # Récupère ses matières
    cur.execute("""
        SELECT id, nom_matiere, note_examen, moyenne_matiere
        FROM matieres
        WHERE etudiant_id = %s
        ORDER BY nom_matiere
    """, (etudiant_id,))
    matieres = cur.fetchall()

    etudiant['matieres'] = []
    for mat in matieres:
        mat = dict(mat)

        # Récupère les notes de devoir de cette matière
        cur.execute("""
            SELECT id, note, ordre
            FROM notes_devoir
            WHERE matiere_id = %s
            ORDER BY ordre
        """, (mat['id'],))
        mat['notes_devoir'] = [dict(n) for n in cur.fetchall()]
        etudiant['matieres'].append(mat)

    cur.close()
    conn.close()
    return etudiant

# ──────────────────────────────────────────────────────────────
# POST /etudiants — Ajouter un nouvel étudiant
# ──────────────────────────────────────────────────────────────
@router.post("", status_code=201)
def create_etudiant(data: EtudiantCreate):
    conn = get_connection()
    cur  = get_cursor(conn)

    # Vérifie si le numéro existe déjà
    cur.execute("SELECT id FROM etudiants WHERE numero = %s", (data.numero,))
    if cur.fetchone():
        raise HTTPException(
            status_code=409,
            detail=f"Un étudiant avec le numéro '{data.numero}' existe déjà"
        )

    cur.execute("""
        INSERT INTO etudiants
            (code, numero, nom, prenom, date_naissance, classe, source)
        VALUES (%s, %s, %s, %s, %s, %s, 'db')
        RETURNING id
    """, (
        data.code, data.numero, data.nom, data.prenom,
        data.date_naissance, data.classe
    ))

    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Étudiant créé avec succès", "id": new_id}

# ──────────────────────────────────────────────────────────────
# PATCH /etudiants/{id} — Modifier partiellement un étudiant
# ──────────────────────────────────────────────────────────────
@router.patch("/{etudiant_id}")
def update_etudiant(etudiant_id: int, data: EtudiantUpdate):
    conn = get_connection()
    cur  = get_cursor(conn)

    # Vérifie que l'étudiant existe et vient de la DB
    cur.execute("SELECT id, source FROM etudiants WHERE id = %s", (etudiant_id,))
    etudiant = cur.fetchone()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    if etudiant['source'] != 'db':
        raise HTTPException(
            status_code=403,
            detail="Seuls les étudiants de source 'db' sont modifiables"
        )

    # Construit la mise à jour dynamiquement
    fields = []
    params = []
    for field, value in data.model_dump(exclude_none=True).items():
        fields.append(f"{field} = %s")
        params.append(value)

    if not fields:
        raise HTTPException(status_code=400, detail="Aucune donnée à modifier")

    params.append(etudiant_id)
    cur.execute(
        f"UPDATE etudiants SET {', '.join(fields)} WHERE id = %s",
        params
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Étudiant modifié avec succès"}

# ──────────────────────────────────────────────────────────────
# PATCH /etudiants/{id}/archive — Archiver un étudiant
# ──────────────────────────────────────────────────────────────
@router.patch("/{etudiant_id}/archive")
def archive_etudiant(etudiant_id: int):
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("SELECT id, est_archive FROM etudiants WHERE id = %s", (etudiant_id,))
    etudiant = cur.fetchone()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    if etudiant['est_archive']:
        raise HTTPException(status_code=400, detail="Étudiant déjà archivé")

    cur.execute(
        "UPDATE etudiants SET est_archive = TRUE WHERE id = %s",
        (etudiant_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Étudiant archivé avec succès"}

# ──────────────────────────────────────────────────────────────
# PATCH /etudiants/{id}/restaurer — Restaurer un étudiant archivé
# ──────────────────────────────────────────────────────────────
@router.patch("/{etudiant_id}/restaurer")
def restaurer_etudiant(etudiant_id: int):
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("SELECT id, est_archive FROM etudiants WHERE id = %s", (etudiant_id,))
    etudiant = cur.fetchone()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    if not etudiant['est_archive']:
        raise HTTPException(status_code=400, detail="Étudiant non archivé")

    cur.execute(
        "UPDATE etudiants SET est_archive = FALSE WHERE id = %s",
        (etudiant_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Étudiant restauré avec succès"}
