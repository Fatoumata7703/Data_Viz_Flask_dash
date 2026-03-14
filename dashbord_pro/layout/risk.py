"""Section Patients à Risque"""
import dash_bootstrap_components as dbc
from dash import html, dash_table

def create_risk_patients_section():
    """Section Patients à Risque"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Patients à Risque (Long Séjour + Coût Élevé)", className="graph-title"),
                        html.Div([
                            html.Div([
                                html.H6("Qu'est-ce qu'un patient à risque ?", style={
                                    'marginBottom': '0.5rem',
                                    'fontWeight': '700',
                                    'color': '#92400e'
                                }),
                                html.P([
                                    html.Strong("Définition : "),
                                    "Un patient est considéré à risque si sa durée de séjour ET son coût sont supérieurs au 75ème percentile de tous les patients."
                                ], style={'marginBottom': '0.75rem'}),
                                html.P([
                                    html.Strong("Qu'est-ce que le 75ème percentile ? "),
                                    "C'est la valeur en dessous de laquelle se trouvent 75% des patients. Par exemple, si le 75ème percentile de la durée de séjour est de 12 jours, cela signifie que 75% des patients restent moins de 12 jours à l'hôpital. Les 25% restants (les patients à risque) restent plus de 12 jours."
                                ], style={'marginBottom': '0.75rem'}),
                                html.P([
                                    html.Strong("Critères : "),
                                    "Pour être considéré à risque, un patient doit avoir :",
                                    html.Ul([
                                        html.Li("Une durée de séjour supérieure au 75ème percentile (par exemple > 12 jours)"),
                                        html.Li("ET un coût supérieur au 75ème percentile (par exemple > 5000€)")
                                    ], style={'marginTop': '0.5rem', 'marginBottom': '0.5rem', 'paddingLeft': '1.5rem'})
                                ], style={'marginBottom': '0.75rem'}),
                                html.P([
                                    "Ce tableau affiche les patients nécessitant une attention immédiate, triés par durée de séjour et coût décroissants. ",
                                    html.Strong("Cliquez sur une ligne pour voir les détails complets du patient.")
                                ], style={'marginBottom': '0'})
                            ], style={
                                'marginBottom': '1rem',
                                'padding': '1rem',
                                'backgroundColor': '#fef3c7',
                                'borderLeft': '4px solid #fbbf24',
                                'borderRadius': '4px',
                                'color': '#92400e',
                                'fontSize': '0.875rem',
                                'lineHeight': '1.6'
                            })
                        ], style={'marginBottom': '1rem'}),
                        html.Div([
                            dash_table.DataTable(
                                id='risk-table',
                                data=[],
                                columns=[],
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '10px',
                                    'fontFamily': 'Inter',
                                    'backgroundColor': 'white',
                                    'color': '#1a1f3a',
                                    'cursor': 'pointer',
                                    'fontSize': '0.875rem'
                                },
                                style_header={
                                    'backgroundColor': '#fbbf24',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    'textAlign': 'center',
                                    'padding': '10px',
                                    'fontSize': '0.875rem'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'filter_query': '{DureeSejour} > 10'},
                                        'backgroundColor': 'rgba(239, 68, 68, 0.2)'
                                    },
                                    {
                                        'if': {'filter_query': '{Cout} > 5000'},
                                        'backgroundColor': 'rgba(245, 158, 11, 0.2)'
                                    },
                                    {
                                        'if': {'state': 'active'},
                                        'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                                        'border': '1px solid #10b981'
                                    }
                                ],
                                style_table={
                                    'overflowX': 'auto'
                                },
                                page_size=10,
                                sort_action='native',
                                filter_action='native',
                                fill_width=False
                            )
                        ], className="risk-table-container")
                    ])
                ], className="graph-card")
            ], width=12),
        ], className="mb-4"),
        
        # Modal pour les détails du patient à risque
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-risk-title")),
            dbc.ModalBody(id="modal-risk-content"),
            dbc.ModalFooter([
                dbc.Button("Fermer", id="close-modal-risk", className="ms-auto", n_clicks=0)
            ])
        ], id="modal-risk", is_open=False, size="lg", centered=True)
    ])
