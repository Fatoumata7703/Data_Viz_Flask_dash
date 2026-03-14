"""Section Organisation Hospitalière"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_organization_section():
    """Section Organisation - Départements"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🏥 Coûts par Département", className="graph-title"),
                        dcc.Graph(id='graph-cout-departement', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("⏱️ Durée de Séjour par Département", className="graph-title"),
                        dcc.Graph(id='graph-duree-departement', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🎯 Coût par Jour par Département", className="graph-title"),
                        dcc.Graph(id='graph-cout-jour-departement', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
        ], className="mb-4"),
        
        # Modal pour les détails du département
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-dept-title")),
            dbc.ModalBody(id="modal-dept-content"),
            dbc.ModalFooter([
                dbc.Button("Fermer", id="close-modal-dept", className="ms-auto", n_clicks=0)
            ])
        ], id="modal-dept", is_open=False, size="lg", centered=True)
    ])
