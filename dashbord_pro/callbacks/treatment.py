"""Callbacks pour la section Traitements"""
from dash import Input, Output, State, callback_context
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import html
from utils import filter_data, get_treatment_stats, format_number
from callbacks.constants import COLORS

def register_treatment_callbacks(app, df):
    """Enregistre les callbacks pour les traitements"""
    
    @app.callback(
        [Output('treatment-stat-total', 'children'),
         Output('treatment-stat-cout-moyen', 'children'),
         Output('treatment-stat-duree-moyenne', 'children'),
         Output('treatment-stat-cout-total', 'children'),
         Output('treatment-stat-efficacite', 'children'),
         Output('treatment-stat-patients', 'children')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_treatment_stats(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les statistiques des traitements"""
        from utils import filter_data, format_number
        
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
        
        # Calculer les statistiques globales
        total_traitements = len(filtered_df['Traitement'].unique()) if len(filtered_df) > 0 else 0
        cout_moyen = filtered_df['Cout'].mean() if len(filtered_df) > 0 else 0
        duree_moyenne = filtered_df['DureeSejour'].mean() if len(filtered_df) > 0 else 0
        cout_total = filtered_df['Cout'].sum() if len(filtered_df) > 0 else 0
        total_patients = len(filtered_df) if len(filtered_df) > 0 else 0
        
        # Calculer l'efficacité moyenne (inverse du coût moyen * durée moyenne)
        efficacite = 0
        if cout_moyen > 0 and duree_moyenne > 0:
            efficacite = 1 / (cout_moyen * duree_moyenne / 1000)
        
        return (
            f"{total_traitements:.0f}",
            format_number(cout_moyen, currency=True, decimals=1) if cout_moyen > 0 else "N/A",
            f"{duree_moyenne:.1f} j" if duree_moyenne > 0 else "N/A",
            format_number(cout_total, currency=True, decimals=1) if cout_total > 0 else "N/A",
            f"{efficacite:.2f}" if efficacite > 0 else "N/A",
            f"{total_patients:.0f}"
        )
    
    @app.callback(
        [Output('graph-cout-traitement', 'figure'),
         Output('graph-efficacite-traitement', 'figure')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_treatment_graphs(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les graphiques des traitements"""
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
        
        treat_stats = get_treatment_stats(filtered_df)
        
        # Vérifier si treat_stats est vide
        if len(treat_stats) == 0:
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
        
        # Trier par valeur décroissante
        treat_stats_cout = treat_stats.sort_values('CoutTotal', ascending=False)
        
        # Graphique 1: Coûts par Traitement - ORANGE (#f97316)
        fig_cout_traitement = go.Figure(data=[
            go.Bar(
                y=treat_stats_cout['Traitement'],
                x=treat_stats_cout['CoutTotal'],
                orientation='h',
                marker_color='#f97316',
                marker_line_color='#ea580c',
                marker_line_width=1.5,
                text=treat_stats_cout['CoutTotal'].apply(lambda x: format_number(x, currency=True, decimals=1)),
                textposition='outside',
                textfont=dict(color='#f97316', size=11),
                name='Coût Total'
            )
        ])
        fig_cout_traitement.update_layout(
            title='',
            xaxis_title='Coût Total (€)',
            yaxis_title='',
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a1f3a'),
            height=400,
            showlegend=False,
            margin=dict(l=120, r=20, t=50, b=50)
        )
        
        # Graphique 2: Efficacité des Traitements (Scatter) - ROSE (#ec4899)
        fig_efficacite = go.Figure(data=[
            go.Scatter(
                x=treat_stats['DureeMoyenne'],
                y=treat_stats['CoutMoyen'],
                mode='markers+text',
                marker=dict(
                    size=treat_stats['NbPatients']*2,
                    color='#ec4899',
                    sizemode='diameter',
                    sizemin=10,
                    line=dict(color='#be185d', width=1.5)
                ),
                text=treat_stats['Traitement'],
                textposition='top center',
                textfont=dict(size=10, color='#1a1f3a'),
                name='Traitements'
            )
        ])
        fig_efficacite.update_layout(
            title='',
            xaxis_title='Durée Moyenne (jours)',
            yaxis_title='Coût Moyen (€)',
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a1f3a'),
            height=400,
            showlegend=False
        )
        
        return fig_cout_traitement, fig_efficacite
    
    # Callback pour le modal - détecte les clics sur les graphiques
    @app.callback(
        [Output('modal-treatment', 'is_open'),
         Output('modal-treatment-title', 'children'),
         Output('modal-treatment-content', 'children')],
        [Input('graph-cout-traitement', 'clickData'),
         Input('graph-efficacite-traitement', 'clickData'),
         Input('close-modal-treatment', 'n_clicks')],
        [State('modal-treatment', 'is_open'),
         State('filter-departement', 'value'),
         State('filter-maladie', 'value'),
         State('filter-traitement', 'value'),
         State('filter-sexe', 'value'),
         State('filter-age-min', 'value'),
         State('filter-age-max', 'value')]
    )
    def toggle_modal_treatment(click_cout, click_efficacite, n_close, is_open, 
                              departement, maladie, traitement, sexe, age_min, age_max):
        """Gère l'ouverture/fermeture du modal avec les détails du traitement"""
        ctx = callback_context
        if not ctx.triggered:
            return False, "", ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si on clique sur fermer
        if trigger_id == 'close-modal-treatment':
            return False, "", ""
        
        # Détecter quel graphique a été cliqué
        click_data = None
        treat_name = None
        
        if trigger_id == 'graph-cout-traitement' and click_cout:
            click_data = click_cout
            if click_data and 'points' in click_data and len(click_data['points']) > 0:
                point = click_data['points'][0]
                if 'y' in point and isinstance(point['y'], str):
                    treat_name = point['y']
        elif trigger_id == 'graph-efficacite-traitement' and click_efficacite:
            click_data = click_efficacite
            if click_data and 'points' in click_data and len(click_data['points']) > 0:
                point = click_data['points'][0]
                if 'text' in point:
                    treat_name = point['text']
        
        if not click_data or not treat_name:
            return is_open, "", ""
        
        # Filtrer les données pour ce traitement
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
        treat_df = filtered_df[filtered_df['Traitement'] == treat_name]
        
        if len(treat_df) == 0:
            return is_open, "", ""
        
        # Calculer les statistiques du traitement
        total_patients = len(treat_df)
        cout_total = treat_df['Cout'].sum()
        cout_moyen = treat_df['Cout'].mean()
        duree_moyenne = treat_df['DureeSejour'].mean()
        cout_par_jour = treat_df['CoutParJour'].mean()
        patients_risque = treat_df['PatientRisque'].sum()
        efficacite = 1 / (cout_moyen * duree_moyenne / 1000) if cout_moyen > 0 and duree_moyenne > 0 else 0
        
        # Créer le contenu du modal
        modal_title = f"💊 Détails - {treat_name}"
        
        modal_content = html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div("👥", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                        html.Div(f"{total_patients}", style={'fontSize': '2rem', 'fontWeight': '700', 'color': '#f97316'}),
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
