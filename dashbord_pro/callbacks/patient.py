"""Callbacks pour la section Profil Patient"""
from dash import Input, Output, State, callback_context
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import html
from dashbord_pro.utils import filter_data, format_number
from .constants import COLORS

def register_patient_callbacks(app, df):
    """Enregistre les callbacks pour le profil patient"""
    
    @app.callback(
        [Output('patient-stat-total', 'children'),
         Output('patient-stat-age', 'children'),
         Output('patient-stat-hommes', 'children'),
         Output('patient-stat-femmes', 'children'),
         Output('patient-stat-cout', 'children'),
         Output('patient-stat-duree', 'children')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_patient_stats(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les statistiques du profil patient"""
        from dashbord_pro.utils import filter_data, format_number
        
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
        
        # Calculer les statistiques
        total_patients = len(filtered_df)
        age_moyen = filtered_df['Age'].mean() if len(filtered_df) > 0 else 0
        hommes = len(filtered_df[filtered_df['Sexe'] == 'M'])
        femmes = len(filtered_df[filtered_df['Sexe'] == 'F'])
        cout_moyen = filtered_df['Cout'].mean() if len(filtered_df) > 0 else 0
        duree_moyenne = filtered_df['DureeSejour'].mean() if len(filtered_df) > 0 else 0
        
        return (
            f"{total_patients:.0f}",
            f"{age_moyen:.1f} ans" if age_moyen > 0 else "N/A",
            f"{hommes:.0f}",
            f"{femmes:.0f}",
            format_number(cout_moyen, currency=True, decimals=1) if cout_moyen > 0 else "N/A",
            f"{duree_moyenne:.1f} j" if duree_moyenne > 0 else "N/A"
        )
    
    @app.callback(
        [Output('graph-age-duree', 'figure'),
         Output('graph-sexe-cout', 'figure')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_patient_graphs(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les graphiques du profil patient"""
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
        
        # Vérifier si le DataFrame filtré est vide
        if len(filtered_df) == 0:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title='Aucune donnée disponible',
                template='plotly_white',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#1a1f3a'),
                height=400
            )
            return empty_fig, empty_fig
        
        # Graphique Âge vs Durée - ORANGE (#f97316)
        age_duree = filtered_df.groupby('Age')['DureeSejour'].mean().reset_index()
        fig_age_duree = go.Figure(data=[
            go.Scatter(
                x=age_duree['Age'],
                y=age_duree['DureeSejour'],
                mode='lines+markers',
                marker=dict(color='#f97316', size=8),
                line=dict(color='#f97316', width=2),
                name='Durée Moyenne'
            )
        ])
        fig_age_duree.update_layout(
            title='',
            xaxis_title='Âge',
            yaxis_title='Durée Moyenne de Séjour (jours)',
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a1f3a'),
            height=400,
            showlegend=False
        )
        
        # Graphique Coûts par Sexe - F en ROSE, M en BLEU
        sexe_cout = filtered_df.groupby('Sexe')['Cout'].mean().reset_index()
        
        # Créer des couleurs différentes pour chaque sexe
        colors = []
        for sexe in sexe_cout['Sexe']:
            if sexe == 'F':
                colors.append('#ec4899')  # Rose pour Femme
            else:
                colors.append('#3b82f6')  # Bleu pour Homme
        
        fig_sexe_cout = go.Figure(data=[
            go.Bar(
                x=sexe_cout['Sexe'],
                y=sexe_cout['Cout'],
                marker_color=colors,
                marker_line_color=['#db2777', '#2563eb'],  # Rose foncé et bleu foncé pour les bordures
                marker_line_width=1.5,
                text=sexe_cout['Cout'].apply(lambda x: format_number(x, currency=True, decimals=1)),
                textposition='outside',
                textfont=dict(color='#1a1f3a', size=11),
                name='Coût Moyen'
            )
        ])
        fig_sexe_cout.update_layout(
            title='',
            xaxis_title='Sexe',
            yaxis_title='Coût Moyen (€)',
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a1f3a'),
            height=400,
            showlegend=False
        )
        
        return fig_age_duree, fig_sexe_cout
    
    # Callback pour le modal - détecte les clics sur les graphiques
    @app.callback(
        [Output('modal-patient', 'is_open'),
         Output('modal-patient-title', 'children'),
         Output('modal-patient-content', 'children')],
        [Input('graph-age-duree', 'clickData'),
         Input('graph-sexe-cout', 'clickData'),
         Input('close-modal-patient', 'n_clicks')],
        [State('modal-patient', 'is_open'),
         State('filter-departement', 'value'),
         State('filter-maladie', 'value'),
         State('filter-traitement', 'value'),
         State('filter-sexe', 'value'),
         State('filter-age-min', 'value'),
         State('filter-age-max', 'value')]
    )
    def toggle_modal_patient(click_age, click_sexe, n_close, is_open, 
                            departement, maladie, traitement, sexe, age_min, age_max):
        """Gère l'ouverture/fermeture du modal avec les détails du profil patient"""
        ctx = callback_context
        if not ctx.triggered:
            return False, "", ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si on clique sur fermer
        if trigger_id == 'close-modal-patient':
            return False, "", ""
        
        # Détecter quel graphique a été cliqué
        click_data = None
        selected_value = None
        
        if trigger_id == 'graph-age-duree' and click_age:
            click_data = click_age
            if click_data and 'points' in click_data and len(click_data['points']) > 0:
                point = click_data['points'][0]
                if 'x' in point:
                    selected_value = int(point['x'])  # Âge
        elif trigger_id == 'graph-sexe-cout' and click_sexe:
            click_data = click_sexe
            if click_data and 'points' in click_data and len(click_data['points']) > 0:
                point = click_data['points'][0]
                if 'x' in point:
                    selected_value = point['x']  # Sexe
        
        if not click_data or not selected_value:
            return is_open, "", ""
        
        # Filtrer les données
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
        
        # Filtrer selon le type de sélection
        if isinstance(selected_value, int):  # C'est un âge
            patient_df = filtered_df[filtered_df['Age'] == selected_value]
            modal_title = f"👤 Détails - Patients de {selected_value} ans"
        else:  # C'est un sexe
            patient_df = filtered_df[filtered_df['Sexe'] == selected_value]
            modal_title = f"⚥ Détails - Patients {selected_value}"
        
        if len(patient_df) == 0:
            return is_open, "", ""
        
        # Calculer les statistiques
        total_patients = len(patient_df)
        cout_total = patient_df['Cout'].sum()
        cout_moyen = patient_df['Cout'].mean()
        duree_moyenne = patient_df['DureeSejour'].mean()
        cout_par_jour = patient_df['CoutParJour'].mean()
        patients_risque = patient_df['PatientRisque'].sum()
        
        # Créer le contenu du modal
        modal_content = html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div("👥", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                        html.Div(f"{total_patients}", style={'fontSize': '2rem', 'fontWeight': '700', 'color': '#8b5cf6'}),
                        html.Div("Patients", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                    ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'})
                ], style={'gridColumn': 'span 2'}),
                
                html.Div([
                    html.Div("💰", style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                    html.Div(format_number(cout_total, currency=True, decimals=1), style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#10b981'}),
                    html.Div("Coût Total", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                
                html.Div([
                    html.Div("📊", style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                    html.Div(format_number(cout_moyen, currency=True, decimals=1), style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#8b5cf6'}),
                    html.Div("Coût Moyen", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                
                html.Div([
                    html.Div("⏱️", style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                    html.Div(f"{duree_moyenne:.1f} j", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#f97316'}),
                    html.Div("Durée Moyenne", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                
                html.Div([
                    html.Div("🎯", style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                    html.Div(format_number(cout_par_jour, currency=True, decimals=1), style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#6366f1'}),
                    html.Div("Coût/Jour", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                
                html.Div([
                    html.Div("⚠️", style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                    html.Div(f"{patients_risque}", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#f59e0b'}),
                    html.Div("À Risque", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '1rem', 'marginTop': '1rem'})
        ], style={'padding': '1rem'})
        
        return True, modal_title, modal_content
