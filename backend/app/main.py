"""
main.py — Point d'entrée de l'API FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.etudiants  import router as etudiants_router
from .routes.stats       import router as stats_router
from .routes.import_json import router as import_router

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

app.include_router(etudiants_router)
app.include_router(stats_router)
app.include_router(import_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API opérationnelle"}
