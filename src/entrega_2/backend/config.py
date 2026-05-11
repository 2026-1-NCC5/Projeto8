"""
Configurações centralizadas do backend.
Carrega variáveis do .env automaticamente.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # ── Database ────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/liderancas_empaticas",
    )

    # ── JWT ─────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    # ── Upload ──────────────────────────────────
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    # ── Cursos disponíveis ──────────────────────
    CURSOS_VALIDOS: list[str] = [
        "Administração",
        "Análise e Desenvolvimento de Sistemas",
        "Ciência da Computação",
        "Ciências Contábeis",
        "Ciências Econômicas",
        "Contabilidade para Graduados",
        "Publicidade e Propaganda",
        "Relações Públicas",
        "Relações Internacionais",
        "Secretariado e Assessoria Executiva",
    ]


settings = Settings()
