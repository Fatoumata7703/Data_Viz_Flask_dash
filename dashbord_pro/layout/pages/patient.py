"""Page Profil Patient"""
import dash_bootstrap_components as dbc
from dash import html
from ..filters import create_filters
from ..patient import create_patient_profile_section
from ..icons import create_icon_svg
from dashbord_pro.utils import get_age_sex_stats, format_number

def _patient_card(icon, id_value, label, color):
    """Carte : icône + chiffre sur une ligne, libellé en dessous."""
    return html.Div([
        html.Div(icon, className="patient-stat-icon", style={'background': color}),
        html.Div([
            html.Div(id=id_value, className="patient-stat-value"),
            html.Div(label, className="patient-stat-label")
        ], className="stat-card-body")
    ], className="patient-stat-card", style={'--stat-color': color})

def create_patient_stats_cards():
    """Crée les cartes de statistiques pour le profil patient (sera mis à jour par callback)"""
    return html.Div([
        _patient_card(create_icon_svg('users-group', 28, color='white'), "patient-stat-total", "PATIENTS", '#8b5cf6'),
        _patient_card(create_icon_svg('user', 28, color='white'), "patient-stat-age", "ÂGE MOY.", '#6366f1'),
        _patient_card(create_icon_svg('user', 28, color='white'), "patient-stat-hommes", "HOMMES", '#10b981'),
        _patient_card(create_icon_svg('user', 28, color='white'), "patient-stat-femmes", "FEMMES", '#ec4899'),
        _patient_card(create_icon_svg('chart', 28, color='white'), "patient-stat-cout", "COÛT MOY.", '#f97316'),
        _patient_card(create_icon_svg('clock', 28, color='white'), "patient-stat-duree", "DURÉE MOY.", '#f59e0b'),
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
