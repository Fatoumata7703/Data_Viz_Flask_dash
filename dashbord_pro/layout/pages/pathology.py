"""Page Pathologies"""
import dash_bootstrap_components as dbc
from dash import html
from ..filters import create_filters
from ..pathology import create_pathology_section
from ..icons import create_icon_svg

def _patho_card(icon, id_value, label, color):
    """Carte : icône + chiffre sur une ligne, libellé en dessous."""
    return html.Div([
        html.Div(icon, className="pathology-stat-icon", style={'background': color}),
        html.Div([
            html.Div(id=id_value, className="pathology-stat-value"),
            html.Div(label, className="pathology-stat-label")
        ], className="stat-card-body")
    ], className="pathology-stat-card", style={'--stat-color': color})

def create_pathology_stats_cards():
    """Crée les cartes de statistiques pour les pathologies"""
    return html.Div([
        _patho_card(create_icon_svg('virus', 28, color='white'), "pathology-stat-pathologies", "PATHOLOGIES", '#10b981'),
        _patho_card(create_icon_svg('chart', 28, color='white'), "pathology-stat-cout-total", "COÛT TOTAL", '#10b981'),
        _patho_card(create_icon_svg('clock', 28, color='white'), "pathology-stat-duree-moyenne", "DURÉE MOY.", '#8b5cf6'),
        _patho_card(create_icon_svg('chart', 28, color='white'), "pathology-stat-cout-jour", "COÛT/JOUR", '#f97316'),
    ], className="pathology-stats-grid", id="pathology-stats-grid")

def create_pathology_page(df):
    """Crée la page pathologies avec design amélioré"""
    return html.Div([
        create_pathology_stats_cards(),
        html.Div([
            create_filters(df),
            create_pathology_section(),
        ], className="page-content-wrapper")
    ], className="page-container")
