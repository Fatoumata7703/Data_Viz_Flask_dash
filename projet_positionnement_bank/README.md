# Projet Positionnement des banques au Sénégal

Dashboard Dash pour l’analyse du positionnement des banques au Sénégal : indicateurs agrégés ou par banque, graphiques de positionnement et de comparaison, analyse financière, et génération de rapports HTML à partir d’un notebook Jupyter.

## 1. Vue d’ensemble

L’application permet de visualiser les données bancaires (bilans, emplois, ressources, fonds propres) par année et par banque, de comparer les établissements, d’afficher des fiches individuelles et d’exporter un rapport HTML complet lorsqu’une banque est sélectionnée. Les données sont chargées depuis la base MongoDB de production (`bank_prod.prod`). En l’absence de MongoDB ou si la collection est vide, le dashboard démarre avec un DataFrame vide (les scripts d’import Excel/PDF permettent de peupler la base).

## 2. Données et chargement

### Source

- **MongoDB** : base `bank_prod`, collection `prod`. Configuration dans `config.py` (`MONGO_URI`, `MONGO_DB_NAME_PROD`, `MONGO_COLLECTION_BANQUES_PROD`). Le fichier `.env` du projet est chargé au démarrage pour définir `MONGO_URI` (connexion Atlas en production).
- **Normalisation** : le module `data_loader.py` charge les documents, supprime `_id`, et normalise les noms de colonnes (sigle, annee, bilan, groupe_bancaire, emploi, ressources, etc.) pour un usage homogène dans le dashboard.

### Base de référence Excel (import initial)

- Fichier : `data/BASE_SENEGAL2.xlsx` (colonnes : Sigle, ANNEE, BILAN, Goupe_Bancaire, etc.).
- Chargement dans MongoDB : `python -m scripts.load_excel_to_mongo` (depuis la racine du projet ou avec le chemin Python adapté).

### Données BCEAO (optionnel)

- Scripts : `scripts/bceao_scraper.py` (liens PDF), `scripts/extract_pdf_to_mongo.py` (extraction des tableaux et insertion en base).
- Les fascicules PDF BCEAO sont téléchargés dans `data/bceao_pdfs/`. L’extraction peut utiliser pdfplumber ou OCR (Tesseract) selon les besoins.

## 3. Structure du projet

```
projet_positionnement_bank/
├── config.py                 # URI MongoDB, chemins, constantes
├── data_loader.py            # Chargement des données (MongoDB)
├── app_bank.py               # Application Dash (navbar, filtres, pages, callbacks)
├── assets/
│   └── custom.css            # Styles (navbar, filtres, cartes KPI, graphiques, toast, contours)
├── data/
│   ├── BASE_SENEGAL2.xlsx    # Base de référence (import Mongo)
│   └── bceao_pdfs/           # PDF téléchargés BCEAO
├── generate_rapport/
│   ├── convert_to_html.py    # Conversion notebook -> HTML, remplacement placeholders, surlignage banque
│   └── sommaire.py           # Table des matières
├── graphiques/               # Modules de graphiques (positionnement, scatter, etc.)
├── rapport.ipynb             # Notebook exécuté pour générer le rapport
├── scripts/
│   ├── load_excel_to_mongo.py
│   ├── bceao_scraper.py
│   ├── extract_pdf_to_mongo.py
│   └── sync_local_to_atlas.py   # Sync prod locale -> MongoDB Atlas
└── packages/                 # ETL, transformations (optionnel)
```

## 4. Interface et fonctionnalités

### Barre de navigation (navbar)

- Liens : Vue d’ensemble, Positionnement, Comparaison, Analyse Financière, Rapport.
- Sous-titre dynamique (année courante ou sélectionnée).

### Filtres

- **Année** : dropdown (liste des années présentes en base).
- **Indicateur** : Total Bilan, Emplois, Ressources, Fonds Propres (selon colonnes disponibles).
- **Banque** : dropdown avec placeholder « Toutes les banques » ; valeur vide = agrégat secteur.
- **Bouton Rapport** : unique point d’export ; présent dans la barre de filtres pour être accessible depuis tous les onglets. Au clic, si aucune banque n’est sélectionnée, un toast invite à sélectionner une banque ; sinon déclenche le téléchargement du rapport HTML.

La barre de filtres est dimensionnée pour utiliser toute la largeur (colonnes Bootstrap réparties sur 12 unités) afin d’éviter une zone vide à droite. Styles : `bk-filter-bar`, `bk-filter-col`, `bk-filter-btn` (définis dans `assets/custom.css`).

### Pages

- **Vue d’ensemble** : six blocs KPI réactifs aux filtres (année, indicateur, banque). Sans banque = agrégat secteur ; avec banque = données de la banque sélectionnée. Graphiques de synthèse (évolution, répartition).
- **Positionnement** : graphiques de positionnement (part de marché, TCAM, groupes), comparaisons inter-banques.
- **Comparaison** : tableaux et graphiques comparatifs.
- **Analyse Financière** : structure bilan, emplois, ressources.
- **Rapport** : titre « Rapport de positionnement », texte d’aide indiquant d’utiliser le bouton « Rapport » de la barre de filtres pour télécharger le rapport ; carte « Fiche banque — Indicateurs clés » en pleine largeur ; graphiques « Évolution de la banque sélectionnée » et « Position dans le classement ». Aucun second bouton de téléchargement sur cette page (éviter la redondance avec le bouton de la barre).

### KPIs et graphiques

- Cartes KPI avec style « pastel » : fond en dégradé léger, bordure gauche épaisse colorée, contour discret (1 px), coins arrondis.
- Cartes de graphiques : fond blanc, contour 1 px discret, bordures cohérentes avec le thème (teal / bleu).
- Tous les graphiques et KPIs dépendent du store `store-filters` (annee, indicateur, banque, groupe).

## 5. Génération du rapport HTML

### Workflow

1. L’utilisateur sélectionne une banque dans le filtre et clique sur « Rapport » (barre de filtres).
2. Si aucune banque n’est sélectionnée : un toast s’affiche (« Veuillez sélectionner une banque ») et aucun fichier n’est téléchargé.
3. Si une banque est sélectionnée : le module `generate_rapport.convert_to_html` est utilisé. Il exécute le notebook `rapport.ipynb` en injectant `banque_selectionnee` et éventuellement `annee_rapport`, exporte le notebook en HTML, puis applique les post-traitements décrits ci-dessous.

### Post-traitements (convert_to_html.py)

- **Remplacement des variables techniques** : dans le HTML généré, les chaînes `{banque_rapport}` et `{annee_cible}` sont remplacées par le nom de la banque sélectionnée et l’année utilisée, afin qu’aucun libellé technique n’apparaisse dans le rapport final.
- **Mise en évidence de la banque dans les tableaux** : la fonction `_highlight_banque_in_tables` parcourt tous les tableaux du HTML, repère la ligne dont la première cellule (ou une cellule) correspond au sigle de la banque sélectionnée, et applique un style (fond teal léger, police en gras) pour mettre en couleur la ligne de la banque dans le tableau comparatif détaillé et les autres tableaux concernés.
- **Nettoyage** : suppression des sorties techniques (tracebacks, messages de figure, etc.) via `_clean_html_technical_output`.

### Fichiers générés

- Rapport HTML téléchargeable (nom du fichier incluant la banque et un horodatage). Le contenu est un document autonome (header, styles, sommaire, contenu du notebook, footer).

## 6. Toast et styles

- **Toast « Veuillez sélectionner une banque »** : affiché lorsqu’on clique sur « Rapport » sans banque sélectionnée. Style : fond blanc, contour 2 px (teal discret), pas de header, icône et texte dans un bloc compact (classes `bk-toast-report`, styles dans `custom.css`).
- **Contours** : cartes (filtres, KPI, graphiques) et toast utilisent des contours 1 px ou 2 px discrets (couleurs du thème) pour une séparation visuelle sans surcharge.

## 7. Lancement et intégration

### Prérequis

- Python 3.8+
- MongoDB (local ou distant) avec base et collection configurées dans `config.py`, ou variables d’environnement pour `MONGO_URI`.
- Dépendances : pandas, dash, plotly, dash-bootstrap-components, pymongo, nbformat, nbconvert, beautifulsoup4, etc. (voir `requirements.txt` à la racine du dépôt).

### Lancer le dashboard seul (optionnel)

Depuis la racine du dépôt Flash_dash (ou en ajoutant le chemin au PYTHONPATH) :

```bash
python -m projet_positionnement_bank.app_bank
```

Ou depuis `projet_positionnement_bank` :

```bash
python app_bank.py
```

En production, le dashboard est monté sur l’application Flask principale : `app.py` appelle `create_dash_app(server, '/bank/')` et la route `/bank` sert la page du dashboard bancaire.

### Ordre d’exécution recommandé (données)

1. Démarrer MongoDB ou configurer `MONGO_URI`.
2. Charger l’Excel dans MongoDB : `python -m scripts.load_excel_to_mongo` (en adaptant le module path selon la racine du projet).
3. Optionnel : scraper BCEAO et extraire les PDF avec `scripts/bceao_scraper.py` et `scripts/extract_pdf_to_mongo.py`.

## 8. Déploiement

Pour la mise en production (MongoDB Atlas, hébergement de l’app Flask), voir le fichier `DEPLOY.md` à la racine du dépôt. La variable d’environnement `MONGO_URI` doit être définie sur la plateforme de déploiement ; ne pas commiter l’URI dans le code.

### Synchroniser la prod locale vers Atlas

Pour envoyer le contenu de la base prod locale (`bank_prod.prod`) vers MongoDB Atlas :

1. Définir `MONGO_URI` avec l’URI de votre cluster Atlas (cible).
2. Depuis `projet_positionnement_bank` :  
   `python -m scripts.sync_local_to_atlas`

Le script lit toute la collection `prod` en local (par défaut `mongodb://localhost:27017`), remplace le contenu de la collection `prod` sur Atlas, puis affiche le nombre de documents envoyés. Optionnel : `LOCAL_MONGO_URI` pour une source locale différente.

### Sync local → Atlas

Pour envoyer le contenu de la base prod locale vers MongoDB Atlas (une fois ou à la demande) :

1. Définir `MONGO_URI` avec l’URI Atlas (ex. PowerShell : `$env:MONGO_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"`).
2. Depuis `projet_positionnement_bank` : `python -m scripts.sync_local_to_atlas`.

Le script lit `bank_prod.prod` en local (`localhost:27017` ou `LOCAL_MONGO_URI`), remplace le contenu de la collection `prod` sur Atlas par ces documents, puis quitte.

## 9. Résumé des réalisations

- Dashboard multi-pages (Vue d’ensemble, Positionnement, Comparaison, Analyse Financière, Rapport) avec navbar et filtres globaux.
- Filtres Année / Indicateur / Banque avec barre alignée et sans zone vide à droite ; un seul bouton « Rapport » dans la barre, visible sur tous les onglets.
- KPIs et graphiques réactifs au filtre banque (agrégat secteur ou banque seule).
- Génération de rapport HTML à partir du notebook avec injection de la banque et de l’année, remplacement des placeholders techniques, surlignage de la banque dans les tableaux.
- Toast d’information si tentative de rapport sans banque sélectionnée.
- Styles cohérents (thème bleu/teal), contours discrets, cartes KPI et graphiques homogènes.
- Contenu pleine largeur (max-width 100 %) pour utiliser tout l’espace horizontal disponible.
