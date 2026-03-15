"""Statistiques pour la page Pathologies"""
from dash import html
from .icons import create_icon_svg
from dashbord_pro.utils import format_number

def create_pathology_stats_cards(stats):
    """Crée les cartes de statistiques pour les pathologies"""
    import pandas as pd
    
    # Vérifier si stats est un DataFrame valide
    if stats is None or (isinstance(stats, pd.DataFrame) and len(stats) == 0):
        return html.Div()
    
    # S'assurer que c'est un DataFrame
    if not isinstance(stats, pd.DataFrame):
        return html.Div()
    
    # Calculer les statistiques globales avec gestion d'erreur
    try:
        total_cout = float(stats['CoutTotal'].sum()) if 'CoutTotal' in stats.columns else 0.0
        duree_moyenne = float(stats['DureeMoyenne'].mean()) if 'DureeMoyenne' in stats.columns else 0.0
        cout_jour_moyen = float(stats['CoutParJour'].mean()) if 'CoutParJour' in stats.columns else 0.0
        nb_pathologies = int(len(stats)) if len(stats) > 0 else 0
    except Exception as e:
        # En cas d'erreur, retourner des valeurs par défaut
        total_cout = 0.0
        duree_moyenne = 0.0
        cout_jour_moyen = 0.0
        nb_pathologies = 0
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div(create_icon_svg('virus', 24), className="path-stat-icon", style={'background': '#10b981'}),
                html.Div([
                    html.Div(f"{nb_pathologies}", className="path-stat-value"),
                    html.Div("Pathologies", className="path-stat-label")
                ])
            ], className="path-stat-card"),
            
            html.Div([
                html.Div(create_icon_svg('chart', 24), className="path-stat-icon", style={'background': '#10b981'}),
                html.Div([
                    html.Div(format_number(total_cout, currency=True, decimals=1), className="path-stat-value"),
                    html.Div("Coût Total", className="path-stat-label")
                ])
            ], className="path-stat-card"),
            
            html.Div([
                html.Div(create_icon_svg('chart', 24), className="path-stat-icon", style={'background': '#8b5cf6'}),
                html.Div([
                    html.Div(f"{duree_moyenne:.1f} j", className="path-stat-value"),
                    html.Div("Durée Moyenne", className="path-stat-label")
                ])
            ], className="path-stat-card"),
            
            html.Div([
                html.Div(create_icon_svg('chart', 24), className="path-stat-icon", style={'background': '#f97316'}),
                html.Div([
                    html.Div(format_number(cout_jour_moyen, currency=True, decimals=1), className="path-stat-value"),
                    html.Div("Coût/Jour Moyen", className="path-stat-label")
                ])
            ], className="path-stat-card"),
        ], className="path-stats-grid")
    ])
