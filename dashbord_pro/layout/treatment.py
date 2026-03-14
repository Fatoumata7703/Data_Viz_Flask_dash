"""Section Traitements"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_treatment_section():
    """Section Traitements"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("💊 Coûts par Traitement", className="graph-title"),
                        dcc.Graph(id='graph-cout-traitement', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("✅ Efficacité des Traitements (Coût vs Durée)", className="graph-title"),
                        dcc.Graph(id='graph-efficacite-traitement', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
        ], className="mb-4"),
        
        # Modal pour les détails du traitement
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-treatment-title")),
            dbc.ModalBody(id="modal-treatment-content"),
            dbc.ModalFooter([
                dbc.Button("Fermer", id="close-modal-treatment", className="ms-auto", n_clicks=0)
            ])
        ], id="modal-treatment", is_open=False, size="lg", centered=True)
    ])
