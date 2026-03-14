# Dashboard Hospitalier - Analyse de performance

Dashboard interactif pour l'analyse de la prise en charge des patients à l'hôpital : qualité des soins, durée d'hospitalisation et maîtrise des coûts. Intégré à l'application Flash Dash sous la route `/pro`.

## 1. Vue d'ensemble

Le projet permet d'analyser les performances hospitalières selon plusieurs axes : organisation par département, analyse des pathologies, profils des patients, efficacité des traitements, gestion des risques et analyses statistiques avancées. L'interface est modulaire (layout et callbacks par section) et s'appuie sur Dash, Plotly et Pandas.

## 2. Fonctionnalités principales

### Indicateurs stratégiques (KPI)

- Durée moyenne de séjour
- Coût moyen par patient
- Coût par jour
- Coût par maladie
- Durée par traitement
- Patients à risque (séjour et coût au-dessus du 75ème percentile)

### Organisation hospitalière

- Coûts totaux par département
- Durée de séjour par département
- Coût par jour par département

### Pathologies

- Coûts totaux par pathologie
- Durée d'hospitalisation par pathologie
- Comparaison des performances entre pathologies

### Profil patient

- Impact de l'âge sur la durée de séjour
- Coût selon le sexe
- Analyse par groupes d'âge

### Traitements

- Coûts par type de traitement
- Efficacité (coût vs durée)
- Score d'efficacité (rapport coût/durée)

### Gestion des risques

- Liste des patients à risque (tableau interactif avec tri et filtres)
- Critères : séjour et coût supérieurs au 75ème percentile
- Analyse des départements et pathologies générateurs de risque

### Analyses avancées

- Corrélation durée de séjour / coût
- Statistiques descriptives (variance, médiane, écart-type, quartiles)
- Coefficient de variation
- Détection des valeurs aberrantes

## 3. Structure du projet

```
dashbord_pro/
├── app.py                      # Point d'entrée : create_dash_app(server, url_base_pathname)
├── utils.py                    # Traitement des données, calculs KPI, formatage
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
├── DOCUMENTATION.md            # Documentation détaillée des analyses
├── data/
│   └── hospital_data (1).csv   # Données hospitalières (secours si pas Atlas)
├── assets/
│   └── style.css               # Styles CSS
├── layout/
│   ├── __init__.py
│   ├── main_layout.py          # Assemblage du layout
│   ├── header_main.py           # En-tête
│   ├── sidebar.py               # Navigation latérale
│   ├── welcome_card.py
│   ├── stat_cards.py
│   ├── alert_card.py
│   ├── filters.py
│   ├── organization.py
│   ├── pathology.py
│   ├── patient.py
│   ├── treatment.py
│   ├── risk.py
│   ├── analytics.py
│   └── pages/
│       ├── home.py
│       ├── organization.py
│       ├── pathology.py
│       ├── patient.py
│       ├── treatment.py
│       ├── risk.py
│       └── analytics.py
└── callbacks/
    ├── __init__.py             # Enregistrement des callbacks
    ├── constants.py
    ├── navigation.py
    ├── clock.py
    ├── organization.py
    ├── pathology.py
    ├── patient.py
    ├── treatment.py
    ├── risk.py
    └── analytics.py
```

## 4. Données

- **MongoDB Atlas** (priorité) : base `flash_dash`, collection `hospital`. Définir `MONGO_URI` dans le fichier `.env` à la racine du projet Flash Dash.
- **Secours CSV** : si Atlas n’est pas disponible, les données sont lues depuis `data/hospital_data (1).csv`. Pour envoyer ce CSV vers Atlas une fois : à la racine du projet, `python upload_csv_to_atlas.py`.

### Format CSV

Colonnes attendues : PatientID, Age, Sexe, Departement, Maladie, DureeSejour, Cout, DateAdmission, DateSortie, Traitement. Le fichier doit être placé dans `data/` sous le nom `hospital_data (1).csv` ou le chemin doit être adapté dans `utils.py`.

### Filtres interactifs

Disponibles sur toutes les pages sauf l'accueil : Département, Pathologie, Traitement, Sexe, Âge (min/max). Les graphiques et statistiques se mettent à jour en temps réel selon les filtres.

## 5. Technologies utilisées

- Dash 2.14.2
- Plotly 5.18.0
- Pandas 2.1.3
- NumPy 1.26.2
- Dash Bootstrap Components 1.5.0

## 6. Installation et exécution

### Prérequis

- Python 3.9 ou supérieur

### Installation

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Lancement autonome (développement)

```bash
python app.py
```

Accès : http://127.0.0.1:8050

### Intégration Flash Dash

En production, le dashboard est monté sur le serveur Flask principal. Le répertoire `dashbord_pro` est ajouté au `sys.path` dans `app.py` (racine du dépôt) pour résoudre les imports (layout, callbacks, utils). La fonction `create_dash_app(server, '/pro/')` est appelée au démarrage ; l'utilisateur accède au dashboard via http://localhost:5000/pro.

## 7. Développement et personnalisation

- **Styles** : `assets/style.css`
- **Couleurs** : `callbacks/constants.py`
- **Nouvelle page** : ajouter un module dans `layout/pages/`, les callbacks dans `callbacks/`, les enregistrer dans `callbacks/__init__.py` et ajouter la route dans `app.py`.

Pour le détail de chaque page et analyse, voir `DOCUMENTATION.md`.

## 8. Licence et contexte

Projet à finalité éducative et d'analyse de données.
