"""Page Patients à Risque"""
import dash_bootstrap_components as dbc
from dash import html
from ..filters import create_filters
from ..risk import create_risk_patients_section
from ..icons import create_icon_svg

def _risk_card(icon, id_value, label, color):
    """Carte : icône + chiffre sur une ligne, libellé en dessous."""
    return html.Div([
        html.Div(icon, className="risk-stat-icon", style={'background': color}),
        html.Div([
            html.Div(id=id_value, className="risk-stat-value"),
            html.Div(label, className="risk-stat-label")
        ], className="stat-card-body")
    ], className="risk-stat-card", style={'--stat-color': color})

def create_risk_stats_cards():
    """Crée les cartes de statistiques pour les patients à risque"""
    return html.Div([
        _risk_card(create_icon_svg('warning', 28, color='white'), "risk-stat-total", "À RISQUE", '#f97316'),
        _risk_card(create_icon_svg('chart', 28, color='white'), "risk-stat-cout-moyen", "COÛT MOY.", '#ef4444'),
        _risk_card(create_icon_svg('clock', 28, color='white'), "risk-stat-duree-moyenne", "DURÉE MOY.", '#f59e0b'),
        _risk_card(create_icon_svg('chart', 28, color='white'), "risk-stat-cout-total", "COÛT TOTAL", '#dc2626'),
        _risk_card(create_icon_svg('chart', 28, color='white'), "risk-stat-cout-jour", "COÛT/JOUR", '#fbbf24'),
        _risk_card(create_icon_svg('user', 28, color='white'), "risk-stat-percentage", "% PATIENTS", '#ec4899'),
    ], className="risk-stats-grid", id="risk-stats-grid")

def create_risk_page(df):
    """Crée la page patients à risque avec design amélioré"""
    return html.Div([
        create_risk_stats_cards(),
        html.Div([
            create_filters(df),
            create_risk_patients_section(),
        ], className="page-content-wrapper")
    ], className="page-container")
