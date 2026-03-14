# Dashboards Photovoltaïque et Assurance

Ce répertoire contient deux applications Dash intégrées à l’application Flash Dash : le **Dashboard Photovoltaïque** (dash1) pour le suivi de la production d’énergie solaire, et le **Dashboard Assurance** (dash2) pour l’analyse des sinistres et du profil des assurés.

---

## 1. Dashboard Photovoltaïque (dash1)

### Objectif

Suivi et analyse de la production d’énergie solaire : production AC/DC, efficacité, impact de l’environnement (température, irradiation), détection d’anomalies et analyses avancées (prévisions, décomposition, outliers).

### Données

- **MongoDB Atlas** (priorité) : base `flash_dash`, collection `solar`. Définir `MONGO_URI` dans le fichier `.env` à la racine du projet.
- **Secours CSV** : `data/solar_data.csv` ou `data/salar_data.csv` si Atlas n’est pas disponible.
- Pour envoyer les CSV vers Atlas une fois : à la racine du projet, `python upload_csv_to_atlas.py`.
- Colonnes utilisées : `DateTime`, `Date`, `Hour` (ou `Time`), `AC_Power`, `DC_Power`, `Module_Temperature`, `Ambient_Temperature`, `Irradiation` (optionnel), `Country` (optionnel pour filtre site).
- Efficacité calculée : `Efficiency = AC_Power / DC_Power * 100` lorsque `DC_Power > 0`.

### Structure des pages

- **Vue d’ensemble** : production horaire AC vs DC, production journalière, cumulée, efficacité dans le temps, bloc IA Insights.
- **Performance** : efficacité AC/DC avec seuil 90 %, distribution du rendement (stats Moy./Méd./sigma + histogramme), Top 5 / Pire 5 jours, moyennes mobiles 7j et 30j, comparaison périodes, production moyenne par heure.
- **Environnement** : température module vs production (corrélation Pearson), température ambiante vs efficacité (zone optimale), production par plage de température, heatmap horaire (Heure x Date), impact irradiation.
- **Anomalies** : KPIs (% prod. nulle, nb incidents, durée moyenne panne, plus longue panne), production nulle en journée (8h–18h), efficacité inférieure à 80 %, tableau des incidents, anomalies par mois.
- **Analyse avancée** : prévision (MA 7j + projection 30j), outliers (IQR), décomposition (tendance, saisonnalité, résidu), performance annuelle comparée.

### Filtres

- Plage de dates : Du / Au (DatePickerSingle).
- Presets : 7j, 30j, 90j, Année, Tout.
- Site : dropdown optionnel (colonne `Country`).

Les filtres mettent à jour un store `applied-filters` (start, end, site) ; tous les callbacks (KPIs, graphiques) lisent ce store pour filtrer les données.

### KPIs (Vue d’ensemble)

Production AC totale, production DC totale, rendement AC/DC (%), production moyenne par heure, % anomalies (créneaux nuls), température module.

### Réalisation technique

- **Conteneurs à hauteur fixe** : sur les pages Performance et Environnement, les graphiques sont dans des divs à hauteur fixe (ex. 380px, 300px, 420px) et les zones de stats (ex. corrélation, Moy./Méd./sigma) ont une `min-height` réservée pour éviter les décalages au chargement (pas de « bougé » vers le bas).
- **Export PDF** : bouton « Exporter PDF » dans le header (navbar) ; déclenche `window.print()` pour enregistrer en PDF via le navigateur. Pas d’export Excel.
- **Thème** : palette solaire (terracotta, ambre, or), cartes KPI avec bordure gauche épaisse colorée, cartes de graphiques avec style cohérent (custom_dash1.css).
- **Sidebar** : navigation entre les 5 pages (Overview, Performance, Environnement, Anomalies, Analyse avancée) avec mise en surbrillance de l’onglet actif.

### Fichiers principaux

- `dash1.py` : application Dash (layout, callbacks, chargement des données).
- `assets/custom_dash1.css` : styles (navbar, filtres, cartes, graphiques, bouton PDF, conteneurs à hauteur fixe, print).

---

## 2. Dashboard Assurance (dash2)

### Objectif

Analyse des sinistres et du profil des assurés : vue d’ensemble par type et région, profil démographique, analyse financière (primes, sinistres, ratios), profils à risque, bonus/malus.

### Données

- **MongoDB Atlas** (priorité) : base `flash_dash`, collection `assurance`. Définir `MONGO_URI` dans le fichier `.env` à la racine du projet.
- **Secours CSV** : `data/assurance_data_1000.csv` (séparateur `;`) si Atlas n’est pas disponible.
- Pour envoyer les CSV vers Atlas : à la racine, `python upload_csv_to_atlas.py`.
- Colonnes utilisées : `type_assurance`, `region`, `sexe`, `age`, `tranche_age` (dérivée), `nb_sinistres`, `montant_sinistres`, `montant_prime`, `date_derniere_sinistre`, `ratio_sinistre_prime` (dérivé), etc.

### Structure des pages

- **Vue d’ensemble** : sinistres par type d’assurance, sinistres par région, évolution dans le temps, répartition homme/femme.
- **Profil des assurés** : distribution par âge, prime moyenne par tranche d’âge, durée de contrat par type, répartition par type d’assurance.
- **Analyse financière** : montant des sinistres par type, ratio sinistres/primes par type, prime vs montant sinistres (scatter), distribution des montants.
- **Profils à risque** : âge vs montant sinistres, bonus/malus par tranche d’âge, sinistres par type et sexe, top 10 régions par sinistralité, tableau des assurés à haut risque.
- **Bonus / Malus** : distribution du coefficient B/M, B/M vs nb sinistres, B/M moyen par région et par type.

### Filtres

- Type d’assurance, Région, Sexe, Tranche d’âge (dropdowns). Tous les graphiques et KPIs réagissent à ces filtres.
- Barre de filtres : alignement homogène (labels, colonnes), min-height pour stabilité, classe `ins-filter-col` pour alignement des champs sur la même ligne de base. Répartition des colonnes sur 12 unités (1 + 2 + 2 + 2 + 5) pour utiliser toute la largeur sans espace vide à droite.

### KPIs

Assurés (effectif filtré), Sinistres (nombre), Montant total (sinistres), Moyenne par sinistre, Prime moyenne, Ratio sinistres/primes. Cartes KPI avec bordure gauche colorée et fond blanc.

### Réalisation technique

- **Bouton PDF** : placé dans la barre de header (navbar) à droite, visible sur toutes les pages ; déclenche `window.print()`. Style contrasté sur fond sombre (fond blanc, texte bleu foncé) pour rester visible.
- **Barre de filtres** : pleine largeur, pas de max-width ni centrage réduit ; colonnes réparties pour éviter une zone vide à droite.
- **Thème** : bleu profond / bordeaux / gris (INS_PRIMARY, INS_ACCENT, etc.), cartes de contenu avec style `ins-content-card`, dropdowns avec style premium (custom_dash2.css).
- **Sidebar** : navigation entre Vue d’ensemble, Profil assurés, Analyse financière, Profils à risque, Bonus/Malus.

### Fichiers principaux

- `dash2.py` : application Dash (layout, callbacks, chargement CSV, filtres).
- `assets/custom_dash2.css` : styles (navbar, filter bar, colonnes, labels, dropdowns, bouton PDF sur fond sombre, KPI cards).

---

## 3. Installation et exécution

Les deux dashboards sont montés par l’application principale (voir racine du dépôt et `app.py`). Ils ne sont pas lancés seuls en production ; le point d’entrée est `run.py` à la racine.

Pour développer ou tester :

- Dépendances : celles du projet racine (`pip install -r requirements.txt`).
- Données : soit `MONGO_URI` dans `.env` à la racine (les dashboards lisent alors depuis Atlas), soit placer les CSV dans `data/` pour le mode secours.
- Envoi initial des CSV vers Atlas : depuis la racine, `python upload_csv_to_atlas.py`.
- Accès : après `python run.py`, ouvrir http://localhost:5000/dash1 et http://localhost:5000/dash2.

Les assets (CSS) sont chargés automatiquement par Dash depuis `dashboard/assets/` pour chaque application.
