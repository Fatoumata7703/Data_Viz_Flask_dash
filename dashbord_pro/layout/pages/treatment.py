"""Page Traitements"""
import dash_bootstrap_components as dbc
from dash import html
from layout.filters import create_filters
from layout.treatment import create_treatment_section
from layout.icons import create_icon_svg

def create_treatment_stats_cards():
    """Crée les cartes de statistiques pour les traitements"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('pill', 28, color='white'), className="treatment-stat-icon", style={'background': '#8b5cf6'}),
            html.Div(id="treatment-stat-total", className="treatment-stat-value"),
            html.Div("TOTAL TRAITEMENTS", className="treatment-stat-label")
        ], className="treatment-stat-card", style={'--stat-color': '#8b5cf6'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="treatment-stat-icon", style={'background': '#f97316'}),
            html.Div(id="treatment-stat-cout-moyen", className="treatment-stat-value"),
            html.Div("COÛT MOYEN", className="treatment-stat-label")
        ], className="treatment-stat-card", style={'--stat-color': '#f97316'}),
        
        html.Div([
            html.Div(create_icon_svg('clock', 28, color='white'), className="treatment-stat-icon", style={'background': '#10b981'}),
            html.Div(id="treatment-stat-duree-moyenne", className="treatment-stat-value"),
            html.Div("DURÉE MOYENNE", className="treatment-stat-label")
        ], className="treatment-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="treatment-stat-icon", style={'background': '#6366f1'}),
            html.Div(id="treatment-stat-cout-total", className="treatment-stat-value"),
            html.Div("COÛT TOTAL", className="treatment-stat-label")
        ], className="treatment-stat-card", style={'--stat-color': '#6366f1'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="treatment-stat-icon", style={'background': '#ec4899'}),
            html.Div(id="treatment-stat-efficacite", className="treatment-stat-value"),
            html.Div("EFFICACITÉ MOYENNE", className="treatment-stat-label")
        ], className="treatment-stat-card", style={'--stat-color': '#ec4899'}),
        
        html.Div([
            html.Div(create_icon_svg('user', 28, color='white'), className="treatment-stat-icon", style={'background': '#f59e0b'}),
            html.Div(id="treatment-stat-patients", className="treatment-stat-value"),
            html.Div("PATIENTS TRAITÉS", className="treatment-stat-label")
        ], className="treatment-stat-card", style={'--stat-color': '#f59e0b'}),
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
