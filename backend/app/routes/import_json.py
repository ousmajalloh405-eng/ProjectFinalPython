"""
import_json.py — Lecture du CSV et import vers PostgreSQL
"""

from fastapi import APIRouter, HTTPException
from typing import List
import ast

from ..database import get_connection, get_cursor

router = APIRouter(prefix="/import", tags=["Import"])

def parse_csv_line(line: str):
    """Parse une ligne du CSV en dictionnaire étudiant."""
    line = line.strip()
    if not line:
        return None
    try:
        bracket_pos   = line.index('[')
        avant         = line[:bracket_pos].rstrip(',')
        champs        = avant.split(',')
        if len(champs) < 6:
            return None
        matieres_list = ast.literal_eval(line[bracket_pos:].strip())
        moyennes      = [m['moyenne'] for m in matieres_list if 'moyenne' in m]
        return {
            'code':           champs[0].strip(),
            'numero':         champs[1].strip(),
            'nom':            champs[2].strip(),
            'prenom':         champs[3].strip(),
            'date_naissance': champs[4].strip() or None,
            'classe':         champs[5].strip(),
            'matieres':       matieres_list,
            'moyenne_generale': round(sum(moyennes)/len(moyennes), 2) if moyennes else None,
        }
    except Exception:
        return None

# ──────────────────────────────────────────────────────────────
# GET /import/preview — Aperçu des données CSV non encore en DB
# ──────────────────────────────────────────────────────────────
@router.get("/preview")
def preview_import():
    """Retourne les étudiants du CSV qui ne sont pas encore en DB."""
    conn = get_connection()
    cur  = get_cursor(conn)

    # Récupère tous les numéros déjà en base
    cur.execute("SELECT numero FROM etudiants")
    existants = {r['numero'] for r in cur.fetchall()}
    cur.close()
    conn.close()

    nouveaux = []
    try:
        with open('data/eleves_valides.csv', encoding='utf-8') as f:
            for line in f:
                etudiant = parse_csv_line(line)
                if etudiant and etudiant['numero'] not in existants:
                    nouveaux.append({
                        'code':             etudiant['code'],
                        'numero':           etudiant['numero'],
                        'nom':              etudiant['nom'],
                        'prenom':           etudiant['prenom'],
                        'date_naissance':   etudiant['date_naissance'],
                        'classe':           etudiant['classe'],
                        'moyenne_generale': etudiant['moyenne_generale'],
                        'nb_matieres':      len(etudiant['matieres']),
                    })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier CSV introuvable")

    return {"total": len(nouveaux), "data": nouveaux}

# ──────────────────────────────────────────────────────────────
# POST /import/transfer — Importe des numéros sélectionnés en DB
# ──────────────────────────────────────────────────────────────
@router.post("/transfer")
def transfer_to_db(numeros: List[str]):
    """Importe une liste de numéros depuis le CSV vers la DB."""
    if not numeros:
        raise HTTPException(status_code=400, detail="Aucun numéro fourni")

    conn = get_connection()
    cur  = get_cursor(conn)

    inserted = 0
    skipped  = 0

    try:
        with open('data/eleves_valides.csv', encoding='utf-8') as f:
            for line in f:
                etudiant = parse_csv_line(line)
                if not etudiant or etudiant['numero'] not in numeros:
                    continue

                # Vérifie doublon
                cur.execute("SELECT id FROM etudiants WHERE numero = %s",
                            (etudiant['numero'],))
                if cur.fetchone():
                    skipped += 1
                    continue

                # Insère l'étudiant
                cur.execute("""
                    INSERT INTO etudiants
                        (code, numero, nom, prenom, date_naissance,
                         classe, moyenne_generale, est_archive, source)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,FALSE,'db')
                    RETURNING id
                """, (
                    etudiant['code'], etudiant['numero'],
                    etudiant['nom'],  etudiant['prenom'],
                    etudiant['date_naissance'], etudiant['classe'],
                    etudiant['moyenne_generale']
                ))
                etudiant_id = cur.fetchone()['id']

                # Insère les matières
                for mat in etudiant['matieres']:
                    cur.execute("""
                        INSERT INTO matieres
                            (etudiant_id, nom_matiere, note_examen, moyenne_matiere)
                        VALUES (%s,%s,%s,%s)
                        RETURNING id
                    """, (etudiant_id, mat.get('matieres',''),
                          mat.get('examen'), mat.get('moyenne')))
                    matiere_id = cur.fetchone()['id']

                    for ordre, note in enumerate(mat.get('notes_dev',[]), 1):
                        cur.execute("""
                            INSERT INTO notes_devoir (matiere_id, note, ordre)
                            VALUES (%s,%s,%s)
                        """, (matiere_id, note, ordre))

                inserted += 1

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier CSV introuvable")

    conn.commit()
    cur.close()
    conn.close()

    return {
        "message":  f"{inserted} étudiant(s) importé(s) avec succès",
        "inserted": inserted,
        "skipped":  skipped
    }
