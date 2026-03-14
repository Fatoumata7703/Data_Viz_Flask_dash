"""Section Analyses Avancées"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_advanced_analytics_section():
    """Section Analyses Avancées"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📈 Analyse Corrélation Coût vs Durée", className="graph-title"),
                        dcc.Graph(id='graph-correlation', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12),
        ], className="mb-4"),
        
        # Modal pour les détails de l'analyse
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-analytics-title")),
            dbc.ModalBody(id="modal-analytics-content"),
            dbc.ModalFooter([
                dbc.Button("Fermer", id="close-modal-analytics", className="ms-auto", n_clicks=0)
            ])
        ], id="modal-analytics", is_open=False, size="lg", centered=True)
    ])
