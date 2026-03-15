"""Cartes de statistiques avec icônes SVG professionnelles"""
import dash_bootstrap_components as dbc
from dash import html
from .icons import create_icon_svg

def create_stat_cards(kpis, df):
    """Crée les cartes de statistiques avec les couleurs exactes de l'image"""
    return html.Div([
        html.Div([
            # Carte Départements - Vert (#10b981) couleur hospitalière
            html.Div([
                html.Div([
                    html.Div(create_icon_svg('hospital-building', 24), className="stat-icon", style={'background': '#10b981'}),
                    html.Div([
                        html.Div(f"{len(df['Departement'].unique())}", className="stat-value"),
                        html.Div("Départements", className="stat-label"),
                        html.Div([
                            html.Span("▲"),
                            html.Span("Actifs")
                        ], className="stat-change")
                    ])
                ], className="stat-header"),
            ], className="stat-card", style={'--stat-color': '#10b981'}),
            
            # Carte Patients - Bleu (#3b82f6) pour différencier
            html.Div([
                html.Div([
                    html.Div(create_icon_svg('users-group', 24), className="stat-icon", style={'background': '#3b82f6'}),
                    html.Div([
                        html.Div(f"{kpis['total_patients']:.0f}", className="stat-value"),
                        html.Div("Total Patients", className="stat-label"),
                        html.Div([
                            html.Span("▲"),
                            html.Span("Enregistrés")
                        ], className="stat-change")
                    ])
                ], className="stat-header"),
            ], className="stat-card", style={'--stat-color': '#3b82f6'}),
            
            # Carte Traitements - Violet (#8b5cf6) exact de l'image
            html.Div([
                html.Div([
                    html.Div(create_icon_svg('pill', 24), className="stat-icon", style={'background': '#8b5cf6'}),
                    html.Div([
                        html.Div(f"{len(df['Traitement'].unique())}", className="stat-value"),
                        html.Div("Traitements", className="stat-label"),
                        html.Div([
                            html.Span("▲"),
                            html.Span("Disponibles")
                        ], className="stat-change")
                    ])
                ], className="stat-header"),
            ], className="stat-card", style={'--stat-color': '#8b5cf6'}),
            
            # Carte À Risque - Jaune (#fbbf24) exact de l'image
            html.Div([
                html.Div([
                    html.Div(create_icon_svg('alert-warning', 24), className="stat-icon", style={'background': '#fbbf24'}),
                    html.Div([
                        html.Div(f"{kpis['patients_risque']:.0f}", className="stat-value"),
                        html.Div("À Risque", className="stat-label"),
                        html.Div([
                            html.Span("Nouveau à traiter", style={'color': '#f59e0b'})
                        ], className="stat-change warning")
                    ])
                ], className="stat-header"),
            ], className="stat-card", style={'--stat-color': '#fbbf24'}),
        ], className="stats-grid")
    ])
