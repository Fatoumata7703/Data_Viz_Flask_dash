"""En-tête du dashboard"""
from dash import html

def create_header():
    """Crée l'en-tête premium du dashboard"""
    return html.Div(
        className="dashboard-header",
        children=[
            html.Div([
                html.H1("🏥 Dashboard Hospitalier", className="dashboard-title"),
                html.P("Analyse de Performance & Optimisation des Soins", className="dashboard-subtitle"),
                html.Div([
                    html.Span("Qualité", className="badge-modern", style={'margin': '0 0.5rem'}),
                    html.Span("•", style={'color': 'rgba(255,255,255,0.5)', 'margin': '0 0.5rem'}),
                    html.Span("Durée", className="badge-modern", style={'margin': '0 0.5rem'}),
                    html.Span("•", style={'color': 'rgba(255,255,255,0.5)', 'margin': '0 0.5rem'}),
                    html.Span("Coûts", className="badge-modern", style={'margin': '0 0.5rem'}),
                ], style={'marginTop': '1.5rem', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'flexWrap': 'wrap'})
            ], style={'position': 'relative', 'zIndex': 1})
        ]
    )
