# -*- coding: utf-8 -*-
"""
Lance le pipeline ETL (packages.etl) pour remplir la base prod à partir de la base dev.
Extract (bank.banque) -> Transform (nettoyage) -> Load (bank_prod.prod).

Usage: python -m scripts.data_clean_to_prod
Depuis projet_positionnement_bank: python -m scripts.data_clean_to_prod
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MONGO_DB_NAME, MONGO_DB_NAME_PROD, MONGO_COLLECTION_BANQUES, MONGO_COLLECTION_BANQUES_PROD
from packages.etl import run_etl


def main():
    print("ETL : Extract (dev) -> Transform (nettoyage) -> Load (prod)")
    print("-" * 50)
    n_extracted, n_transformed, n_loaded, missing_report = run_etl()
    if n_extracted == 0:
        print(f"Aucune donnée dans {MONGO_COLLECTION_BANQUES} (dev).")
        print("Exécuter d'abord: load_excel_to_mongo puis extract_pdf_to_mongo.")
        return 0
    print(f"Extract  : {n_extracted} documents lus depuis {MONGO_DB_NAME}.{MONGO_COLLECTION_BANQUES} (dev).")
    print(f"Transform: {n_transformed} lignes après nettoyage.")
    print(f"Load     : {n_loaded} documents écrits dans {MONGO_DB_NAME_PROD}.{MONGO_COLLECTION_BANQUES_PROD} (prod).")
    if missing_report:
        print("-" * 50)
        print("Données manquantes (avant / après imputation):")
        for col, stats in sorted(missing_report.items()):
            before = stats.get("missing_before", 0)
            imputed = stats.get("imputed", 0)
            restant = before - imputed
            print(f"  {col}: {before} manquants -> {imputed} imputés (médiane/mode par sigle), {restant} restants")
    print("-" * 50)
    print("Terminé. Le dashboard et les rapports utilisent la base prod.")


if __name__ == "__main__":
    main()
