"""
main.py — Point d'entrée de l'API FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.etudiants import router as etudiants_router

app = FastAPI(
    title="API Gestion Étudiants",
    description="API REST pour la gestion des étudiants - Projet Final P8",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Enregistrement des routes ──────────────────────────────────
app.include_router(etudiants_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API opérationnelle"}
