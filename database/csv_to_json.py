"""
csv_to_json.py — Convertit eleves_valides.csv vers valides.json
"""

import ast, json

eleves = []

with open('data/eleves_valides.csv', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            bracket_pos = line.index('[')
            avant       = line[:bracket_pos].rstrip(',')
            champs      = avant.split(',')
            if len(champs) < 6:
                continue

            matieres_list = ast.literal_eval(line[bracket_pos:].strip())
            moyennes      = [m['moyenne'] for m in matieres_list if 'moyenne' in m]

            eleve = {
                'code':             champs[0].strip(),
                'numero':           champs[1].strip(),
                'nom':              champs[2].strip(),
                'prenom':           champs[3].strip(),
                'date_naissance':   champs[4].strip(),
                'classe':           champs[5].strip(),
                'moyenne_generale': round(sum(moyennes)/len(moyennes), 2) if moyennes else None,
                'matieres': [
                    {
                        'nom_matiere':     m.get('matieres', ''),
                        'note_examen':     m.get('examen'),
                        'moyenne_matiere': m.get('moyenne'),
                        'notes_dev':       m.get('notes_dev', []),
                    }
                    for m in matieres_list
                ]
            }
            eleves.append(eleve)
        except Exception as e:
            print(f"Erreur ligne : {e}")
            continue

with open('data/valides.json', 'w', encoding='utf-8') as f:
    json.dump(eleves, f, ensure_ascii=False, indent=2)

print(f"✅ {len(eleves)} étudiants exportés dans data/valides.json")
