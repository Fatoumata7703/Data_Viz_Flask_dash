# -*- coding: utf-8 -*-
"""
Charge le fichier Excel BASE_SENEGAL2.xlsx dans MongoDB.
Transfert direct : on ne supprime rien dans MongoDB, on insère les documents Excel.
Usage: python -m scripts.load_excel_to_mongo
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pymongo import MongoClient
from config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_BANQUES,
    EXCEL_FILE,
)


def load_excel():
    """Charge le fichier Excel et retourne un DataFrame."""
    if not os.path.exists(EXCEL_FILE):
        raise FileNotFoundError(f"Fichier introuvable: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    return df


def normalize_for_mongo(df):
    """
    Normalise le DataFrame pour MongoDB:
    - Noms de colonnes en minuscules, espaces remplacés par _
    - Types numériques et dates cohérents
    - Un document par ligne (banque + année) avec source = "excel"
    """
    df = df.copy()
    # Harmoniser les noms de colonnes
    df.columns = [
        c.strip().replace(" ", "_").replace(".", "_").lower()
        for c in df.columns
    ]
    # S'assurer que les colonnes clés existent (Sigle -> sigle, ANNEE -> annee, etc.)
    col_map = {}
    for c in df.columns:
        if "sigle" in c:
            col_map[c] = "sigle"
        elif "annee" in c or "année" in c:
            col_map[c] = "annee"
        elif "bilan" in c:
            col_map[c] = "bilan"
        elif "goupe" in c or "groupe" in c:
            col_map[c] = "groupe_bancaire"
    df = df.rename(columns={k: v for k, v in col_map.items() if k != v})
    # Convertir année en int
    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    # Ajouter la source
    df["source"] = "excel"
    return df


def insert_into_mongo(df):
    """Insère les documents dans MongoDB (transfert direct, on ne supprime rien)."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    coll = db[MONGO_COLLECTION_BANQUES]
    # Convertir chaque ligne en document
    records = df.to_dict(orient="records")
    # Nettoyer les NaN pour JSON/Mongo
    for r in records:
        for k, v in list(r.items()):
            if pd.isna(v):
                r[k] = None
            elif hasattr(v, "item"):  # numpy scalar
                r[k] = v.item()
    if records:
        coll.insert_many(records)
    return len(records)


def main():
    print("Chargement du fichier Excel...")
    df = load_excel()
    print(f"  Lignes lues: {len(df)}")
    print(f"  Colonnes: {list(df.columns)}")
    df = normalize_for_mongo(df)
    print("Insertion dans MongoDB...")
    n = insert_into_mongo(df)
    print(f"  {n} documents insérés dans {MONGO_DB_NAME}.{MONGO_COLLECTION_BANQUES}")
    print("Terminé.")


if __name__ == "__main__":
    main()
