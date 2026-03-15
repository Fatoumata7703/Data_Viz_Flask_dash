"""Filtres interactifs avec design amélioré"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from .icons import create_icon_svg

def create_filters(df):
    """Crée les filtres interactifs avec design moderne"""
    departements = sorted(df['Departement'].unique())
    maladies = sorted(df['Maladie'].unique())
    traitements = sorted(df['Traitement'].unique())
    sexes = sorted(df['Sexe'].unique())
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div(create_icon_svg('dashboard', 20), className="filter-header-icon"),
                html.H5("Filtres d'Analyse", className="filter-header-title")
            ], className="filter-header"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(create_icon_svg('hospital', 18), className="filter-icon"),
                        html.Label("Département", className="filter-label")
                    ], className="filter-label-wrapper"),
                    dcc.Dropdown(
                        id='filter-departement',
                        options=[{'label': d, 'value': d} for d in departements],
                        value=departements,
                        multi=True,
                        placeholder="Tous les départements",
                        className="filter-dropdown"
                    )
                ], className="filter-item"),
                
                html.Div([
                    html.Div([
                        html.Div(create_icon_svg('virus', 18), className="filter-icon"),
                        html.Label("Pathologie", className="filter-label")
                    ], className="filter-label-wrapper"),
                    dcc.Dropdown(
                        id='filter-maladie',
                        options=[{'label': m, 'value': m} for m in maladies],
                        value=maladies,
                        multi=True,
                        placeholder="Toutes les pathologies",
                        className="filter-dropdown"
                    )
                ], className="filter-item"),
                
                html.Div([
                    html.Div([
                        html.Div(create_icon_svg('pill', 18), className="filter-icon"),
                        html.Label("Traitement", className="filter-label")
                    ], className="filter-label-wrapper"),
                    dcc.Dropdown(
                        id='filter-traitement',
                        options=[{'label': t, 'value': t} for t in traitements],
                        value=traitements,
                        multi=True,
                        placeholder="Tous les traitements",
                        className="filter-dropdown"
                    )
                ], className="filter-item"),
                
                html.Div([
                    html.Div([
                        html.Div(create_icon_svg('user', 18), className="filter-icon"),
                        html.Label("Sexe", className="filter-label")
                    ], className="filter-label-wrapper"),
                    dcc.Dropdown(
                        id='filter-sexe',
                        options=[{'label': s, 'value': s} for s in sexes],
                        value=sexes,
                        multi=True,
                        placeholder="Tous",
                        className="filter-dropdown"
                    )
                ], className="filter-item"),
            ], className="filter-row"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("Âge Minimum", className="filter-label"),
                        html.Div(id='age-min-value', className="filter-value-display")
                    ], className="filter-slider-header"),
                    dcc.Slider(
                        id='filter-age-min',
                        min=int(df['Age'].min()),
                        max=int(df['Age'].max()),
                        value=int(df['Age'].min()),
                        marks={i: {'label': str(i), 'style': {'fontSize': '0.75rem'}} for i in range(int(df['Age'].min()), int(df['Age'].max())+1, 10)},
                        tooltip={"placement": "bottom", "always_visible": False},
                        className="filter-slider"
                    )
                ], className="filter-slider-item"),
                
                html.Div([
                    html.Div([
                        html.Label("Âge Maximum", className="filter-label"),
                        html.Div(id='age-max-value', className="filter-value-display")
                    ], className="filter-slider-header"),
                    dcc.Slider(
                        id='filter-age-max',
                        min=int(df['Age'].min()),
                        max=int(df['Age'].max()),
                        value=int(df['Age'].max()),
                        marks={i: {'label': str(i), 'style': {'fontSize': '0.75rem'}} for i in range(int(df['Age'].min()), int(df['Age'].max())+1, 10)},
                        tooltip={"placement": "bottom", "always_visible": False},
                        className="filter-slider"
                    )
                ], className="filter-slider-item"),
            ], className="filter-slider-row")
        ], className="filter-container")
    ])
