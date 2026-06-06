"""
seed.py — Importe seulement les 20 premiers étudiants en DB
Le reste reste dans valides.json (source JSON)
"""

import ast, os
import psycopg2
from dotenv import load_dotenv

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

def seed():
    conn = get_connection()
    cur  = conn.cursor()

    inserted = 0
    limite   = 20  # Seulement 20 en DB, le reste reste en JSON

    with open('data/eleves_valides.csv', encoding='utf-8') as f:
        for line in f:
            if inserted >= limite:
                break

            etudiant = parse_line(line)
            if not etudiant:
                continue

            # Vérifie doublon
            cur.execute("SELECT id FROM etudiants WHERE numero = %s",
                        (etudiant['numero'],))
            if cur.fetchone():
                continue

            # Insère étudiant avec source = 'db'
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
            etudiant_id = cur.fetchone()[0]

            # Insère matières
            for mat in etudiant['matieres']:
                cur.execute("""
                    INSERT INTO matieres
                        (etudiant_id, nom_matiere, note_examen, moyenne_matiere)
                    VALUES (%s,%s,%s,%s)
                    RETURNING id
                """, (etudiant_id, mat.get('matieres',''),
                      mat.get('examen'), mat.get('moyenne')))
                matiere_id = cur.fetchone()[0]

                for ordre, note in enumerate(mat.get('notes_dev',[]), 1):
                    cur.execute("""
                        INSERT INTO notes_devoir (matiere_id, note, ordre)
                        VALUES (%s,%s,%s)
                    """, (matiere_id, note, ordre))

            inserted += 1
            print(f"  ✓ DB [{inserted}] : {etudiant['numero']} - {etudiant['nom']}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\n✅ {inserted} étudiants insérés en DB")
    print(f"📄 Le reste ({95 - inserted}) reste dans valides.json")

if __name__ == '__main__':
    seed()
