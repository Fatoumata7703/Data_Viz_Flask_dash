# Conformité au cahier des charges — Data Visualisation Bancaire (Sénégal)

## 1. Partie Données

| Exigence | Statut | Détail |
|----------|--------|--------|
| Source principale : base_senegal2 | ✅ | Fichier Excel `data/BASE_SENEGAL2.xlsx` chargé via `load_excel_to_mongo` puis ETL. |
| Centraliser les données dans MongoDB | ✅ | `config.py` : bases `bank` (dev) et `bank_prod` (nettoyée). `data_loader.get_data()` lit en priorité `bank_prod.prod`. |
| Compléments : extraction PDF BCEAO | ✅ | `scripts/extract_pdf_to_mongo.py` : web scraping (`bceao_scraper`) + extraction PDF (pdfplumber + OCR optionnel Tesseract). Colonnes normalisées alignées sur l’Excel. |
| Nettoyage et structuration | ✅ | Pipeline ETL dans `packages/etl/` : extract, transform (harmonisation, imputation), load vers `bank_prod.prod`. |

---

## 2. Dashboard

| Exigence | Statut | Détail |
|----------|--------|--------|
| KPI : Bilan (actif, passif, capital) | ✅ | BILAN utilisé dans le dashboard et les rapports. |
| KPI : Emploi (placements, crédits, investissements) | ✅ | Colonne EMPLOI si présente (Excel/ETL). Filtre « Indicateur » dans le dashboard. |
| KPI : Fonds propres | ✅ | FONDS_PROPRES si présent dans les données. Proposé dans le filtre indicateur. |
| KPI : Ressources (dépôts, emprunts, financement) | ✅ | RESSOURCES si présent. Filtre indicateur. |
| KPI : Analyse financière (ratios) | ⚠️ | Ratios (solvabilité, liquidité, rentabilité) non calculés dans le dashboard ; à ajouter à partir des colonnes disponibles (ex. résultat_net, bilan). |
| Visualisation KPI par banque et par année | ✅ | Filtres Année + Indicateur ; graphique « Comparaison par banque » et rapports par banque. |
| Comparaison interbancaire | ✅ | Graphique en barres par banque ; graphique positionnement par groupe. |
| Téléchargement rapports PDF (positionnement banque) | ⚠️ | Téléchargement **HTML** (rapport issu du notebook). Export PDF possible en bonus (impression navigateur ou librairie). |
| Interactivité : filtres (année, banque, type d’indicateur) | ✅ | Filtres Année, Indicateur, Banque (pour le rapport). |
| Carte interactive du Sénégal (localisation + positionnement) | ⚠️ | **Placeholder** dans l’interface. Intégration carte nécessite coordonnées (lat/long) par banque/agence. |

---

## 3. Intégration Multi-Secteurs

| Exigence | Statut | Détail |
|----------|--------|--------|
| Flask pour orchestrer plusieurs dashboards | ❌ | Une seule app **Dash** (`app_bank.py`) pour le secteur bancaire. Pas d’orchestration Flask (secteurs énergétique, assurance) dans ce dépôt. |
| Socle technique commun (MongoDB + Dash + Flask) | ⚠️ | MongoDB + Dash en place. Flask non utilisé ; à ajouter si multi-secteurs requis. |

---

## 4. Déploiement et Bonnes Pratiques

| Exigence | Statut | Détail |
|----------|--------|--------|
| Déploiement (Heroku / Render / Railway) | ⚠️ | À faire : Procfile / Docker / variables d’environnement (MONGO_URI, etc.). |
| MongoDB accessible et mise à jour des données | ✅ | Scripts ETL et `extract_pdf_to_mongo` pour alimenter et mettre à jour les données. |
| Projet sur GitHub | ⚠️ | À héberger et à documenter (README). |
| README (structure, lancement, sources) | ⚠️ | À rédiger ou compléter (structure, étapes de lancement, sources de données et extraction PDF). |
| Code commenté et lisible | ✅ | Commentaires dans les scripts principaux (ETL, extraction PDF, `app_bank`, `data_loader`). |
| Tests unitaires (intégrité des données) | ⚠️ | À formaliser (pytest sur chargement, ETL, cohérence des colonnes). |
| Nettoyage des données après extraction PDF | ✅ | ETL (transform, imputation, seuils) avant chargement en prod. |
| UI/UX professionnelle avec dash-bootstrap-components | ✅ | Dashboard avec `dash-bootstrap-components`, cartes KPI, filtres, graphiques Plotly. |

---

## 5. Bonus / Extensions

| Exigence | Statut | Détail |
|----------|--------|--------|
| Automatisation extraction nouveaux rapports BCEAO | ⚠️ | Scripts manuels (`bceao_scraper`, `extract_pdf_to_mongo`). Cron / tâche planifiée à mettre en place. |
| Module prédictif (positionnement futur) | ❌ | Non implémenté. |
| Export rapports PDF ou Excel | ⚠️ | Export HTML en place ; PDF/Excel en bonus (ex. weasyprint / openpyxl). |

---

## Synthèse

- **Données et ETL** : conformes (MongoDB, Excel, PDF BCEAO, nettoyage, prod).
- **Dashboard** : KPI de base (Bilan, Emploi, Fonds propres, Ressources) et interactivité en place ; à compléter : ratios financiers explicites, export PDF, carte avec géolocalisation.
- **Multi-secteurs** : non réalisé (Flask + autres secteurs à développer).
- **Déploiement et qualité** : README, déploiement, tests à finaliser ; UI professionnelle avec Bootstrap en place.

La data visualisation vise à faire parler les données pour des décisions claires : le dashboard permet de comparer les banques et les groupes, de filtrer par année et indicateur, et de générer un rapport par banque.
