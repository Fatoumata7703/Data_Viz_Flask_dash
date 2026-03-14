# -*- coding: utf-8 -*-
"""
Vide les collections MongoDB du projet (bank.banque et bank_prod.prod).
Ne supprime pas le fichier Excel : il reste sur le disque pour recharger après.

Usage: python -m scripts.empty_mongo

Ensuite, recharger les données :
  1. python -m scripts.load_excel_to_mongo   (données Excel)
  2. python -m scripts.extract_pdf_to_mongo  (données PDF BCEAO, optionnel --force)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_DB_NAME_PROD,
    MONGO_COLLECTION_BANQUES,
    MONGO_COLLECTION_BANQUES_PROD,
)


def main():
    client = MongoClient(MONGO_URI)
    db_dev = client[MONGO_DB_NAME]
    db_prod = client[MONGO_DB_NAME_PROD]

    coll_banque = db_dev[MONGO_COLLECTION_BANQUES]
    coll_prod = db_prod[MONGO_COLLECTION_BANQUES_PROD]

    n_banque = coll_banque.count_documents({})
    n_prod = coll_prod.count_documents({})

    coll_banque.delete_many({})
    coll_prod.delete_many({})

    print(f"Base vidée (dev)  : {MONGO_DB_NAME}.{MONGO_COLLECTION_BANQUES} -> {n_banque} supprimé(s)")
    print(f"Base vidée (prod) : {MONGO_DB_NAME_PROD}.{MONGO_COLLECTION_BANQUES_PROD} -> {n_prod} supprimé(s)")
    print()
    print("Pour repartir de zéro, charger dans cet ordre :")
    print("  1. D'abord l'Excel  : python -m scripts.load_excel_to_mongo")
    print("  2. Ensuite les PDF : python -m scripts.extract_pdf_to_mongo   (ou --force)")


if __name__ == "__main__":
    main()
