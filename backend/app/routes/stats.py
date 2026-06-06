from fastapi import APIRouter
from ..database import get_connection, get_cursor
import json, os

router = APIRouter(prefix="/stats", tags=["Statistiques"])

def load_json_data():
    path = 'data/valides.json'
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def get_numeros_db(cur):
    cur.execute("SELECT numero FROM etudiants")
    return {r['numero'] for r in cur.fetchall()}

@router.get("")
def get_stats():
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT
            COUNT(*) AS total_db,
            COUNT(*) FILTER (WHERE est_archive = FALSE) AS actifs_db,
            COUNT(*) FILTER (WHERE est_archive = TRUE)  AS archives_db,
            ROUND(AVG(moyenne_generale)::numeric, 2)    AS moyenne_db
        FROM etudiants
    """)
    row        = dict(cur.fetchone())
    numeros_db = get_numeros_db(cur)
    cur.close()
    conn.close()

    json_data     = load_json_data()
    json_eleves   = [e for e in json_data if e.get('numero') not in numeros_db]
    total_json    = len(json_eleves)
    moyennes_json = [float(e['moyenne_generale']) for e in json_eleves if e.get('moyenne_generale')]
    moyenne_json  = round(sum(moyennes_json)/len(moyennes_json), 2) if moyennes_json else 0.0

    moyenne_db  = float(row['moyenne_db']) if row['moyenne_db'] else 0.0
    toutes_moy  = [m for m in [moyenne_db, moyenne_json] if m > 0]
    moy_globale = round(sum(toutes_moy)/len(toutes_moy), 2) if toutes_moy else None

    return {
        "total":           int(row['total_db']) + total_json,
        "actifs":          int(row['actifs_db']) + total_json,
        "archives":        int(row['archives_db']),
        "source_db":       int(row['total_db']),
        "source_json":     total_json,
        "moyenne_globale": moy_globale,
    }

@router.get("/classes")
def get_stats_classes():
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT classe, COUNT(*) AS total,
               ROUND(AVG(moyenne_generale)::numeric, 2) AS moyenne
        FROM etudiants
        WHERE est_archive = FALSE AND classe IS NOT NULL
        GROUP BY classe
    """)
    db_classes = {
        r['classe']: {'total': int(r['total']), 'moyenne': float(r['moyenne'] or 0)}
        for r in cur.fetchall()
    }
    numeros_db = get_numeros_db(cur)
    cur.close()
    conn.close()

    json_data   = load_json_data()
    json_eleves = [e for e in json_data if e.get('numero') not in numeros_db]
    json_classes = {}
    for e in json_eleves:
        cl  = e.get('classe', '')
        moy = float(e.get('moyenne_generale') or 0)
        if cl not in json_classes:
            json_classes[cl] = {'total': 0, 'sum_moy': 0.0}
        json_classes[cl]['total']   += 1
        json_classes[cl]['sum_moy'] += moy

    result = []
    for cl in sorted(set(db_classes) | set(json_classes)):
        db_t = db_classes.get(cl, {}).get('total', 0)
        db_m = db_classes.get(cl, {}).get('moyenne', 0.0)
        js_t = json_classes.get(cl, {}).get('total', 0)
        js_s = json_classes.get(cl, {}).get('sum_moy', 0.0)
        tot  = db_t + js_t
        moy  = round(((db_m * db_t) + js_s) / tot, 2) if tot > 0 else 0
        result.append({'classe': cl, 'total': tot, 'moyenne': moy})
    return result

@router.get("/top10")
def get_top10():
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT numero, nom, prenom, classe, moyenne_generale
        FROM etudiants
        WHERE est_archive = FALSE AND moyenne_generale IS NOT NULL
    """)
    db_rows    = [
        {**dict(r), 'moyenne_generale': float(r['moyenne_generale'])}
        for r in cur.fetchall()
    ]
    numeros_db = get_numeros_db(cur)
    cur.close()
    conn.close()

    json_data = load_json_data()
    json_rows = [
        {
            'numero':           e.get('numero'),
            'nom':              e.get('nom'),
            'prenom':           e.get('prenom'),
            'classe':           e.get('classe'),
            'moyenne_generale': float(e.get('moyenne_generale') or 0),
        }
        for e in json_data
        if e.get('numero') not in numeros_db and e.get('moyenne_generale')
    ]

    all_rows = db_rows + json_rows
    return sorted(all_rows, key=lambda x: x['moyenne_generale'], reverse=True)[:10]

@router.get("/sources")
def get_stats_sources():
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("SELECT COUNT(*) AS total FROM etudiants WHERE est_archive = FALSE")
    total_db   = int(cur.fetchone()['total'])
    numeros_db = get_numeros_db(cur)
    cur.close()
    conn.close()

    json_data  = load_json_data()
    total_json = len([e for e in json_data if e.get('numero') not in numeros_db])
    return [
        {"source": "db",   "total": total_db},
        {"source": "json", "total": total_json},
    ]
