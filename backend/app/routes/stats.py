"""
stats.py — Routes statistiques pour le dashboard
"""

from fastapi import APIRouter
from ..database import get_connection, get_cursor

router = APIRouter(prefix="/stats", tags=["Statistiques"])

# ──────────────────────────────────────────────────────────────
# GET /stats — KPI globaux
# ──────────────────────────────────────────────────────────────
@router.get("")
def get_stats():
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("""
        SELECT
            COUNT(*)                                    AS total,
            COUNT(*) FILTER (WHERE est_archive = FALSE) AS actifs,
            COUNT(*) FILTER (WHERE est_archive = TRUE)  AS archives,
            COUNT(*) FILTER (WHERE source = 'db')       AS source_db,
            COUNT(*) FILTER (WHERE source = 'json')     AS source_json,
            ROUND(AVG(moyenne_generale)::numeric, 2)    AS moyenne_globale
        FROM etudiants
    """)
    stats = dict(cur.fetchone())

    cur.close()
    conn.close()
    return stats

# ──────────────────────────────────────────────────────────────
# GET /stats/classes — Répartition par classe
# ──────────────────────────────────────────────────────────────
@router.get("/classes")
def get_stats_classes():
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("""
        SELECT
            classe,
            COUNT(*)                                 AS total,
            ROUND(AVG(moyenne_generale)::numeric, 2) AS moyenne
        FROM etudiants
        WHERE est_archive = FALSE AND classe IS NOT NULL
        GROUP BY classe
        ORDER BY classe
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

# ──────────────────────────────────────────────────────────────
# GET /stats/top10 — Top 10 meilleures moyennes
# ──────────────────────────────────────────────────────────────
@router.get("/top10")
def get_top10():
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("""
        SELECT
            numero, nom, prenom, classe,
            moyenne_generale
        FROM etudiants
        WHERE est_archive = FALSE
          AND moyenne_generale IS NOT NULL
        ORDER BY moyenne_generale DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

# ──────────────────────────────────────────────────────────────
# GET /stats/sources — Répartition DB vs JSON
# ──────────────────────────────────────────────────────────────
@router.get("/sources")
def get_stats_sources():
    conn = get_connection()
    cur  = get_cursor(conn)

    cur.execute("""
        SELECT
            source,
            COUNT(*) AS total
        FROM etudiants
        WHERE est_archive = FALSE
        GROUP BY source
        ORDER BY source
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]
