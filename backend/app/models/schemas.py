"""
schemas.py — Modèles de données Pydantic
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# ── Notes de devoir ────────────────────────────────────────────
class NoteDevoir(BaseModel):
    id:    int
    note:  float
    ordre: int

# ── Matière ────────────────────────────────────────────────────
class Matiere(BaseModel):
    id:              int
    nom_matiere:     str
    note_examen:     Optional[float]
    moyenne_matiere: Optional[float]
    notes_devoir:    List[NoteDevoir] = []

# ── Étudiant complet (avec matières) ──────────────────────────
class Etudiant(BaseModel):
    id:               int
    code:             str
    numero:           str
    nom:              str
    prenom:           str
    date_naissance:   Optional[str]
    classe:           Optional[str]
    moyenne_generale: Optional[float]
    est_archive:      bool
    source:           str
    matieres:         List[Matiere] = []

# ── Étudiant simple (sans matières — pour le tableau) ─────────
class EtudiantResume(BaseModel):
    id:               int
    code:             str
    numero:           str
    nom:              str
    prenom:           str
    date_naissance:   Optional[str]
    classe:           Optional[str]
    moyenne_generale: Optional[float]
    est_archive:      bool
    source:           str

# ── Réponse paginée ────────────────────────────────────────────
class PaginatedEtudiants(BaseModel):
    total:    int
    page:     int
    per_page: int
    pages:    int
    data:     List[EtudiantResume]

# ── Création d'un étudiant (données envoyées par le frontend) ──
class EtudiantCreate(BaseModel):
    code:           str
    numero:         str
    nom:            str
    prenom:         str
    date_naissance: Optional[str] = None
    classe:         Optional[str] = None

# ── Modification d'un étudiant ─────────────────────────────────
class EtudiantUpdate(BaseModel):
    nom:            Optional[str] = None
    prenom:         Optional[str] = None
    date_naissance: Optional[str] = None
    classe:         Optional[str] = None
