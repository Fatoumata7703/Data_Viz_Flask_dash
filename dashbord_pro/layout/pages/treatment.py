"""Page Traitements"""
import dash_bootstrap_components as dbc
from dash import html
from ..filters import create_filters
from ..treatment import create_treatment_section
from ..icons import create_icon_svg

def _treatment_card(icon, id_value, label, color):
    """Carte : icône + chiffre sur une ligne, libellé en dessous."""
    return html.Div([
        html.Div(icon, className="treatment-stat-icon", style={'background': color}),
        html.Div([
            html.Div(id=id_value, className="treatment-stat-value"),
            html.Div(label, className="treatment-stat-label")
        ], className="stat-card-body")
    ], className="treatment-stat-card", style={'--stat-color': color})

def create_treatment_stats_cards():
    """Crée les cartes de statistiques pour les traitements"""
    return html.Div([
        _treatment_card(create_icon_svg('pill', 28, color='white'), "treatment-stat-total", "TRAITEMENTS", '#8b5cf6'),
        _treatment_card(create_icon_svg('chart', 28, color='white'), "treatment-stat-cout-moyen", "COÛT MOY.", '#f97316'),
        _treatment_card(create_icon_svg('clock', 28, color='white'), "treatment-stat-duree-moyenne", "DURÉE MOY.", '#10b981'),
        _treatment_card(create_icon_svg('chart', 28, color='white'), "treatment-stat-cout-total", "COÛT TOTAL", '#6366f1'),
        _treatment_card(create_icon_svg('chart', 28, color='white'), "treatment-stat-efficacite", "EFFICACITÉ", '#ec4899'),
        _treatment_card(create_icon_svg('user', 28, color='white'), "treatment-stat-patients", "PATIENTS", '#f59e0b'),
    ], className="treatment-stats-grid", id="treatment-stats-grid")

def create_treatment_page(df):
    """Crée la page traitements avec design amélioré"""
    return html.Div([
        create_treatment_stats_cards(),
        html.Div([
            create_filters(df),
            create_treatment_section(),
        ], className="page-content-wrapper")
    ], className="page-container")
