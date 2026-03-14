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
3. **Répertoire de l’application** : racine du dépôt (où se trouvent `app.py`, `wsgi.py`).
4. **Fichier d’entrée WSGI** : `wsgi.py` (le module expose `application`).
5. **Variables d’environnement** : dans le panneau AlwaysData, définir `MONGO_URI` avec l’URI Atlas (pour les 4 dashboards). Pour le bancaire, le projet charge aussi depuis `projet_positionnement_bank/.env` si présent ; en prod, privilégier la variable d’environnement du serveur.
6. **Dépendances** : configurer l’installation des paquets (ex. `pip install -r requirements.txt` selon la doc AlwaysData).

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

## 4. Résumé minimal (Atlas + hébergement)

1. Créer un cluster MongoDB Atlas, récupérer l’URI. Créer / peupler les bases : `bank_prod.prod` (sync avec `sync_local_to_atlas`), `flash_dash` (solar, assurance, hospital avec `upload_csv_to_atlas.py`).
2. **AlwaysData** : site WSGI, entrée `wsgi.py`, variable `MONGO_URI`. **Render** : Web Service → Build `pip install -r requirements.txt` → Start `gunicorn -w 2 -b 0.0.0.0:$PORT app:server`, variable `MONGO_URI`.
3. Déployer ; l’app utilisera Atlas pour les 4 dashboards.
