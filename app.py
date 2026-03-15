import os
import sys
import asyncio

# Éviter le warning zmq/tornado sur Windows (Proactor event loop)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Pour que dashbord_pro résolve ses imports absolus (layout, callbacks, utils)
_dashbord_pro_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashbord_pro")
if _dashbord_pro_dir not in sys.path:
    sys.path.insert(0, _dashbord_pro_dir)

from flask import Flask, render_template, redirect
from dashboard.dash1 import create_dash_app as create_dash1
from dashboard.dash2 import create_dash_app as create_dash2
from projet_positionnement_bank.app_bank import create_dash_app as create_dash_bank
from dashbord_pro.app import create_dash_app as create_dash_pro

# Initialiser Flask
server = Flask(__name__)

# Configuration
server.config['SECRET_KEY'] = 'your-secret-key-here'

# Préfixe (ex. /data_viz) : même rendu local / en ligne. wsgi.py définit APPLICATION_ROOT avant import.
# En ligne (AlwaysData) APPLICATION_ROOT doit être /data_viz pour que les liens Hospitalier (Organisation, etc.) soient /data_viz/pro/...
_application_root = (os.environ.get("APPLICATION_ROOT") or "").rstrip("/")
_requests_prefix = (_application_root + "/") if _application_root else None

def _req(path):
    """Préfixe complet pour les apps Dash (ex. /data_viz/pro/) — utilisé pour les liens et le routage."""
    return (_application_root + path) if _application_root else None


@server.before_request
def _force_script_root():
    """En ligne : forcer SCRIPT_NAME pour que iframe et assets aient le bon préfixe (même rendu qu'en local)."""
    from flask import request
    if _application_root and not (request.environ.get("SCRIPT_NAME") or "").strip():
        request.environ["SCRIPT_NAME"] = _application_root


@server.context_processor
def _inject_base_url():
    """Injecte base_slash dans tous les templates pour des liens nav corrects sur AlwaysData (évite 404)."""
    base_slash = (_application_root + "/") if _application_root else "/"
    return {"base_slash": base_slash}


# Enregistrer les routes /pro/* AVANT create_dash_pro pour qu'elles soient prioritaires sur Dash
# (sinon Dash peut matcher /pro/<path> et renvoyer 404 pour organisation, pathologies, etc.).
def _serve_pro_subpath(subpath=""):
    app = server.extensions.get("dash_pro_app")
    return app.index() if app else ("Dashboard non chargé", 503)

server.extensions["dash_pro_app"] = None
# /pro/ et /pro/<path> servent l'app Dash (pour l'iframe). /pro sans slash sert le template pro.html (barre + iframe), comme dash1, bank, etc.
server.add_url_rule("/pro/", "pro_dash_index", _serve_pro_subpath, methods=["GET"])
server.add_url_rule("/pro/<path:subpath>", "pro_dash_subpath", _serve_pro_subpath, methods=["GET"])

create_dash1(server, "/dash1/", requests_pathname_prefix=_req("/dash1/"))
create_dash2(server, "/dash2/", requests_pathname_prefix=_req("/dash2/"))
create_dash_bank(server, "/bank/", requests_pathname_prefix=_req("/bank/"))
dash_pro_app = create_dash_pro(server, "/pro/", requests_pathname_prefix=_req("/pro/"))
server.extensions["dash_pro_app"] = dash_pro_app

@server.route("/", strict_slashes=False)
def index():
    return render_template('index.html')

@server.route("/dash1")
def dash1():
    return render_template('dash1.html')

@server.route("/dash2")
def dash2():
    return render_template('dash2.html')

@server.route("/bank")
def bank():
    return render_template('bank.html')

@server.route("/pro")
def pro():
    return render_template('pro.html')

@server.route("/a-propos")
def a_propos():
    return render_template('a_propos.html')

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)
