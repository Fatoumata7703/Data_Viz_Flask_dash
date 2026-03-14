"""
Dashboard Hospitalier - Application Dash principale
Analyse de la prise en charge des patients : Qualité, Durée, Coûts
Intégrable au Flask principal via create_dash_app(server, url_base_pathname).
"""
import os
import sys
import dash
from dash import html
import dash_bootstrap_components as dbc

# Imports selon le contexte (depuis la racine run.py ou en standalone depuis dashbord_pro)
try:
    from .utils import load_data
    from .layout.main_layout import create_main_layout
    from .callbacks import register_all_callbacks
except ImportError:
    _parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    from dashbord_pro.utils import load_data
    from dashbord_pro.layout.main_layout import create_main_layout
    from dashbord_pro.callbacks import register_all_callbacks

# Chemins relatifs au dossier dashbord_pro (pour assets et données)
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_APP_DIR, 'assets')


def create_dash_app(server=None, url_base_pathname='/pro/'):
    """
    Crée et retourne l'app Dash hospitalier.
    Si server est fourni (Flask), l'app est montée dessus à url_base_pathname.
    Si server est None (standalone), Dash crée son propre serveur Flask.
    """
    external = [
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
    ]
    kwargs = dict(
        external_stylesheets=external,
        suppress_callback_exceptions=True,
        assets_folder=_ASSETS,
        url_base_pathname=url_base_pathname,
    )
    if server is not None:
        kwargs["server"] = server
    app = dash.Dash(__name__, **kwargs)
    base_path = (url_base_pathname or "/").rstrip("/")  # '/pro/' -> '/pro', '/' -> ''
    try:
        from .layout import sidebar
        from .callbacks import navigation
    except ImportError:
        from layout import sidebar
        from callbacks import navigation
    sidebar.BASE = base_path
    navigation.BASE = base_path
    print("Chargement des données (dashboard pro)...")
    df = load_data()
    print(f"✓ {len(df)} patients chargés")
    app.layout = html.Div([create_main_layout(df)])
    print("Enregistrement des callbacks (pro)...")
    register_all_callbacks(app, df)
    print("✓ Callbacks enregistrés (pro)")
    return app


if __name__ == '__main__':
    app = create_dash_app(None, '/')
    server = app.server
    print("\n" + "="*60)
    print("🏥 DASHBOARD HOSPITALIER - DÉMARRAGE")
    print("="*60)
    print("\n📊 Indicateurs disponibles:")
    print("   • Durée moyenne de séjour")
    print("   • Coût moyen par patient")
    print("   • Coût par jour")
    print("   • Patients à risque")
    print("\n🔍 Analyses disponibles:")
    print("   • Organisation (départements)")
    print("   • Pathologies")
    print("   • Profil patient (âge, sexe)")
    print("   • Traitements")
    print("   • Gestion des risques")
    print("\n" + "="*60)
    print("🌐 Accédez au dashboard sur: http://127.0.0.1:8050")
    print("="*60 + "\n")
    app.run_server(debug=True, host='127.0.0.1', port=8050)
