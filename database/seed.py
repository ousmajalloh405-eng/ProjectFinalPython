"""
seed.py — Import initial de eleves_valides.csv vers PostgreSQL
"""

import ast
import os
import re
import psycopg2
from dotenv import load_dotenv

# ── Chargement des variables d'environnement ──────────────────
load_dotenv('backend/.env')

DB_CONFIG = {
    'host':     os.getenv('DB_HOST'),
    'port':     os.getenv('DB_PORT'),
    'dbname':   os.getenv('DB_NAME'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def parse_line(line):
    """
    Parse une ligne du CSV manuellement.
    Format : CODE,Numero,Nom,Prenom,DateNaissance,Classe,[liste_matieres]
    """
    line = line.strip()
    if not line:
        return None

    # Trouve le début de la liste des matières [ ... ]
    bracket_pos = line.index('[')

    # Les 6 premiers champs sont avant le crochet
    avant = line[:bracket_pos].rstrip(',')
    champs = avant.split(',')

    if len(champs) < 6:
        return None

    code           = champs[0].strip()
    numero         = champs[1].strip()
    nom            = champs[2].strip()
    prenom         = champs[3].strip()
    date_naissance = champs[4].strip() or None
    classe         = champs[5].strip()

    # Le reste est la liste des matières
    matieres_raw = line[bracket_pos:].strip()

    try:
        matieres_list = ast.literal_eval(matieres_raw)
    except Exception as e:
        print(f"  ⚠ Erreur parsing matières pour {numero}: {e}")
        return None

    return {
        'code':           code,
        'numero':         numero,
        'nom':            nom,
        'prenom':         prenom,
        'date_naissance': date_naissance,
        'classe':         classe,
        'matieres':       matieres_list,
    }

def seed():
    conn = get_connection()
    cur  = conn.cursor()

    inserted = 0
    skipped  = 0

    with open('data/eleves_valides.csv', encoding='utf-8') as f:
        for line in f:
            etudiant = parse_line(line)

            if not etudiant:
                skipped += 1
                continue

            # ── Calcul moyenne générale ────────────────────────
            moyennes = [m['moyenne'] for m in etudiant['matieres'] if 'moyenne' in m]
            moyenne_generale = round(sum(moyennes) / len(moyennes), 2) if moyennes else None

            # ── Vérifie les doublons ───────────────────────────
            cur.execute("SELECT id FROM etudiants WHERE numero = %s", (etudiant['numero'],))
            if cur.fetchone():
                print(f"  ↷ Doublon : {etudiant['numero']} - {etudiant['nom']}")
                skipped += 1
                continue

            # ── Insertion étudiant ─────────────────────────────
            cur.execute("""
                INSERT INTO etudiants
                    (code, numero, nom, prenom, date_naissance, classe,
                     moyenne_generale, est_archive, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, 'db')
                RETURNING id
            """, (
                etudiant['code'],
                etudiant['numero'],
                etudiant['nom'],
                etudiant['prenom'],
                etudiant['date_naissance'],
                etudiant['classe'],
                moyenne_generale
            ))
            etudiant_id = cur.fetchone()[0]

            # ── Insertion matières ─────────────────────────────
            for mat in etudiant['matieres']:
                cur.execute("""
                    INSERT INTO matieres
                        (etudiant_id, nom_matiere, note_examen, moyenne_matiere)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    etudiant_id,
                    mat.get('matieres', ''),
                    mat.get('examen'),
                    mat.get('moyenne')
                ))
                matiere_id = cur.fetchone()[0]

                # ── Insertion notes de devoir ──────────────────
                for ordre, note in enumerate(mat.get('notes_dev', []), start=1):
                    cur.execute("""
                        INSERT INTO notes_devoir (matiere_id, note, ordre)
                        VALUES (%s, %s, %s)
                    """, (matiere_id, note, ordre))

            inserted += 1
            print(f"  ✓ {etudiant['numero']} - {etudiant['nom']} {etudiant['prenom']} ({etudiant['classe']})")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"✅ Import terminé !")
    print(f"   Insérés  : {inserted}")
    print(f"   Ignorés  : {skipped}")
    print(f"{'='*50}")

if __name__ == '__main__':
    seed()
