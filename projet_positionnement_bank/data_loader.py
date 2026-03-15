# -*- coding: utf-8 -*-
"""
Charge les données depuis la base MongoDB PROD pour le dashboard.
Source unique : bank_prod.prod — pas d’Excel, pas de base dev.
"""
import pandas as pd

try:
    from pymongo import MongoClient
    try:
        from .config import (
            MONGO_URI,
            MONGO_DB_NAME_PROD,
            MONGO_COLLECTION_BANQUES_PROD,
        )
    except ImportError:
        from config import (
            MONGO_URI,
            MONGO_DB_NAME_PROD,
            MONGO_COLLECTION_BANQUES_PROD,
        )
    _MONGO_AVAILABLE = True
except Exception:
    _MONGO_AVAILABLE = False


def _load_from_collection(coll):
    cursor = coll.find({})
    records = list(cursor)
    if not records:
        return None
    df = pd.DataFrame(records)
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    return df


def get_data():
    """
    Charge les données depuis la base PROD (bank_prod.prod) uniquement.
    C’est la base prod qui alimente le dashboard.
    """
    if not _MONGO_AVAILABLE:
        return None
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=500, connectTimeoutMS=500)
        db = client[MONGO_DB_NAME_PROD]
        coll = db[MONGO_COLLECTION_BANQUES_PROD]
        df = _load_from_collection(coll)
        client.close()
        if df is None or len(df) == 0:
            return None
        # Normaliser les noms de colonnes
        renames = {}
        for c in list(df.columns):
            c_str = str(c).strip()
            if c_str.lower() == "sigle" and "Sigle" not in df.columns:
                renames[c] = "Sigle"
            elif c_str.lower() in ("annee", "année") and "ANNEE" not in df.columns:
                renames[c] = "ANNEE"
            elif c_str.lower() == "bilan" and "BILAN" not in df.columns:
                renames[c] = "BILAN"
            elif ("groupe" in c_str.lower() or "goupe" in c_str.lower()) and "Goupe_Bancaire" not in df.columns:
                renames[c] = "Goupe_Bancaire"
            elif c_str.lower() == "emploi" and "EMPLOI" not in df.columns:
                renames[c] = "EMPLOI"
            elif c_str.lower() == "ressources" and "RESSOURCES" not in df.columns:
                renames[c] = "RESSOURCES"
            elif c_str.lower() == "compte" and "COMPTE" not in df.columns:
                renames[c] = "COMPTE"
        if renames:
            df = df.rename(columns=renames)
        return df
    except Exception:
        return None
