"""Navigation moderne avec menu"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_navigation():
    """Crée la barre de navigation moderne"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("🏥", style={
                            'fontSize': '2.5rem', 
                            'marginRight': '0.75rem',
                            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            '-webkit-background-clip': 'text',
                            '-webkit-text-fill-color': 'transparent',
                            'background-clip': 'text',
                            'filter': 'drop-shadow(0 0 10px rgba(102, 126, 234, 0.5))'
                        }),
                        html.Span("Dashboard Hospitalier", className="navbar-brand")
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], width="auto"),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("📊 Accueil", href="/", id="nav-home", className="nav-link-modern")),
                        dbc.NavItem(dbc.NavLink("🏥 Organisation", href="/organisation", id="nav-org", className="nav-link-modern")),
                        dbc.NavItem(dbc.NavLink("🦠 Pathologies", href="/pathologies", id="nav-path", className="nav-link-modern")),
                        dbc.NavItem(dbc.NavLink("👤 Profil Patient", href="/profil", id="nav-profil", className="nav-link-modern")),
                        dbc.NavItem(dbc.NavLink("💊 Traitements", href="/traitements", id="nav-trait", className="nav-link-modern")),
                        dbc.NavItem(dbc.NavLink("⚠️ Risques", href="/risques", id="nav-risk", className="nav-link-modern")),
                        dbc.NavItem(dbc.NavLink("📈 Analyses", href="/analyses", id="nav-analytics", className="nav-link-modern")),
                    ], navbar=True, className="ms-auto")
                ], width="auto")
            ], align="center", className="g-0")
        ], fluid=True),
        className="navbar-modern",
        dark=False,
        sticky="top"
    )
