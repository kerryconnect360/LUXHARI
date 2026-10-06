# Compatibility shim. The application-owned seeder lives in app/seed_catalog.py.
from app.seed_catalog import ensure_starter_catalog

__all__ = ['ensure_starter_catalog']
