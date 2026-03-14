"""Page Pathologies"""
import dash_bootstrap_components as dbc
from dash import html
from layout.filters import create_filters
from layout.pathology import create_pathology_section
from layout.icons import create_icon_svg

def create_pathology_stats_cards():
    """Crée les cartes de statistiques pour les pathologies"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('virus', 28, color='white'), className="pathology-stat-icon", style={'background': '#10b981'}),
            html.Div(id="pathology-stat-pathologies", className="pathology-stat-value"),
            html.Div("PATHOLOGIES", className="pathology-stat-label")
        ], className="pathology-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="pathology-stat-icon", style={'background': '#10b981'}),
            html.Div(id="pathology-stat-cout-total", className="pathology-stat-value"),
            html.Div("COÛT TOTAL", className="pathology-stat-label")
        ], className="pathology-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('clock', 28, color='white'), className="pathology-stat-icon", style={'background': '#8b5cf6'}),
            html.Div(id="pathology-stat-duree-moyenne", className="pathology-stat-value"),
            html.Div("DURÉE MOYENNE", className="pathology-stat-label")
        ], className="pathology-stat-card", style={'--stat-color': '#8b5cf6'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="pathology-stat-icon", style={'background': '#f97316'}),
            html.Div(id="pathology-stat-cout-jour", className="pathology-stat-value"),
            html.Div("COÛT/JOUR MOYEN", className="pathology-stat-label")
        ], className="pathology-stat-card", style={'--stat-color': '#f97316'}),
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
