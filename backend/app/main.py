from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes.etudiants  import router as etudiants_router
from .routes.stats       import router as stats_router
from .routes.import_json import router as import_router

app = FastAPI(
    title="API Gestion Étudiants",
    description="API REST - Projet Final P8",
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

# Sert les fichiers statiques du frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def index():
    return FileResponse("frontend/index.html")

@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API opérationnelle"}
