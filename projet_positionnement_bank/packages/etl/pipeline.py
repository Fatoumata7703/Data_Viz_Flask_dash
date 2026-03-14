# -*- coding: utf-8 -*-
"""
Pipeline ETL : Extract -> Transform -> Load.
Exécute le flux complet pour alimenter la base prod à partir de la base dev.
"""
from pymongo import MongoClient

from config import MONGO_URI, MONGO_COLLECTION_BANQUES, MONGO_COLLECTION_BANQUES_PROD
from .extract import extract_from_dev
from .transform import transform_clean
from .load import load_to_prod


def run_etl():
    """
    Lance le pipeline ETL complet.
    Retourne (n_extracted, n_transformed, n_loaded, missing_report) ou (0, 0, 0, {}) en cas d'erreur.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
    except Exception:
        return 0, 0, 0, {}

    # Extract
    df_raw = extract_from_dev(client)
    n_extracted = len(df_raw) if df_raw is not None else 0
    if n_extracted == 0:
        client.close()
        return 0, 0, 0, {}

    # Transform (avec rapport des manquants)
    df_clean, missing_report = transform_clean(df_raw, return_report=True)
    n_transformed = len(df_clean) if df_clean is not None else 0
    if n_transformed == 0:
        client.close()
        return n_extracted, 0, 0, {}

    # Load
    n_loaded = load_to_prod(df_clean, client=client)
    client.close()
    return n_extracted, n_transformed, n_loaded, missing_report
