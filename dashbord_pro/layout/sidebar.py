"""Sidebar — liens ABSOLUS (BASE + segment) pour AlwaysData : /data_viz/pro sans slash final sinon 'profil' → /data_viz/profil."""
from dash import html
from .icons import create_icon_svg

# Écrasé par app.py avec le préfixe complet (ex. /data_viz/pro)
BASE = "/pro"

def _href(path_segment):
    """Lien toujours valide : BASE/ ou BASE/path (ex. /data_viz/pro/profil)."""
    base = (BASE or "/pro").rstrip("/")
    return f"{base}/" if not path_segment else f"{base}/{path_segment}"

def create_sidebar():
    return html.Div([
        html.Div([
            html.Div(create_icon_svg('logo', 50), className="sidebar-logo-icon"),
            html.Span("Dashboard Hospitalier", className="sidebar-logo-text")
        ], className="sidebar-logo"),
        
        html.Nav([
            html.A([
                html.Div(create_icon_svg('dashboard', 24), className="nav-icon"),
                html.Span("Accueil", className="nav-text")
            ], href=_href(""), className="nav-link active", id="nav-home"),
            
            html.A([
                html.Div(create_icon_svg('organization', 24), className="nav-icon"),
                html.Span("Organisation", className="nav-text")
            ], href=_href("organisation"), className="nav-link", id="nav-org"),
            
            html.A([
                html.Div(create_icon_svg('virus', 24), className="nav-icon"),
                html.Span("Pathologies", className="nav-text")
            ], href=_href("pathologies"), className="nav-link", id="nav-path"),
            
            html.A([
                html.Div(create_icon_svg('user', 24), className="nav-icon"),
                html.Span("Profil Patient", className="nav-text")
            ], href=_href("profil"), className="nav-link", id="nav-profil"),
            
            html.A([
                html.Div(create_icon_svg('pill', 24), className="nav-icon"),
                html.Span("Traitements", className="nav-text")
            ], href=_href("traitements"), className="nav-link", id="nav-trait"),
            
            html.A([
                html.Div(create_icon_svg('warning', 24), className="nav-icon"),
                html.Span("Risques", className="nav-text")
            ], href=_href("risques"), className="nav-link", id="nav-risk"),
            
            html.A([
                html.Div(create_icon_svg('chart', 24), className="nav-icon"),
                html.Span("Analyses", className="nav-text")
            ], href=_href("analyses"), className="nav-link", id="nav-analytics"),
        ], className="sidebar-nav"),
        
        html.Div([
            html.P("Dashboard Hospitalier", style={'margin': 0})
        ], className="sidebar-footer")
    ], className="sidebar")
