"""Barre de navigation vers les autres dashboards (Photovoltaïque, Bancaire, etc.) — visible quand on ouvre /pro/ directement."""
from dash import html

# Racine du site (ex. /data_viz) pour les liens ; défini par app.py
MAIN_ROOT = ""

def _href(path):
    """Lien vers une page du site principal (path sans slash initial)."""
    root = (MAIN_ROOT or "").rstrip("/")
    return f"{root}/{path}" if root else f"/{path}"

def create_top_nav():
    """Barre en haut : Accueil, Photovoltaïque, Assurance, Bancaire, Hospitalier (actif), À propos. target=_top pour sortir de l'iframe."""
    return html.Nav([
        html.A("⚡ DashFlow", href=_href(""), className="top-nav-logo", target="_top"),
        html.Div([
            html.A("Accueil", href=_href(""), className="top-nav-link", target="_top"),
            html.A("Photovoltaïque", href=_href("dash1"), className="top-nav-link", target="_top"),
            html.A("Assurance", href=_href("dash2"), className="top-nav-link", target="_top"),
            html.A("Bancaire", href=_href("bank"), className="top-nav-link", target="_top"),
            html.A("Hospitalier", href=_href("pro"), className="top-nav-link top-nav-link--active", target="_top"),
            html.A("À propos", href=_href("a-propos"), className="top-nav-link", target="_top"),
        ], className="top-nav-links")
    ], className="top-nav")
