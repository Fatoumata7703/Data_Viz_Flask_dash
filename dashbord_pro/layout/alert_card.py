"""Carte d'alerte pour les patients à risque"""
from dash import html, dcc
from .icons import create_icon_svg

def create_alert_card(count):
    """Crée la carte d'alerte"""
    if count == 0:
        return None
    
    return html.Div([
        html.Div(create_icon_svg('alert-warning', 24, color='#f97316'), className="alert-icon"),
        html.Div([
            html.Div(f"{count} patient(s) à risque en attente", className="alert-title"),
            html.Div("Des patients nécessitent une attention immédiate", className="alert-description")
        ], className="alert-content"),
        dcc.Link([
            html.Div(create_icon_svg('warning', 24, color='white'), className="alert-action-icon")
        ], href="/risques", className="alert-action")
    ], className="alert-card")
