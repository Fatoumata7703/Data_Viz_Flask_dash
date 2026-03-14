# -*- coding: utf-8 -*-
"""
Configuration du projet positionnement bancaire.
MongoDB, chemins et paramètres BCEAO.
"""
import os

# Charger .env du projet si présent (MONGO_URI, etc.)
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_CONFIG_DIR, ".env")
if os.path.isfile(_env_path):
    with open(_env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value

# MongoDB (lit MONGO_URI depuis .env ou variable d'environnement)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# Base dev (brut)
MONGO_DB_NAME = "bank"
MONGO_COLLECTION_BANQUES = "banque"  # Données brutes (dev)

# Base prod (nettoyée) — utilisée en priorité pour dashboard et rapports
MONGO_DB_NAME_PROD = "bank_prod"
MONGO_COLLECTION_BANQUES_PROD = "prod"

# Chemins données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_FILE = os.path.join(DATA_DIR, "BASE_SENEGAL2.xlsx")
PDF_DOWNLOAD_DIR = os.path.join(DATA_DIR, "bceao_pdfs")

# BCEAO - page des bilans et comptes de résultat
BCEAO_BASE_URL = "https://www.bceao.int"
BCEAO_PUBLICATIONS_URL = (
    "https://www.bceao.int/fr/publications/"
    "bilans-et-comptes-de-resultat-des-banques-etablissements-financiers-et-compagnies"
)

# Années couvertes par l'Excel (base de référence)
ANNEES_EXCEL = list(range(2015, 2021))  # 2015 à 2020
