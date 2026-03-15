# -*- coding: utf-8 -*-
"""
Point d'entrée WSGI pour le déploiement (AlwaysData, etc.).
Expose l'application Flask sous le nom `application`.
"""
import os
import sys

_racine = os.path.dirname(os.path.abspath(__file__))

# Toujours mettre la racine du projet en premier
if _racine not in sys.path:
    sys.path.insert(0, _racine)

# Si un venv existe à côté du projet, l'utiliser (AlwaysData : venv ou .venv)
for _venv_name in ("venv", ".venv"):
    _venv_base = os.path.join(_racine, _venv_name)
    if os.path.isdir(_venv_base):
        _lib = os.path.join(_venv_base, "lib")
        if os.path.isdir(_lib):
            for _name in os.listdir(_lib):
                if _name.startswith("python"):
                    _site = os.path.join(_lib, _name, "site-packages")
                    if os.path.isdir(_site) and _site not in sys.path:
                        sys.path.insert(0, _site)
                    break
        break

# Charger .env à la racine si présent (AlwaysData : préférer les variables d'environnement du panel)
_env_path = os.path.join(_racine, ".env")
if os.path.isfile(_env_path):
    with open(_env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value

# Préfixe d'URL (ex. /data_viz) : OBLIGATOIRE avant l'import de app pour que le style des filtres
# (app_bank, dash1, dash2) soit identique en ligne et en local. Sans ce préfixe, les CSS
# (custom.css, custom_dash1.css, custom_dash2.css) ne se chargent pas et les filtres s'affichent en style par défaut.
_application_root = (os.environ.get("APPLICATION_ROOT") or "/data_viz").rstrip("/")
if _application_root and "APPLICATION_ROOT" not in os.environ:
    os.environ["APPLICATION_ROOT"] = _application_root

from app import server


def _application(environ, start_response):
    # En production, le proxy peut envoyer PATH_INFO avec ou sans préfixe.
    # Avec préfixe (/data_viz/pro/organisation) : on l'enlève pour que Flask reçoive /pro/organisation.
    # Sans préfixe (/pro/organisation) : on laisse tel quel pour que la règle /pro/<path:subpath> matche.
    path = (environ.get("PATH_INFO") or "")
    if _application_root and (path == _application_root or path.startswith(_application_root + "/")):
        environ["PATH_INFO"] = path[len(_application_root):] or "/"
        environ["SCRIPT_NAME"] = (environ.get("SCRIPT_NAME") or "") + _application_root
    try:
        return server(environ, start_response)
    except Exception:
        # Éviter que le worker crash (502) : renvoyer 500 avec un corps pour debug
        start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"500 Internal Server Error (see server logs)\n"]


application = _application
