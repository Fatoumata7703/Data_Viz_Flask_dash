# -*- coding: utf-8 -*-
"""
Envoie les CSV des dashboards vers MongoDB Atlas.
- data/solar_data.csv ou data/salar_data.csv -> flash_dash.solar
- data/assurance_data_1000.csv -> flash_dash.assurance
- dashbord_pro/data/hospital_data (1).csv -> flash_dash.hospital

Usage (depuis la racine du projet, avec .env contenant MONGO_URI):
  python upload_csv_to_atlas.py
"""
import os
import sys
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Charger la config (et .env)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_mongo as cfg

ROOT = os.path.dirname(os.path.abspath(__file__))


def _df_to_docs(df):
    """Convertit un DataFrame en liste de dicts sans _id, types compatibles MongoDB."""
    df = df.copy()
    # Remplacer NaN par None pour MongoDB
    df = df.where(pd.notna(df), None)
    records = df.to_dict("records")
    for r in records:
        r.pop("_id", None)
    return records


def main():
    if not cfg.MONGO_URI or cfg.MONGO_URI.strip() == "mongodb://localhost:27017":
        print("Erreur: définir MONGO_URI (Atlas) dans .env à la racine du projet.")
        return 1
    try:
        client = MongoClient(
            cfg.MONGO_URI,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=15000,
        )
        db = client[cfg.FLASH_DASH_DB]
        # Vérifier la connexion tout de suite
        client.admin.command("ping")
    except ServerSelectionTimeoutError as e:
        print("Erreur: impossible de joindre MongoDB Atlas (timeout).")
        print("Vérifiez :")
        print("  1. Atlas → Network Access → ajoutez votre IP ou 0.0.0.0/0 (Allow from anywhere).")
        print("  2. Pare-feu / réseau (port 27017, accès Internet).")
        return 1
    except Exception as e:
        print(f"Erreur connexion Atlas: {e}")
        return 1

    # 1) Solar (salar_data ou solar_data)
    solar_path1 = os.path.join(ROOT, "data", "solar_data.csv")
    solar_path2 = os.path.join(ROOT, "data", "salar_data.csv")
    if os.path.isfile(solar_path1):
        solar_path = solar_path1
    elif os.path.isfile(solar_path2):
        solar_path = solar_path2
    else:
        print("Avertissement: aucun data/solar_data.csv ni data/salar_data.csv trouvé.")
        solar_path = None
    if solar_path:
        df_solar = pd.read_csv(solar_path, sep=";")
        docs = _df_to_docs(df_solar)
        db[cfg.SOLAR_COLLECTION].delete_many({})
        db[cfg.SOLAR_COLLECTION].insert_many(docs)
        print(f"  solar: {len(docs)} documents -> {cfg.FLASH_DASH_DB}.{cfg.SOLAR_COLLECTION}")

    # 2) Assurance
    assurance_path = os.path.join(ROOT, "data", "assurance_data_1000.csv")
    if os.path.isfile(assurance_path):
        df_ins = pd.read_csv(assurance_path, sep=";")
        docs = _df_to_docs(df_ins)
        db[cfg.ASSURANCE_COLLECTION].delete_many({})
        db[cfg.ASSURANCE_COLLECTION].insert_many(docs)
        print(f"  assurance: {len(docs)} documents -> {cfg.FLASH_DASH_DB}.{cfg.ASSURANCE_COLLECTION}")
    else:
        print("Avertissement: data/assurance_data_1000.csv introuvable.")

    # 3) Hospital
    hospital_path = os.path.join(ROOT, "dashbord_pro", "data", "hospital_data (1).csv")
    if os.path.isfile(hospital_path):
        df_hosp = pd.read_csv(hospital_path, sep=";", encoding="utf-8")
        docs = _df_to_docs(df_hosp)
        db[cfg.HOSPITAL_COLLECTION].delete_many({})
        db[cfg.HOSPITAL_COLLECTION].insert_many(docs)
        print(f"  hospital: {len(docs)} documents -> {cfg.FLASH_DASH_DB}.{cfg.HOSPITAL_COLLECTION}")
    else:
        print("Avertissement: dashbord_pro/data/hospital_data (1).csv introuvable.")

    try:
        client.close()
    except Exception:
        pass
    print("OK: CSV envoyés vers MongoDB Atlas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
