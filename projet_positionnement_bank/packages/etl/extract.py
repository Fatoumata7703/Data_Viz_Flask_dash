# -*- coding: utf-8 -*-
"""
Extract : lecture des données brutes depuis la collection banque (dev).
"""
import pandas as pd
from pymongo import MongoClient

from config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_BANQUES,
)


def extract_from_dev(client=None):
    """
    Extrait tous les documents de la collection banque (dev).
    Retourne un DataFrame ou None.
    Si client est None, ouvre et ferme une connexion.
    """
    if client is None:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            df = _extract(client)
        finally:
            client.close()
        return df
    return _extract(client)


def _extract(client):
    db = client[MONGO_DB_NAME]
    coll = db[MONGO_COLLECTION_BANQUES]
    records = list(coll.find({}))
    if not records:
        return None
    df = pd.DataFrame(records)
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    return df
