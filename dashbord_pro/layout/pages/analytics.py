"""Page Analyses Avancées"""
import dash_bootstrap_components as dbc
from dash import html
from layout.filters import create_filters
from layout.analytics import create_advanced_analytics_section
from layout.icons import create_icon_svg

def create_analytics_stats_cards():
    """Crée les cartes de statistiques pour les analyses avancées"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="analytics-stat-icon", style={'background': '#8b5cf6'}),
            html.Div(id="analytics-stat-correlations", className="analytics-stat-value"),
            html.Div("CORRÉLATIONS", className="analytics-stat-label")
        ], className="analytics-stat-card", style={'--stat-color': '#8b5cf6'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="analytics-stat-icon", style={'background': '#6366f1'}),
            html.Div(id="analytics-stat-tendances", className="analytics-stat-value"),
            html.Div("TENDANCES", className="analytics-stat-label")
        ], className="analytics-stat-card", style={'--stat-color': '#6366f1'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="analytics-stat-icon", style={'background': '#10b981'}),
            html.Div(id="analytics-stat-variance", className="analytics-stat-value"),
            html.Div("VARIANCE", className="analytics-stat-label")
        ], className="analytics-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="analytics-stat-icon", style={'background': '#f97316'}),
            html.Div(id="analytics-stat-mediane", className="analytics-stat-value"),
            html.Div("MÉDIANE COÛT", className="analytics-stat-label")
        ], className="analytics-stat-card", style={'--stat-color': '#f97316'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="analytics-stat-icon", style={'background': '#ec4899'}),
            html.Div(id="analytics-stat-ecart", className="analytics-stat-value"),
            html.Div("ÉCART-TYPE", className="analytics-stat-label")
        ], className="analytics-stat-card", style={'--stat-color': '#ec4899'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="analytics-stat-icon", style={'background': '#f59e0b'}),
            html.Div(id="analytics-stat-quartiles", className="analytics-stat-value"),
            html.Div("QUARTILES", className="analytics-stat-label")
        ], className="analytics-stat-card", style={'--stat-color': '#f59e0b'}),
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
