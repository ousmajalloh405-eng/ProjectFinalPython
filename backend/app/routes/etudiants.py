"""
etudiants.py — Routes CRUD avec fusion DB + JSON
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import math, json, os

from ..database import get_connection, get_cursor
from ..models.schemas import PaginatedEtudiants, EtudiantCreate, EtudiantUpdate

router = APIRouter(prefix="/etudiants", tags=["Étudiants"])

# ── Lecture du fichier valides.json ────────────────────────
def load_json_data():
    """Charge les données depuis valides.json"""
    path = 'data/valides.json'
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def json_to_etudiant(e, index):
    """Convertit un étudiant JSON au format standard"""
    return {
        'id':               f"json_{index}",
        'code':             e.get('code', ''),
        'numero':           e.get('numero', ''),
        'nom':              e.get('nom', ''),
        'prenom':           e.get('prenom', ''),
        'date_naissance':   e.get('date_naissance', ''),
        'classe':           e.get('classe', ''),
        'moyenne_generale': e.get('moyenne_generale'),
        'est_archive':      False,
        'source':           'json',
    }

# ──────────────────────────────────────────────────────────────
# GET /etudiants — Liste paginée avec fusion DB + JSON
# ──────────────────────────────────────────────────────────────
@router.get("")
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

    # ── 1. Récupère tous les étudiants DB ──────────────────
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

    where = "WHERE " + " AND ".join(conditions)

    cur.execute(f"""
        SELECT id, code, numero, nom, prenom,
               TO_CHAR(date_naissance, 'DD/MM/YYYY') AS date_naissance,
               classe, moyenne_generale, est_archive, source
        FROM etudiants
        {where}
        ORDER BY nom, prenom
    """, params)

    db_rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    # ── 2. Récupère les étudiants JSON si source != 'db' ───
    json_rows = []
    if source != 'db' and not archive:
        # Charge le fichier JSON
        conn2 = get_connection()
        cur2  = get_cursor(conn2)
        cur2.execute("SELECT numero FROM etudiants")
        numeros_db = {r['numero'] for r in cur2.fetchall()}
        cur2.close()
        conn2.close()

        all_json = load_json_data()
        for i, e in enumerate(all_json):
            # Ignore les étudiants déjà en DB
            if e.get('numero') in numeros_db:
                continue

            etudiant = json_to_etudiant(e, i)

            # Applique les filtres
            if search:
                s = search.lower()
                if not any([
                    s in etudiant['nom'].lower(),
                    s in etudiant['prenom'].lower(),
                    s in etudiant['numero'].lower(),
                    s in etudiant['code'].lower(),
                ]):
                    continue

            if classe and etudiant['classe'] != classe:
                continue

            json_rows.append(etudiant)

    # ── 3. Filtre source ───────────────────────────────────
    if source == 'db':
        all_rows = db_rows
    elif source == 'json':
        all_rows = json_rows
    else:
        all_rows = db_rows + json_rows

    # ── 4. Pagination ──────────────────────────────────────
    total  = len(all_rows)
    pages  = math.ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page
    paged  = all_rows[offset: offset + per_page]

    return {
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    pages,
        "data":     paged,
    }

# ──────────────────────────────────────────────────────────────
# GET /etudiants/classes — Liste des classes distinctes
# ──────────────────────────────────────────────────────────────
@router.get("/classes")
def get_classes():
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT DISTINCT classe FROM etudiants
        WHERE classe IS NOT NULL AND est_archive = FALSE
        ORDER BY classe
    """)
    db_classes = [r['classe'] for r in cur.fetchall()]
    cur.close()
    conn.close()

    # Ajoute les classes du JSON
    json_data  = load_json_data()
    json_classes = {e.get('classe','') for e in json_data if e.get('classe')}
    all_classes  = sorted(set(db_classes) | json_classes)

    return all_classes

# ──────────────────────────────────────────────────────────────
# GET /etudiants/{id} — Détail complet
# ──────────────────────────────────────────────────────────────
@router.get("/{etudiant_id}")
def get_etudiant(etudiant_id: str):
    # Si c'est un ID JSON
    if str(etudiant_id).startswith('json_'):
        index    = int(etudiant_id.replace('json_', ''))
        all_json = load_json_data()
        if index >= len(all_json):
            raise HTTPException(status_code=404, detail="Étudiant non trouvé")
        e = all_json[index]
        result = json_to_etudiant(e, index)
        result['matieres'] = e.get('matieres', [])
        return result

    # Sinon c'est un ID DB
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT id, code, numero, nom, prenom,
               TO_CHAR(date_naissance, 'DD/MM/YYYY') AS date_naissance,
               classe, moyenne_generale, est_archive, source
        FROM etudiants WHERE id = %s
    """, (etudiant_id,))
    etudiant = cur.fetchone()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    etudiant = dict(etudiant)
    cur.execute("""
        SELECT id, nom_matiere, note_examen, moyenne_matiere
        FROM matieres WHERE etudiant_id = %s ORDER BY nom_matiere
    """, (etudiant_id,))
    matieres = cur.fetchall()
    etudiant['matieres'] = []
    for mat in matieres:
        mat = dict(mat)
        cur.execute("""
            SELECT id, note, ordre FROM notes_devoir
            WHERE matiere_id = %s ORDER BY ordre
        """, (mat['id'],))
        mat['notes_devoir'] = [dict(n) for n in cur.fetchall()]
        etudiant['matieres'].append(mat)

    cur.close()
    conn.close()
    return etudiant

# ──────────────────────────────────────────────────────────────
# POST /etudiants — Ajouter un étudiant
# ──────────────────────────────────────────────────────────────
@router.post("", status_code=201)
def create_etudiant(data: EtudiantCreate):
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("SELECT id FROM etudiants WHERE numero = %s", (data.numero,))
    if cur.fetchone():
        raise HTTPException(
            status_code=409,
            detail=f"Un étudiant avec le numéro '{data.numero}' existe déjà"
        )

    cur.execute("""
        INSERT INTO etudiants
            (code, numero, nom, prenom, date_naissance, classe, source)
        VALUES (%s,%s,%s,%s,%s,%s,'db')
        RETURNING id
    """, (data.code, data.numero, data.nom, data.prenom,
          data.date_naissance, data.classe))

    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Étudiant créé avec succès", "id": new_id}

# ──────────────────────────────────────────────────────────────
# PATCH /etudiants/{id} — Modifier un étudiant DB
# ──────────────────────────────────────────────────────────────
@router.patch("/{etudiant_id}")
def update_etudiant(etudiant_id: int, data: EtudiantUpdate):
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("SELECT id, source FROM etudiants WHERE id = %s", (etudiant_id,))
    etudiant = cur.fetchone()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    if etudiant['source'] != 'db':
        raise HTTPException(
            status_code=403,
            detail="Seuls les étudiants DB sont modifiables"
        )

    fields = []
    params = []
    for field, value in data.model_dump(exclude_none=True).items():
        fields.append(f"{field} = %s")
        params.append(value)

    if not fields:
        raise HTTPException(status_code=400, detail="Aucune donnée à modifier")

    params.append(etudiant_id)
    cur.execute(f"UPDATE etudiants SET {', '.join(fields)} WHERE id = %s", params)
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Étudiant modifié avec succès"}

# ──────────────────────────────────────────────────────────────
# PATCH /etudiants/{id}/archive — Archiver
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
        raise HTTPException(status_code=400, detail="Déjà archivé")

    cur.execute("UPDATE etudiants SET est_archive = TRUE WHERE id = %s", (etudiant_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Étudiant archivé avec succès"}

# ──────────────────────────────────────────────────────────────
# PATCH /etudiants/{id}/restaurer — Restaurer
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

    cur.execute("UPDATE etudiants SET est_archive = FALSE WHERE id = %s", (etudiant_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Étudiant restauré avec succès"}
