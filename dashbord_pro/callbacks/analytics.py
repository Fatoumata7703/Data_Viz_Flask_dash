"""Callbacks pour les analyses avancées"""
from dash import Input, Output, State, callback_context
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import html
from utils import filter_data, format_number
from callbacks.constants import COLORS
import pandas as pd

def register_analytics_callbacks(app, df):
    """Enregistre les callbacks pour les analyses avancées"""
    
    @app.callback(
        [Output('analytics-stat-correlations', 'children'),
         Output('analytics-stat-tendances', 'children'),
         Output('analytics-stat-variance', 'children'),
         Output('analytics-stat-mediane', 'children'),
         Output('analytics-stat-ecart', 'children'),
         Output('analytics-stat-quartiles', 'children')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_analytics_stats(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les statistiques des analyses avancées"""
        from utils import filter_data, format_number
        import numpy as np
        
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
        
        if len(filtered_df) == 0:
            return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        # Calculer les corrélations
        correlation = filtered_df['Cout'].corr(filtered_df['DureeSejour'])
        
        # Calculer les tendances (coefficient de variation)
        cv_cout = (filtered_df['Cout'].std() / filtered_df['Cout'].mean()) * 100 if filtered_df['Cout'].mean() > 0 else 0
        
        # Variance
        variance = filtered_df['Cout'].var()
        
        # Médiane
        mediane = filtered_df['Cout'].median()
        
        # Écart-type
        ecart_type = filtered_df['Cout'].std()
        
        # Quartiles (Q3 - Q1)
        q1 = filtered_df['Cout'].quantile(0.25)
        q3 = filtered_df['Cout'].quantile(0.75)
        iqr = q3 - q1
        
        return (
            f"{correlation:.2f}" if not np.isnan(correlation) else "N/A",
            f"{cv_cout:.1f}%" if cv_cout > 0 else "N/A",
            format_number(variance, currency=False, decimals=1) if not np.isnan(variance) else "N/A",
            format_number(mediane, currency=True, decimals=1) if not np.isnan(mediane) else "N/A",
            format_number(ecart_type, currency=True, decimals=1) if not np.isnan(ecart_type) else "N/A",
            format_number(iqr, currency=True, decimals=1) if not np.isnan(iqr) else "N/A"
        )
    
    @app.callback(
        Output('graph-correlation', 'figure'),
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_correlation_graph(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour le graphique de corrélation"""
        from utils import filter_data
        
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
            return empty_fig
        
        # Graphique Corrélation Coût vs Durée - INDIGO (#6366f1)
        fig_correlation = go.Figure(data=[
            go.Scatter(
                x=filtered_df['DureeSejour'],
                y=filtered_df['Cout'],
                mode='markers',
                marker=dict(
                    color=filtered_df['CoutParJour'],
                    size=8,
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title="Coût/Jour"),
                    line=dict(color='#6366f1', width=1)
                ),
                text=filtered_df['Maladie'],
                hovertemplate='<b>%{text}</b><br>Durée: %{x} jours<br>Coût: %{y} €<extra></extra>',
                name='Patients'
            )
        ])
        fig_correlation.update_layout(
            title='',
            xaxis_title='Durée de Séjour (jours)',
            yaxis_title='Coût (€)',
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a1f3a'),
            height=400,
            showlegend=False
        )
        
        return fig_correlation
    
    # Callback pour le modal - détecte les clics sur les points du graphique
    @app.callback(
        [Output('modal-analytics', 'is_open'),
         Output('modal-analytics-title', 'children'),
         Output('modal-analytics-content', 'children')],
        [Input('graph-correlation', 'clickData'),
         Input('close-modal-analytics', 'n_clicks')],
        [State('modal-analytics', 'is_open'),
         State('filter-departement', 'value'),
         State('filter-maladie', 'value'),
         State('filter-traitement', 'value'),
         State('filter-sexe', 'value'),
         State('filter-age-min', 'value'),
         State('filter-age-max', 'value')]
    )
    def toggle_modal_analytics(click_data, n_close, is_open, 
                               departement, maladie, traitement, sexe, age_min, age_max):
        """Gère l'ouverture/fermeture du modal avec les détails de l'analyse"""
        ctx = callback_context
        if not ctx.triggered:
            return False, "", ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si on clique sur fermer
        if trigger_id == 'close-modal-analytics':
            return False, "", ""
        
        # Si un point est cliqué
        if click_data and 'points' in click_data and len(click_data['points']) > 0:
            point = click_data['points'][0]
            duree = point.get('x')
            cout = point.get('y')
            maladie_name = point.get('text', '')
            
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
            
            # Trouver les patients correspondants (approximation)
            similar_patients = filtered_df[
                (filtered_df['DureeSejour'].round(0) == round(duree, 0)) & 
                (filtered_df['Cout'].round(-2) == round(cout, -2))
            ]
            
            if len(similar_patients) == 0:
                # Si aucun patient exact, prendre les plus proches
                similar_patients = filtered_df.nsmallest(5, 
                    lambda x: abs(x['DureeSejour'] - duree) + abs(x['Cout'] - cout) / 1000
                )
            
            if len(similar_patients) == 0:
                return is_open, "", ""
            
            # Calculer les statistiques
            total_patients = len(similar_patients)
            cout_total = similar_patients['Cout'].sum()
            cout_moyen = similar_patients['Cout'].mean()
            duree_moyenne = similar_patients['DureeSejour'].mean()
            cout_par_jour = similar_patients['CoutParJour'].mean()
            patients_risque = similar_patients['PatientRisque'].sum()
            
            # Calculer la corrélation
            correlation = similar_patients['DureeSejour'].corr(similar_patients['Cout'])
            
            # Créer le contenu du modal
            modal_title = f"📈 Analyse - Durée: {duree:.0f}j, Coût: {format_number(cout, currency=True, decimals=0)}"
            
            modal_content = html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("👥", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                            html.Div(f"{total_patients}", style={'fontSize': '2rem', 'fontWeight': '700', 'color': '#6366f1'}),
                            html.Div("Patients similaires", style={'fontSize': '0.875rem', 'color': '#6b7280'})
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
                    
                    html.Div([
                        html.Div("📈", style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                        html.Div(f"{correlation:.2f}", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#6366f1'}),
                        html.Div("Corrélation", style={'fontSize': '0.875rem', 'color': '#6b7280'})
                    ], style={'textAlign': 'center', 'padding': '1rem', 'background': '#f5f7fa', 'borderRadius': '12px'}),
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '1rem', 'marginTop': '1rem'})
            ], style={'padding': '1rem'})
            
            return True, modal_title, modal_content
        
        return is_open, "", ""
