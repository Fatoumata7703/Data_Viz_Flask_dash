"""Callbacks pour la section Pathologies"""
from dash import Input, Output, State, callback_context
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import html
from dashbord_pro.utils import filter_data, get_pathology_stats, format_number
from .constants import COLORS

def register_pathology_callbacks(app, df):
    """Enregistre les callbacks pour les pathologies"""
    
    @app.callback(
        [Output('pathology-stat-pathologies', 'children'),
         Output('pathology-stat-cout-total', 'children'),
         Output('pathology-stat-duree-moyenne', 'children'),
         Output('pathology-stat-cout-jour', 'children')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_pathology_stats(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les statistiques des pathologies"""
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
        
        # Calculer les statistiques
        total_pathologies = len(filtered_df['Maladie'].unique()) if len(filtered_df) > 0 else 0
        cout_total = filtered_df['Cout'].sum() if len(filtered_df) > 0 else 0
        duree_moyenne = filtered_df['DureeSejour'].mean() if len(filtered_df) > 0 else 0
        cout_jour_moyen = filtered_df['CoutParJour'].mean() if len(filtered_df) > 0 else 0
        
        return (
            f"{total_pathologies:.0f}",
            format_number(cout_total, currency=True, decimals=1) if cout_total > 0 else "N/A",
            f"{duree_moyenne:.1f} j" if duree_moyenne > 0 else "N/A",
            format_number(cout_jour_moyen, currency=True, decimals=1) if cout_jour_moyen > 0 else "N/A"
        )
    
    @app.callback(
        [Output('graph-cout-maladie', 'figure'),
         Output('graph-duree-maladie', 'figure')],
        [Input('filter-departement', 'value'),
         Input('filter-maladie', 'value'),
         Input('filter-traitement', 'value'),
         Input('filter-sexe', 'value'),
         Input('filter-age-min', 'value'),
         Input('filter-age-max', 'value')]
    )
    def update_pathology_graphs(departement, maladie, traitement, sexe, age_min, age_max):
        """Met à jour les graphiques des pathologies"""
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
        
        path_stats = get_pathology_stats(filtered_df)
        
        # Vérifier si path_stats est vide
        if len(path_stats) == 0:
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
        
        # Trier par valeur décroissante pour chaque graphique
        path_stats_cout = path_stats.sort_values('CoutTotal', ascending=False)
        path_stats_duree = path_stats.sort_values('DureeMoyenne', ascending=False)
        
        # Graphique 1: Coûts par Pathologie - VERT (#10b981)
        fig_cout_maladie = go.Figure(data=[
            go.Bar(
                y=path_stats_cout['Maladie'],
                x=path_stats_cout['CoutTotal'],
                orientation='h',
                marker_color='#10b981',
                marker_line_color='#059669',
                marker_line_width=1.5,
                text=path_stats_cout['CoutTotal'].apply(lambda x: format_number(x, currency=True, decimals=1)),
                textposition='outside',
                textfont=dict(color='#10b981', size=11),
                name='Coût Total'
            )
        ])
        fig_cout_maladie.update_layout(
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
        
        # Graphique 2: Durée par Pathologie - ORANGE (#f97316)
        fig_duree_maladie = go.Figure(data=[
            go.Bar(
                x=path_stats_duree['Maladie'],
                y=path_stats_duree['DureeMoyenne'],
                marker_color='#f97316',
                marker_line_color='#ea580c',
                marker_line_width=1.5,
                text=path_stats_duree['DureeMoyenne'].apply(lambda x: f'{x:.1f} j'),
                textposition='outside',
                textfont=dict(color='#f97316', size=11),
                name='Durée Moyenne'
            )
        ])
        fig_duree_maladie.update_layout(
            title='',
            xaxis_title='Pathologie',
            yaxis_title='Durée (jours)',
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1a1f3a'),
            height=400,
            showlegend=False,
            margin=dict(l=50, r=20, t=50, b=80)
        )
        
        return fig_cout_maladie, fig_duree_maladie
    
    # Callback pour le modal - détecte les clics sur les graphiques
    @app.callback(
        [Output('modal-path', 'is_open'),
         Output('modal-path-title', 'children'),
         Output('modal-path-content', 'children')],
        [Input('graph-cout-maladie', 'clickData'),
         Input('graph-duree-maladie', 'clickData'),
         Input('close-modal-path', 'n_clicks')],
        [State('modal-path', 'is_open'),
         State('filter-departement', 'value'),
         State('filter-maladie', 'value'),
         State('filter-traitement', 'value'),
         State('filter-sexe', 'value'),
         State('filter-age-min', 'value'),
         State('filter-age-max', 'value')]
    )
    def toggle_modal_path(click_cout, click_duree, n_close, is_open, 
                         departement, maladie, traitement, sexe, age_min, age_max):
        """Gère l'ouverture/fermeture du modal avec les détails de la pathologie"""
        ctx = callback_context
        if not ctx.triggered:
            return False, "", ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si on clique sur fermer
        if trigger_id == 'close-modal-path':
            return False, "", ""
        
        # Détecter quel graphique a été cliqué
        click_data = None
        if trigger_id == 'graph-cout-maladie' and click_cout:
            click_data = click_cout
        elif trigger_id == 'graph-duree-maladie' and click_duree:
            click_data = click_duree
        
        if not click_data or 'points' not in click_data or len(click_data['points']) == 0:
            return is_open, "", ""
        
        # Récupérer la pathologie cliquée
        point = click_data['points'][0]
        path_name = None
        
        # Pour les graphiques horizontaux, le label est dans 'y'
        # Pour les graphiques verticaux, le label est dans 'x'
        if 'y' in point and isinstance(point['y'], str):
            path_name = point['y']
        elif 'x' in point and isinstance(point['x'], str):
            path_name = point['x']
        elif 'label' in point:
            path_name = point['label']
        
        if not path_name:
            return is_open, "", ""
        
        # Filtrer les données pour cette pathologie
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
        path_df = filtered_df[filtered_df['Maladie'] == path_name]
        
        if len(path_df) == 0:
            return is_open, "", ""
        
        # Calculer les statistiques de la pathologie
        total_patients = len(path_df)
        cout_total = path_df['Cout'].sum()
        cout_moyen = path_df['Cout'].mean()
        duree_moyenne = path_df['DureeSejour'].mean()
        cout_par_jour = path_df['CoutParJour'].mean()
        patients_risque = path_df['PatientRisque'].sum()
        
        # Créer le contenu du modal
        modal_title = f"🦠 Détails - {path_name}"
        
        modal_content = html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div("👥", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                        html.Div(f"{total_patients}", style={'fontSize': '2rem', 'fontWeight': '700', 'color': '#10b981'}),
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
