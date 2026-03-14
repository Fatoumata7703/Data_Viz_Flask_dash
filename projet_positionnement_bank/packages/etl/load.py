# -*- coding: utf-8 -*-
"""
Load : chargement des données nettoyées dans la base bank_prod, collection prod.
"""
import pandas as pd
from pymongo import MongoClient

from config import (
    MONGO_URI,
    MONGO_DB_NAME_PROD,
    MONGO_COLLECTION_BANQUES_PROD,
)


def load_to_prod(df, client=None):
    """
    Charge le DataFrame nettoyé dans la base bank_prod, collection prod.
    Remplace toute la collection.
    Retourne le nombre de documents écrits.
    Si client est None, ouvre et ferme une connexion.
    """
    if df is None or len(df) == 0:
        return 0
    if client is None:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            n = _load(client, df)
        finally:
            client.close()
        return n
    return _load(client, df)


def _load(client, df):
    db = client[MONGO_DB_NAME_PROD]
    coll_prod = db[MONGO_COLLECTION_BANQUES_PROD]
    coll_prod.delete_many({})
    # Stockage en minuscules (convention Mongo)
    df_out = df.copy()
    rename_back = {
        "Sigle": "sigle",
        "ANNEE": "annee",
        "BILAN": "bilan",
        "Goupe_Bancaire": "groupe_bancaire",
    }
    df_out = df_out.rename(columns={k: v for k, v in rename_back.items() if k in df_out.columns})
    records = df_out.to_dict(orient="records")
    for r in records:
        for k, v in list(r.items()):
            if pd.isna(v):
                r[k] = None
            elif hasattr(v, "item"):
                r[k] = v.item()
    coll_prod.insert_many(records)
    return len(records)
