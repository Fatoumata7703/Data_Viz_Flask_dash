"""Header principal"""
from dash import html, dcc
from datetime import datetime
from layout.icons import create_icon_svg

def create_main_header():
    """Crée le header principal avec design amélioré"""
    return html.Div([
        html.Div([
                html.Div([
                    html.Div(create_icon_svg('medical-cross', 24), className="header-icon"),
                    html.Div([
                        html.H2("Espace Hospitalier", className="header-title"),
                        html.P("Analyse et optimisation de la prise en charge des patients", className="header-subtitle")
                    ], className="header-title-container")
                ], className="header-left"),
            
            html.Div([
                dcc.Link([
                    html.Div(create_icon_svg('virus', 24, color='#10b981'), className="pathology-icon")
                ], href="/pathologies", className="pathology-link")
            ], className="header-right")
        ], className="main-header")
    ])
