"""Page Organisation Hospitalière"""
import dash_bootstrap_components as dbc
from dash import html
from ..filters import create_filters
from ..organization import create_organization_section
from ..icons import create_icon_svg

def _org_card(icon, id_value, label, color):
    """Carte : icône + chiffre sur une ligne, libellé en dessous."""
    return html.Div([
        html.Div(icon, className="organization-stat-icon", style={'background': color}),
        html.Div([
            html.Div(id=id_value, className="organization-stat-value"),
            html.Div(label, className="organization-stat-label")
        ], className="stat-card-body")
    ], className="organization-stat-card", style={'--stat-color': color})

def create_organization_stats_cards():
    """Crée les cartes de statistiques pour l'organisation"""
    return html.Div([
        _org_card(create_icon_svg('hospital-building', 28, color='white'), "organization-stat-departements", "DÉPARTEMENTS", '#10b981'),
        _org_card(create_icon_svg('chart', 28, color='white'), "organization-stat-cout-total", "COÛT TOTAL", '#10b981'),
        _org_card(create_icon_svg('clock', 28, color='white'), "organization-stat-duree-moyenne", "DURÉE MOY.", '#8b5cf6'),
        _org_card(create_icon_svg('chart', 28, color='white'), "organization-stat-cout-jour", "COÛT/JOUR", '#f97316'),
    ], className="organization-stats-grid", id="organization-stats-grid")

def create_organization_page(df):
    """Crée la page organisation avec design amélioré"""
    return html.Div([
        create_organization_stats_cards(),
        html.Div([
            create_filters(df),
            create_organization_section(),
        ], className="page-content-wrapper")
    ], className="page-container")
