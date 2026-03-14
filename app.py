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

from flask import Flask, render_template
from dashboard.dash1 import create_dash_app as create_dash1
from dashboard.dash2 import create_dash_app as create_dash2
from projet_positionnement_bank.app_bank import create_dash_app as create_dash_bank
from dashbord_pro.app import create_dash_app as create_dash_pro

# Initialiser Flask
server = Flask(__name__)

# Configuration
server.config['SECRET_KEY'] = 'your-secret-key-here'

# Créer les instances Dash avec le serveur Flask
app_dash1 = create_dash1(server, '/dash1/')
app_dash2 = create_dash2(server, '/dash2/')
app_dash_bank = create_dash_bank(server, '/bank/')
app_dash_pro = create_dash_pro(server, '/pro/')

# Route principale
@server.route('/')
def index():
    return render_template('index.html')

# Route pour le dashboard 1
@server.route('/dash1')
def dash1():
    return render_template('dash1.html')

# Route pour le dashboard 2
@server.route('/dash2')
def dash2():
    return render_template('dash2.html')

# Route pour le dashboard bancaire
@server.route('/bank')
def bank():
    return render_template('bank.html')

# Route pour le dashboard pro (hospitalier)
@server.route('/pro')
def pro():
    return render_template('pro.html')

# À propos (visible uniquement depuis les dashboards)
@server.route('/a-propos')
def a_propos():
    return render_template('a_propos.html')

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)
