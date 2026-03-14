# -*- coding: utf-8 -*-
"""
Config MongoDB Atlas partagée pour les dashboards Flash Dash
(solaire, assurance, hospitalier). Charge .env à la racine du projet.
"""
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_ROOT, ".env")

if os.path.isfile(_ENV_PATH):
    with open(_ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value

MONGO_URI = os.environ.get("MONGO_URI", "")
FLASH_DASH_DB = "flash_dash"
SOLAR_COLLECTION = "solar"
ASSURANCE_COLLECTION = "assurance"
HOSPITAL_COLLECTION = "hospital"
