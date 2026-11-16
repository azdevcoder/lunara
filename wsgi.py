"""Ponto de entrada WSGI para produção (gunicorn)."""
from app import create_app

app = create_app()
