"""Page Organisation Hospitalière"""
import dash_bootstrap_components as dbc
from dash import html
from layout.filters import create_filters
from layout.organization import create_organization_section
from layout.icons import create_icon_svg

def create_organization_stats_cards():
    """Crée les cartes de statistiques pour l'organisation"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('hospital-building', 28, color='white'), className="organization-stat-icon", style={'background': '#10b981'}),
            html.Div(id="organization-stat-departements", className="organization-stat-value"),
            html.Div("DÉPARTEMENTS", className="organization-stat-label")
        ], className="organization-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="organization-stat-icon", style={'background': '#10b981'}),
            html.Div(id="organization-stat-cout-total", className="organization-stat-value"),
            html.Div("COÛT TOTAL", className="organization-stat-label")
        ], className="organization-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('clock', 28, color='white'), className="organization-stat-icon", style={'background': '#8b5cf6'}),
            html.Div(id="organization-stat-duree-moyenne", className="organization-stat-value"),
            html.Div("DURÉE MOYENNE", className="organization-stat-label")
        ], className="organization-stat-card", style={'--stat-color': '#8b5cf6'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="organization-stat-icon", style={'background': '#f97316'}),
            html.Div(id="organization-stat-cout-jour", className="organization-stat-value"),
            html.Div("COÛT/JOUR MOYEN", className="organization-stat-label")
        ], className="organization-stat-card", style={'--stat-color': '#f97316'}),
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
