"""Page Analyses Avancées"""
import dash_bootstrap_components as dbc
from dash import html
from ..filters import create_filters
from ..analytics import create_advanced_analytics_section
from ..icons import create_icon_svg

def _analytics_card(icon, id_value, label, color):
    """Carte : icône + chiffre sur une ligne, libellé en dessous."""
    return html.Div([
        html.Div(icon, className="analytics-stat-icon", style={'background': color}),
        html.Div([
            html.Div(id=id_value, className="analytics-stat-value"),
            html.Div(label, className="analytics-stat-label")
        ], className="stat-card-body")
    ], className="analytics-stat-card", style={'--stat-color': color})

def create_analytics_stats_cards():
    """Crée les cartes de statistiques pour les analyses avancées"""
    return html.Div([
        _analytics_card(create_icon_svg('chart', 28, color='white'), "analytics-stat-correlations", "CORRÉLATIONS", '#8b5cf6'),
        _analytics_card(create_icon_svg('chart', 28, color='white'), "analytics-stat-tendances", "TENDANCES", '#6366f1'),
        _analytics_card(create_icon_svg('chart', 28, color='white'), "analytics-stat-variance", "VARIANCE", '#10b981'),
        _analytics_card(create_icon_svg('chart', 28, color='white'), "analytics-stat-mediane", "MÉDIANE", '#f97316'),
        _analytics_card(create_icon_svg('chart', 28, color='white'), "analytics-stat-ecart", "ÉCART-TYPE", '#ec4899'),
        _analytics_card(create_icon_svg('chart', 28, color='white'), "analytics-stat-quartiles", "QUARTILES", '#f59e0b'),
    ], className="analytics-stats-grid", id="analytics-stats-grid")

def create_analytics_page(df):
    """Crée la page analyses avancées avec design amélioré"""
    return html.Div([
        create_analytics_stats_cards(),
        html.Div([
            create_filters(df),
            create_advanced_analytics_section(),
        ], className="page-content-wrapper")
    ], className="page-container")
