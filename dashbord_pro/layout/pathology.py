"""Section Pathologies"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_pathology_section():
    """Section Pathologies"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🦠 Coûts par Pathologie", className="graph-title"),
                        dcc.Graph(id='graph-cout-maladie', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 Durée d'Hospitalisation par Pathologie", className="graph-title"),
                        dcc.Graph(id='graph-duree-maladie', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
        ], className="mb-4"),
        
        # Modal pour les détails de la pathologie
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-path-title")),
            dbc.ModalBody(id="modal-path-content"),
            dbc.ModalFooter([
                dbc.Button("Fermer", id="close-modal-path", className="ms-auto", n_clicks=0)
            ])
        ], id="modal-path", is_open=False, size="lg", centered=True)
    ])
