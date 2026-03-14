"""Page Profil Patient"""
import dash_bootstrap_components as dbc
from dash import html
from layout.filters import create_filters
from layout.patient import create_patient_profile_section
from layout.icons import create_icon_svg
from utils import get_age_sex_stats, format_number

def create_patient_stats_cards():
    """Crée les cartes de statistiques pour le profil patient (sera mis à jour par callback)"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('users-group', 28, color='white'), className="patient-stat-icon", style={'background': '#8b5cf6'}),
            html.Div(id="patient-stat-total", className="patient-stat-value"),
            html.Div("TOTAL PATIENTS", className="patient-stat-label")
        ], className="patient-stat-card", style={'--stat-color': '#8b5cf6'}),
        
        html.Div([
            html.Div(create_icon_svg('user', 28, color='white'), className="patient-stat-icon", style={'background': '#6366f1'}),
            html.Div(id="patient-stat-age", className="patient-stat-value"),
            html.Div("ÂGE MOYEN", className="patient-stat-label")
        ], className="patient-stat-card", style={'--stat-color': '#6366f1'}),
        
        html.Div([
            html.Div(create_icon_svg('user', 28, color='white'), className="patient-stat-icon", style={'background': '#10b981'}),
            html.Div(id="patient-stat-hommes", className="patient-stat-value"),
            html.Div("HOMMES", className="patient-stat-label")
        ], className="patient-stat-card", style={'--stat-color': '#10b981'}),
        
        html.Div([
            html.Div(create_icon_svg('user', 28, color='white'), className="patient-stat-icon", style={'background': '#ec4899'}),
            html.Div(id="patient-stat-femmes", className="patient-stat-value"),
            html.Div("FEMMES", className="patient-stat-label")
        ], className="patient-stat-card", style={'--stat-color': '#ec4899'}),
        
        html.Div([
            html.Div(create_icon_svg('chart', 28, color='white'), className="patient-stat-icon", style={'background': '#f97316'}),
            html.Div(id="patient-stat-cout", className="patient-stat-value"),
            html.Div("COÛT MOYEN", className="patient-stat-label")
        ], className="patient-stat-card", style={'--stat-color': '#f97316'}),
        
        html.Div([
            html.Div(create_icon_svg('clock', 28, color='white'), className="patient-stat-icon", style={'background': '#f59e0b'}),
            html.Div(id="patient-stat-duree", className="patient-stat-value"),
            html.Div("DURÉE MOYENNE", className="patient-stat-label")
        ], className="patient-stat-card", style={'--stat-color': '#f59e0b'}),
    ], className="patient-stats-grid", id="patient-stats-grid")

def create_patient_page(df):
    """Crée la page profil patient avec design amélioré"""
    return html.Div([
        create_patient_stats_cards(),
        html.Div([
            create_filters(df),
            create_patient_profile_section(),
        ], className="page-content-wrapper")
    ], className="page-container")
