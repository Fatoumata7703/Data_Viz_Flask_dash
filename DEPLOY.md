# Déployer Flash Dash en ligne (MongoDB prod + app)

## 1. MongoDB en ligne : MongoDB Atlas (recommandé)

1. **Créer un compte** sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. **Créer un cluster** (gratuit M0, 512 Mo).
3. **Réseau** : dans "Network Access", ajouter l’IP `0.0.0.0/0` pour autoriser l’accès depuis n’importe où (ou les IP de ton hébergeur).
4. **Utilisateur** : dans "Database Access", créer un utilisateur (login + mot de passe).
5. **Récupérer l’URI** : "Connect" → "Connect your application" → copier l’URI. Elle ressemble à :
   ```text
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **Bases utilisées par Flash Dash** :
   - **Bancaire** : base `bank_prod`, collection `prod`. Sync depuis le local : `python -m projet_positionnement_bank.scripts.sync_local_to_atlas` (avec `MONGO_URI` dans `projet_positionnement_bank/.env`).
   - **Solaire, Assurance, Hospitalier** : base `flash_dash`, collections `solar`, `assurance`, `hospital`. Envoi des CSV vers Atlas (une fois) : à la racine du projet, `python upload_csv_to_atlas.py` (avec `MONGO_URI` dans le `.env` à la racine).

Tu peux aussi importer la base bancaire locale vers Atlas avec mongodump/mongorestore :
```bash
mongodump --uri="mongodb://localhost:27017" --db=bank_prod --out=./dump
mongorestore --uri="mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net" --db=bank_prod ./dump/bank_prod
```

---

## 2. Déployer l’application Flask

### Option A : AlwaysData (WSGI)

1. **Compte** sur [AlwaysData](https://www.alwaysdata.com).
2. **Créer un site** → type **Python** / **WSGI**.
3. **Répertoire de l’application** : racine du dépôt (ex. `/home/tata/www/Flash_dash`, où se trouvent `app.py`, `wsgi.py`).
4. **Fichier d’entrée WSGI** : `wsgi.py` (le module expose `application`).
5. **Environnement virtuel et dépendances** (obligatoire, sinon « No module named 'flask' ») :
   - Ouvrir un **terminal distant** (SSH ou « Exécuter une commande » dans le panneau AlwaysData).
   - Aller dans le répertoire du projet et créer un venv puis installer les paquets :
   ```bash
   cd /home/tata/www/Flash_dash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   - Dans le panneau AlwaysData : **Site** → ton site → **Paramètres** (ou **Configuration**) → champ **Environnement virtuel** (ou **Virtualenv**) : indiquer le chemin complet du venv, par ex. `/home/tata/www/Flash_dash/venv`.
   - Redémarrer l’application (bouton « Redémarrer » ou enregistrer les paramètres).
6. **Variables d’environnement** : dans le panneau AlwaysData (souvent dans **Variables d’environnement** ou **Environnement**), définir `MONGO_URI` avec l’URI Atlas (pour les 4 dashboards).

### Option B : Render (gratuit, simple)

1. **Compte** sur [Render](https://render.com).
2. **Nouveau "Web Service"** : connecte ton repo Git (GitHub/GitLab).
3. **Build** :  
   - Build command : `pip install -r requirements.txt`  
   - Start command : `gunicorn -w 2 -b 0.0.0.0:$PORT app:server`  
   (ou `run:server` si tu pointes sur `run.py` avec une petite modification.)
4. **Variables d’environnement** : dans le dashboard Render, ajoute :
   - `MONGO_URI` = ton URI Atlas (avec le mot de passe).
5. **Port** : Render fournit `PORT` ; utilise-le dans la commande de démarrage.

Si ton point d’entrée est `run.py` qui lance `app.server`, tu peux :
- soit créer un `Procfile` ou une commande : `gunicorn -w 2 -b 0.0.0.0:$PORT app:server`  
- soit adapter `run.py` pour lire `PORT` et lancer `server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))` et utiliser `python run.py` comme start command (sans gunicorn en gratuit, ou avec gunicorn en pointant sur `app:server`).

### Option C : Railway

1. [Railway](https://railway.app) → New Project → "Deploy from GitHub".
2. Variables : `MONGO_URI` = URI Atlas.
3. Start : `gunicorn -w 2 -b 0.0.0.0:$PORT app:server` (en précisant le port fourni par Railway).

### Option D : VPS (DigitalOcean, OVH, etc.)

1. Sur le serveur : installer Python, MongoDB (ou utiliser Atlas depuis le VPS).
2. Cloner le projet, `pip install -r requirements.txt`, installer gunicorn.
3. Variables d’environnement : exporter `MONGO_URI` (ou utiliser un fichier `.env` chargé par ton lanceur).
4. Lancer avec **gunicorn** derrière **nginx** (reverse proxy) :
   ```bash
   gunicorn -w 2 -b 127.0.0.1:5000 app:server
   ```
5. Nginx : proxy passer les requêtes vers `127.0.0.1:5000`.

---

## 3. Points importants

- **Ne jamais commiter** l’URI MongoDB (mot de passe) dans le repo. Toujours utiliser les variables d’environnement (`MONGO_URI`) sur la plateforme de déploiement.
- **Un seul `MONGO_URI`** alimente les 4 dashboards : bancaire (`bank_prod.prod`), solaire / assurance / hospitalier (`flash_dash.solar`, `flash_dash.assurance`, `flash_dash.hospital`).
- En prod, désactiver le mode debug : `server.run(debug=False, ...)` ou ne pas utiliser `run.py` en direct et passer par gunicorn (ou WSGI sur AlwaysData).
- Si tu utilises un fichier `.env` en local, ajoute `.env` dans `.gitignore` et crée un `.env.example` avec des placeholders (sans vrais mots de passe).

---

## 4. Dépannage : « Loading... » en ligne (AlwaysData)

Si la page d’accueil et « À propos » s’affichent mais que les dashboards (Photovoltaïque, Assurance, Bancaire, Hospitalier) restent sur « Loading... » :

1. **Définir `MONGO_URI` sur AlwaysData**  
   Le fichier `.env` n’est pas déployé (dans `.gitignore`). Il faut donc ajouter la variable dans le panneau : **Site** → **data_viz** → **Configuration** → **Variables d’environnement** → Nom : `MONGO_URI`, Valeur : ton URI Atlas (ex. `mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/?appName=Cluster0`). Puis **redémarrer** le site.

2. **MongoDB Atlas – Network Access**  
   Dans Atlas → **Network Access**, autoriser l’accès depuis n’importe où (`0.0.0.0/0`) pour que le serveur AlwaysData puisse se connecter.

3. **Premier chargement**  
   Au premier chargement, l’app peut prendre 15–30 s (connexion Atlas + chargement des 4 dashboards). Attendre un peu avant de conclure à une erreur.

---

## 4.1 Style des filtres différent en ligne (app_bank, dash1, dash2)

Si en ligne les filtres (barre blanche, dropdowns, boutons) n’ont pas le même style qu’en local (couleurs, bordures, boutons « 7j / 30j » etc.), c’est en général que **les CSS personnalisés ne se chargent pas** : les assets sont demandés sans le préfixe `/data_viz`, donc en 404.

**À faire :**

1. **Point d’entrée AlwaysData**  
   Utiliser **`wsgi:application`** (fichier `wsgi.py`, variable `application`), et **pas** `app:server`.  
   `wsgi.py` définit `APPLICATION_ROOT=/data_viz` **avant** d’importer `app`, ce qui permet à Dash de générer les bonnes URLs pour les CSS (ex. `/data_viz/bank/assets/custom.css`).

2. **Si tu n’utilises pas wsgi.py** (ex. gunicorn seul)  
   Définir la variable d’environnement **`APPLICATION_ROOT=/data_viz`** dans le panneau AlwaysData (**Site** → **Configuration** → **Variables d’environnement**), puis redémarrer. Elle doit être définie **avant** le chargement de l’app.

3. **Accéder au site avec le préfixe**  
   Ouvrir l’app via `https://ton-domaine.alwaysdata.net/data_viz` (puis Bancaire, Photovoltaïque, etc.). Ne pas utiliser une URL sans `/data_viz` pour les dashboards.

Quand c’est correct, les requêtes réseau (comme en local) chargent notamment : `style.css`, `script.js`, `bank/` (ou `dash1/`, `dash2/`), puis les assets Dash (Bootstrap, Inter, composants) sous `/data_viz/bank/...` (ou dash1/dash2), et les filtres ont le même rendu qu’en local.

---

## 5. Résumé minimal (Atlas + hébergement)

1. Créer un cluster MongoDB Atlas, récupérer l’URI. Créer / peupler les bases : `bank_prod.prod` (sync avec `sync_local_to_atlas`), `flash_dash` (solar, assurance, hospital avec `upload_csv_to_atlas.py`).
2. **AlwaysData** : site WSGI, entrée `wsgi.py`, variable `MONGO_URI`. **Render** : Web Service → Build `pip install -r requirements.txt` → Start `gunicorn -w 2 -b 0.0.0.0:$PORT app:server`, variable `MONGO_URI`.
3. Déployer ; l’app utilisera Atlas pour les 4 dashboards.

---

## 6. Rapport bancaire (génération HTML) — AlwaysData

Le rapport de positionnement bancaire (PDF/HTML) est généré à partir du notebook `projet_positionnement_bank/rapport.ipynb`. En ligne, il peut échouer avec **« No module named 'matplotlib' »** ou **« No module named 'IPython' »** si les dépendances ne sont pas installées.

### Commandes à exécuter manuellement sur AlwaysData

1. **Ouvrir un terminal distant** (SSH ou « Exécuter une commande » dans le panneau AlwaysData).

2. **Aller dans le répertoire du projet et activer l’environnement virtuel** :
   ```bash
   cd /home/VOTRE_USER/www/Flash_dash
   source venv/bin/activate
   ```

3. **Réinstaller les dépendances** (pour être sûr que `matplotlib` est présent) :
   ```bash
   pip install -r requirements.txt
   ```
   (Le fichier `requirements.txt` inclut déjà `matplotlib` ; cette commande met à jour si besoin.)

4. **Optionnel — IPython** (pour un affichage HTML plus riche dans le notebook ; le rapport peut se générer sans) :
   ```bash
   pip install ipython
   ```

5. **Redémarrer l’application** (bouton « Redémarrer » du site dans le panneau AlwaysData).

6. **Regénérer le rapport** : depuis l’interface du dashboard bancaire, choisir une banque et une année puis cliquer sur **« Rapport »** pour télécharger le HTML. Si tout est installé, les sections avec graphiques (matplotlib) et les blocs HTML (display) s’afficheront correctement.

### Comportement si matplotlib ou IPython manquent

Le notebook a été rendu **tolérant** :
- Si **matplotlib** est absent : les cellules qui dessinent des graphiques affichent « Graphique non disponible (matplotlib manquant). » au lieu de planter.
- Si **IPython** est absent : les blocs HTML sont affichés en texte brut (sans mise en forme) au lieu de planter.

Pour avoir les graphiques et la mise en forme complète, installe au minimum **matplotlib** (déjà dans `requirements.txt`).
