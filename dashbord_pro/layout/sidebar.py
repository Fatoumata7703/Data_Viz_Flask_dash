"""Sidebar de navigation — liens avec préfixe /pro/ pour le montage Flask"""
from dash import html
from layout.icons import create_icon_svg

# Base path du dashboard (défini par create_dash_app : '' en standalone, '/pro' si monté sur Flask)
BASE = "/pro"

def create_sidebar():
    """Crée la sidebar de navigation avec icônes SVG professionnelles"""
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('logo', 50), className="sidebar-logo-icon"),
            html.Span("Dashboard Hospitalier", className="sidebar-logo-text")
        ], className="sidebar-logo"),
        
        html.Nav([
            html.A([
                html.Div(create_icon_svg('dashboard', 24), className="nav-icon"),
                html.Span("Accueil", className="nav-text")
            ], href=(f"{BASE}/" if BASE else "/"), className="nav-link active", id="nav-home"),
            
            html.A([
                html.Div(create_icon_svg('organization', 24), className="nav-icon"),
                html.Span("Organisation", className="nav-text")
            ], href=(f"{BASE}/organisation" if BASE else "/organisation"), className="nav-link", id="nav-org"),
            
            html.A([
                html.Div(create_icon_svg('virus', 24), className="nav-icon"),
                html.Span("Pathologies", className="nav-text")
            ], href=(f"{BASE}/pathologies" if BASE else "/pathologies"), className="nav-link", id="nav-path"),
            
            html.A([
                html.Div(create_icon_svg('user', 24), className="nav-icon"),
                html.Span("Profil Patient", className="nav-text")
            ], href=(f"{BASE}/profil" if BASE else "/profil"), className="nav-link", id="nav-profil"),
            
            html.A([
                html.Div(create_icon_svg('pill', 24), className="nav-icon"),
                html.Span("Traitements", className="nav-text")
            ], href=(f"{BASE}/traitements" if BASE else "/traitements"), className="nav-link", id="nav-trait"),
            
            html.A([
                html.Div(create_icon_svg('warning', 24), className="nav-icon"),
                html.Span("Risques", className="nav-text")
            ], href=(f"{BASE}/risques" if BASE else "/risques"), className="nav-link", id="nav-risk"),
            
            html.A([
                html.Div(create_icon_svg('chart', 24), className="nav-icon"),
                html.Span("Analyses", className="nav-text")
            ], href=(f"{BASE}/analyses" if BASE else "/analyses"), className="nav-link", id="nav-analytics"),
        ], className="sidebar-nav"),
        
        html.Div([
            html.P("Dashboard Hospitalier", style={'margin': 0})
        ], className="sidebar-footer")
    ], className="sidebar")
