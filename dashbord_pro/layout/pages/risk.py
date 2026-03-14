"""Page Patients à Risque"""
import dash_bootstrap_components as dbc
from dash import html
from layout.filters import create_filters
from layout.risk import create_risk_patients_section
from layout.icons import create_icon_svg

def create_risk_stats_cards():
    """Crée les cartes de statistiques pour les patients à risque"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('warning', 28, color='white'), className="risk-stat-icon", style={'background': '#f97316'}),
            html.Div(id="risk-stat-total", className="risk-stat-value"),
            html.Div("PATIENTS À RISQUE", className="risk-stat-label")
        ], className="risk-stat-card", style={'--stat-color': '#f97316'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="risk-stat-icon", style={'background': '#ef4444'}),
            html.Div(id="risk-stat-cout-moyen", className="risk-stat-value"),
            html.Div("COÛT MOYEN", className="risk-stat-label")
        ], className="risk-stat-card", style={'--stat-color': '#ef4444'}),
        
        html.Div([
            html.Div(create_icon_svg('clock', 28, color='white'), className="risk-stat-icon", style={'background': '#f59e0b'}),
            html.Div(id="risk-stat-duree-moyenne", className="risk-stat-value"),
            html.Div("DURÉE MOYENNE", className="risk-stat-label")
        ], className="risk-stat-card", style={'--stat-color': '#f59e0b'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="risk-stat-icon", style={'background': '#dc2626'}),
            html.Div(id="risk-stat-cout-total", className="risk-stat-value"),
            html.Div("COÛT TOTAL", className="risk-stat-label")
        ], className="risk-stat-card", style={'--stat-color': '#dc2626'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="risk-stat-icon", style={'background': '#fbbf24'}),
            html.Div(id="risk-stat-cout-jour", className="risk-stat-value"),
            html.Div("COÛT/JOUR MOYEN", className="risk-stat-label")
        ], className="risk-stat-card", style={'--stat-color': '#fbbf24'}),
        
        html.Div([
            html.Div(create_icon_svg('user', 28, color='white'), className="risk-stat-icon", style={'background': '#ec4899'}),
            html.Div(id="risk-stat-percentage", className="risk-stat-value"),
            html.Div("% PATIENTS", className="risk-stat-label")
        ], className="risk-stat-card", style={'--stat-color': '#ec4899'}),
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
