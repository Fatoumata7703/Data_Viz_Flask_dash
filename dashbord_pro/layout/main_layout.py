"""Layout principal : sidebar + contenu. La barre horizontale (Accueil, Photovoltaïque...) est celle du template pro.html, comme pour les autres dashboards."""
from dash import html, dcc
from .sidebar import create_sidebar
from .header_main import create_main_header

def create_main_layout(df):
    """Crée le layout : sidebar + contenu (pas de top-nav ici, même barre que dash1/dash2/bank via le template)."""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div([
            create_sidebar(),
            html.Div([
                create_main_header(),
                html.Div(id='page-content', style={'background': '#f5f7fa', 'minHeight': 'calc(100vh - 80px)'})
            ], className="main-content")
        ], className="app-container")
    ])
