# -*- coding: utf-8 -*-
"""
Synchronise la base prod locale vers MongoDB Atlas.
Lit bank_prod.prod en local (localhost) et envoie tout le contenu vers Atlas
(même base bank_prod, même collection prod).

Usage:
  Depuis projet_positionnement_bank (avec MONGO_URI défini pour Atlas):
    python -m scripts.sync_local_to_atlas

  Ou depuis la racine du repo:
    cd projet_positionnement_bank && python -m scripts.sync_local_to_atlas

Variables d'environnement (ou fichier .env à la racine du projet bancaire):
  MONGO_URI       : URI MongoDB Atlas (obligatoire pour la cible).
  LOCAL_MONGO_URI : URI MongoDB local (défaut: mongodb://localhost:27017).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger .env du projet si présent (MONGO_URI, LOCAL_MONGO_URI)
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value


_load_dotenv()

from pymongo import MongoClient

from config import (
    MONGO_DB_NAME_PROD,
    MONGO_COLLECTION_BANQUES_PROD,
)


LOCAL_URI = os.environ.get("LOCAL_MONGO_URI", "mongodb://localhost:27017")


def main():
    atlas_uri = os.environ.get("MONGO_URI", "").strip()
    if not atlas_uri or atlas_uri == LOCAL_URI:
        print("Erreur: définir MONGO_URI (URI MongoDB Atlas) pour la cible.")
        print("Exemple (PowerShell): $env:MONGO_URI = 'mongodb+srv://user:pass@cluster.mongodb.net/'")
        return 1

    print("Sync local -> Atlas")
    print(f"  Source : {LOCAL_URI} / {MONGO_DB_NAME_PROD}.{MONGO_COLLECTION_BANQUES_PROD}")
    print(f"  Cible  : Atlas ({MONGO_DB_NAME_PROD}.{MONGO_COLLECTION_BANQUES_PROD})")

    # Lire depuis le local
    try:
        client_local = MongoClient(LOCAL_URI, serverSelectionTimeoutMS=5000)
        db_local = client_local[MONGO_DB_NAME_PROD]
        coll_local = db_local[MONGO_COLLECTION_BANQUES_PROD]
        docs = list(coll_local.find({}))
        client_local.close()
    except Exception as e:
        print(f"Erreur lecture locale: {e}")
        return 1

    if not docs:
        print("Aucun document en local. Rien à envoyer.")
        return 0

    # Retirer _id pour que Atlas génère les siens (évite conflits de clés)
    for d in docs:
        d.pop("_id", None)

    # Envoyer vers Atlas (remplacer le contenu de la collection)
    try:
        client_atlas = MongoClient(atlas_uri, serverSelectionTimeoutMS=10000)
        db_atlas = client_atlas[MONGO_DB_NAME_PROD]
        coll_atlas = db_atlas[MONGO_COLLECTION_BANQUES_PROD]
        coll_atlas.delete_many({})
        coll_atlas.insert_many(docs)
        client_atlas.close()
    except Exception as e:
        print(f"Erreur écriture Atlas: {e}")
        return 1

    print(f"OK: {len(docs)} documents envoyés vers Atlas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
