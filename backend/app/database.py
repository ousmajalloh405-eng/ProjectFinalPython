"""
database.py — Gestion de la connexion PostgreSQL
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Charge les variables depuis backend/.env
load_dotenv('backend/.env')

DB_CONFIG = {
    'host':     os.getenv('DB_HOST'),
    'port':     os.getenv('DB_PORT'),
    'dbname':   os.getenv('DB_NAME'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}

def get_connection():
    """Retourne une connexion PostgreSQL active."""
    return psycopg2.connect(**DB_CONFIG)

def get_cursor(conn):
    """Retourne un curseur qui retourne des dictionnaires."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
