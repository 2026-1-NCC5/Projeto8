"""
Lideranças Empáticas — Backend API
FastAPI + PostgreSQL + JWT

Execute com: uvicorn main:app --reload --port 8000
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import engine, Base

# Importar todos os models para que o SQLAlchemy os registre
from models import (  # noqa: F401
    Usuario, Semestre, Equipe, EquipeMembro, EquipeMentor, HistoricoAlimento
)

# Importar rotas
from routes.auth import router as auth_router
from routes.usuarios import router as usuarios_router
from routes.semestres import router as semestres_router
from routes.equipes import router as equipes_router
from routes.historico import router as historico_router

# ── Criar tabelas ───────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ─────────────────────────────────────────
app = FastAPI(
    title="Lideranças Empáticas API",
    description="Backend para o portal de gerenciamento de equipes e lideranças empáticas.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Uploads estáticos ──────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Registrar rotas ─────────────────────────────
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(semestres_router)
app.include_router(equipes_router)
app.include_router(historico_router)


# ── Health check ────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "app": "Lideranças Empáticas API",
        "version": "1.0.0",
        "docs": "/docs",
    }
