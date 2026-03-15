"""Callbacks pour la section Patients à Risque"""
from dash import Input, Output, State, callback_context
from dash import dash_table
import dash_bootstrap_components as dbc
from dash import html
from dashbord_pro.utils import filter_data, get_risk_patients, format_number
from .constants import COLORS

def register_risk_callbacks(app, df):
    """Enregistre les callbacks pour les patients à risque"""
    
    @app.callback(
        [Output('risk-stat-total', 'children'),
         Output('risk-stat-cout-moyen', 'children'),
         Output('risk-stat-duree-moyenne', 'children'),
         Output('risk-stat-cout-total', 'children'),
         Output('risk-stat-cout-jour', 'children'),
         Output('risk-stat-percentage', 'children')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_risk_stats(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les statistiques des patients à risque"""
        from dashbord_pro.utils import filter_data, get_risk_patients, format_number
        
        # Gérer les valeurs None
        if departement is None:
            departement = []
        if maladie is None:
            maladie = []
        if traitement is None:
            traitement = []
        if sexe is None:
            sexe = []
        if age_min is None:
            age_min = df['Age'].min()
        if age_max is None:
            age_max = df['Age'].max()
        
        filtered_df = filter_data(df, departement, maladie, traitement, sexe, age_min, age_max)
        risk_patients = get_risk_patients(filtered_df, limit=100)
        
        # Calculer les statistiques
        total_risk = len(risk_patients) if len(risk_patients) > 0 else 0
        total_patients = len(filtered_df) if len(filtered_df) > 0 else 1
        
        if total_risk > 0:
            cout_moyen = risk_patients['Cout'].mean()
            duree_moyenne = risk_patients['DureeSejour'].mean()
            cout_total = risk_patients['Cout'].sum()
            cout_jour_moyen = risk_patients['CoutParJour'].mean()
            percentage = (total_risk / total_patients) * 100
        else:
            cout_moyen = 0
            duree_moyenne = 0
            cout_total = 0
            cout_jour_moyen = 0
            percentage = 0
        
        return (
            f"{total_risk:.0f}",
            format_number(cout_moyen, currency=True, decimals=1) if cout_moyen > 0 else "N/A",
            f"{duree_moyenne:.1f} j" if duree_moyenne > 0 else "N/A",
            format_number(cout_total, currency=True, decimals=1) if cout_total > 0 else "N/A",
            format_number(cout_jour_moyen, currency=True, decimals=1) if cout_jour_moyen > 0 else "N/A",
            f"{percentage:.1f}%"
        )
    
    @app.callback(
        [Output('risk-table', 'data'),
         Output('risk-table', 'columns')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_risk_table(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour le tableau des patients à risque"""
        from utils import filter_data
        import pandas as pd
        
        # Gérer les valeurs None
        if departement is None:
            departement = []
        if maladie is None:
            maladie = []
        if traitement is None:
            traitement = []
        if sexe is None:
            sexe = []
        if age_min is None:
            age_min = df['Age'].min()
        if age_max is None:
            age_max = df['Age'].max()
        
        filtered_df = filter_data(df, departement, maladie, traitement, sexe, age_min, age_max)
        risk_patients = get_risk_patients(filtered_df, limit=20)
        
        if len(risk_patients) == 0:
            empty_columns = [
                {'name': 'ID Patient', 'id': 'PatientID'},
                {'name': 'Âge', 'id': 'Age'},
                {'name': 'Sexe', 'id': 'Sexe'},
                {'name': 'Département', 'id': 'Departement'},
                {'name': 'Pathologie', 'id': 'Maladie'},
                {'name': 'Durée (j)', 'id': 'DureeSejour', 'type': 'numeric', 'format': {'specifier': ',.1f'}},
                {'name': 'Coût Total (€)', 'id': 'Cout', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                {'name': 'Coût/Jour (€)', 'id': 'CoutParJour', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                {'name': 'Traitement', 'id': 'Traitement'}
            ]
            return [], empty_columns
        
        columns = [
            {'name': 'ID Patient', 'id': 'PatientID'},
            {'name': 'Âge', 'id': 'Age'},
            {'name': 'Sexe', 'id': 'Sexe'},
            {'name': 'Département', 'id': 'Departement'},
            {'name': 'Pathologie', 'id': 'Maladie'},
            {'name': 'Durée (j)', 'id': 'DureeSejour', 'type': 'numeric', 'format': {'specifier': ',.1f'}},
            {'name': 'Coût Total (€)', 'id': 'Cout', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
            {'name': 'Coût/Jour (€)', 'id': 'CoutParJour', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
            {'name': 'Traitement', 'id': 'Traitement'}
        ]
        
        data = risk_patients.to_dict('records')
        
        return data, columns
    
    # Callback pour le modal - détecte les clics sur les lignes du tableau
    @app.callback(
        [Output('modal-risk', 'is_open'),
         Output('modal-risk-title', 'children'),
         Output('modal-risk-content', 'children')],
        [Input('risk-table', 'active_cell'),
         Input('close-modal-risk', 'n_clicks')],
        [State('modal-risk', 'is_open'),
         State('risk-table', 'data')]
    )
    def toggle_modal_risk(active_cell, n_close, is_open, table_data):
        """Gère l'ouverture/fermeture du modal avec les détails du patient à risque"""
        ctx = callback_context
        if not ctx.triggered:
            return False, "", ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si on clique sur fermer
        if trigger_id == 'close-modal-risk':
            return False, "", ""
        
        # Si une cellule est active (clic sur une ligne)
        if active_cell and table_data:
            row_idx = active_cell['row']
            if row_idx < len(table_data):
                patient_data = table_data[row_idx]
                patient_id = patient_data.get('PatientID')
                
                # Récupérer les données complètes du patient
                patient_df = df[df['PatientID'] == patient_id]
                
                if len(patient_df) == 0:
                    return is_open, "", ""
                
                patient = patient_df.iloc[0]
                
                # Créer le contenu du modal
                modal_title = f"⚠️ Détails Patient - {patient_id}"
                
                modal_content = html.Div([
                    html.Div([
                        html.Div([
                            html.Div("👤", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{patient['Age']} ans", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#fbbf24'}),
                            html.Div("Âge", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("⚥", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{patient['Sexe']}", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#fbbf24'}),
                            html.Div("Sexe", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("🏥", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{patient['Departement']}", style={'fontSize': '1rem', 'fontWeight': '700', 'color': '#fbbf24'}),
                            html.Div("Département", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("🦠", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{patient['Maladie']}", style={'fontSize': '1rem', 'fontWeight': '700', 'color': '#fbbf24'}),
                            html.Div("Pathologie", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("⏱️", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{patient['DureeSejour']:.0f} j", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#f97316'}),
                            html.Div("Durée", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("💰", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(format_number(patient['Cout'], currency=True, decimals=1), style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#10b981'}),
                            html.Div("Coût Total", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("🎯", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(format_number(patient['CoutParJour'], currency=True, decimals=1), style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#6366f1'}),
                            html.Div("Coût/Jour", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                        
                        html.Div([
                            html.Div("💊", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{patient['Traitement']}", style={'fontSize': '1rem', 'fontWeight': '700', 'color': '#fbbf24'}),
                            html.Div("Traitement", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                        ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '1rem', 'marginTop': '1rem'})
                ], style={'padding': '1rem'})
                
                return True, modal_title, modal_content
        
        return is_open, "", ""
