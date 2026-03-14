# Flash Dash - Application de visualisation multi-secteurs

Application web centralisant quatre dashboards de visualisation de données (Photovoltaïque, Assurance, Bancaire, Hospitalier), servie par un serveur Flask unique et une page d'accueil avec navigation vers chaque secteur.

## Vue d'ensemble

Flash Dash est le conteneur principal du projet Data_Viz. Il assure le routage HTTP, le montage des applications Dash sur des préfixes dédiés, et la fourniture des templates HTML pour chaque dashboard. Les quatre modules métier (Photovoltaïque, Assurance, Bancaire, Hospitalier) sont chargés comme sous-applications et restent techniquement et fonctionnellement indépendants.

## Architecture

- **Flask** : serveur WSGI unique, port par défaut 5000.
- **Dash** : chaque dashboard est une instance Dash montée sur le serveur Flask via `create_dash_app(server, url_base_pathname)`.
- **Templates** : pages HTML (Jinja2) pour l’accueil et le chargement des iframes/redirections vers chaque dashboard.

## Données : MongoDB Atlas

Les quatre dashboards sont alimentés par **MongoDB Atlas** lorsque la variable d’environnement `MONGO_URI` est définie (fichier `.env` à la racine ou variables d’hébergement) :

| Dashboard      | Base Atlas      | Collection   |
|----------------|-----------------|--------------|
| Photovoltaïque | `flash_dash`    | `solar`      |
| Assurance      | `flash_dash`    | `assurance`  |
| Bancaire       | `bank_prod`     | `prod`       |
| Hospitalier    | `flash_dash`    | `hospital`  |

- Script d’envoi des CSV vers Atlas (solaire, assurance, hospital) : `python upload_csv_to_atlas.py` (à lancer une fois après avoir défini `MONGO_URI` dans `.env`).
- Sync de la prod bancaire locale vers Atlas : `python -m projet_positionnement_bank.scripts.sync_local_to_atlas` (voir `projet_positionnement_bank/README.md`).

## Structure du dépôt

```
Flash_dash/
├── app.py                    # Point d'entrée Flask : création des 4 apps Dash, routes /
├── run.py                    # Lancement du serveur (app:server, port 5000)
├── wsgi.py                   # Point d'entrée WSGI pour déploiement (AlwaysData, etc.)
├── config_mongo.py           # Config MongoDB Atlas partagée (charge .env)
├── upload_csv_to_atlas.py    # Envoi des CSV solaire/assurance/hospital vers Atlas
├── .env.example              # Modèle pour .env (MONGO_URI) — ne pas commiter .env
├── requirements.txt          # Dépendances Python globales
├── README.md                 # Ce fichier
├── DEPLOY.md                 # Guide de déploiement (MongoDB Atlas, AlwaysData, Render, etc.)
├── templates/                # Templates HTML
│   ├── index.html            # Page d'accueil avec liens vers les 4 dashboards
│   ├── dash1.html            # Frame / redirection Dashboard Photovoltaïque
│   ├── dash2.html            # Frame / redirection Dashboard Assurance
│   ├── bank.html             # Frame / redirection Dashboard Bancaire
│   ├── pro.html              # Frame / redirection Dashboard Hospitalier
│   └── a_propos.html         # Page "À propos" (accessible depuis les dashboards)
├── static/                   # Fichiers statiques (CSS, etc.) pour les templates
├── dashboard/                # Projet 1 et 2 : Photovoltaïque (dash1), Assurance (dash2)
│   ├── dash1.py
│   ├── dash2.py
│   └── assets/
├── projet_positionnement_bank/  # Projet 3 : Dashboard Bancaire
│   ├── app_bank.py
│   ├── data_loader.py
│   ├── generate_rapport/
│   ├── graphiques/
│   └── ...
└── dashbord_pro/             # Projet 4 : Dashboard Hospitalier
    ├── app.py
    ├── layout/
    ├── callbacks/
    └── ...
```

## URLs et routes

| Route        | Template     | Description                              |
|-------------|--------------|------------------------------------------|
| `/`         | index.html   | Page d'accueil avec liens vers les 4 dashboards |
| `/dash1`    | dash1.html   | Dashboard Photovoltaïque (production solaire)   |
| `/dash2`    | dash2.html   | Dashboard Assurance (sinistres, assurés)       |
| `/bank`     | bank.html    | Dashboard Bancaire (positionnement Sénégal)     |
| `/pro`      | pro.html     | Dashboard Hospitalier (performance, traitements)|
| `/a-propos` | a_propos.html| Page "À propos" des quatre dashboards           |

Les applications Dash sont montées sur les préfixes suivants (utilisés en iframe ou redirection) : `/dash1/`, `/dash2/`, `/bank/`, `/pro/`.

## Prérequis et installation

- Python 3.8 ou supérieur
- Environnement virtuel recommandé

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Les dépendances incluent Flask, Dash, dash-bootstrap-components, pandas, plotly, pymongo (pour le module bancaire), et les bibliothèques utilisées par chaque sous-projet (voir leurs README respectifs).

## Lancement

```bash
python run.py
```

Le serveur écoute par défaut sur `http://0.0.0.0:5000`. Messages affichés au démarrage :

- Page d'accueil : http://localhost:5000/
- Dashboard Photovoltaïque : http://localhost:5000/dash1
- Dashboard Assurance : http://localhost:5000/dash2
- Dashboard Bancaire : http://localhost:5000/bank
- Dashboard Hospitalier : http://localhost:5000/pro

## Intégration des sous-projets

Chaque sous-projet expose une fonction `create_dash_app(server, url_base_pathname)` appelée dans `app.py` :

- `dashboard.dash1.create_dash_app` pour Photovoltaïque (`/dash1/`)
- `dashboard.dash2.create_dash_app` pour Assurance (`/dash2/`)
- `projet_positionnement_bank.app_bank.create_dash_app` pour Bancaire (`/bank/`)
- `dashbord_pro.app.create_dash_app` pour Hospitalier (`/pro/`)

Le répertoire `dashbord_pro` est ajouté au `sys.path` dans `app.py` pour résoudre les imports absolus (layout, callbacks, utils).

## Page À propos

La route `/a-propos` affiche une page détaillée (templates/a_propos.html) décrivant les quatre dashboards, leur objectif et les indicateurs principaux. Elle est accessible depuis la navigation des dashboards (liens "À propos" dans les barres de menu). Le style et le contenu sont définis dans les templates et les fichiers CSS statiques associés.

## Déploiement

Voir `DEPLOY.md` pour la configuration MongoDB (Atlas), le déploiement (AlwaysData avec `wsgi.py`, Render, Railway, VPS), la définition des variables d’environnement (`MONGO_URI` pour les quatre dashboards) et l’utilisation de Gunicorn en production.

## Documentation des projets

- **Dashboard Photovoltaïque et Assurance** : `dashboard/README.md`
- **Projet Positionnement Bancaire** : `projet_positionnement_bank/README.md`
- **Dashboard Hospitalier** : `dashbord_pro/README.md`
