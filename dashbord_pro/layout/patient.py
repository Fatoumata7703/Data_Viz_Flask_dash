"""Section Profil Patient"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_patient_profile_section():
    """Section Profil Patient"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("👤 Impact de l'Âge sur la Durée de Séjour", className="graph-title"),
                        dcc.Graph(id='graph-age-duree', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("⚥ Coûts selon le Sexe", className="graph-title"),
                        dcc.Graph(id='graph-sexe-cout', config={'displayModeBar': False})
                    ])
                ], className="graph-card")
            ], width=12, lg=6),
        ], className="mb-4"),
        
        # Modal pour les détails du groupe d'âge/sexe
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-patient-title")),
            dbc.ModalBody(id="modal-patient-content"),
            dbc.ModalFooter([
                dbc.Button("Fermer", id="close-modal-patient", className="ms-auto", n_clicks=0)
            ])
        ], id="modal-patient", is_open=False, size="lg", centered=True)
    ])
