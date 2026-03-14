"""Callbacks pour la navigation entre les pages — préfixe /pro pour montage Flask"""
from dash import Input, Output
from layout.pages.home import create_home_page
from layout.pages.organization import create_organization_page
from layout.pages.pathology import create_pathology_page
from layout.pages.patient import create_patient_page
from layout.pages.treatment import create_treatment_page
from layout.pages.risk import create_risk_page
from layout.pages.analytics import create_analytics_page

BASE = "/pro"

def _is(pathname, *paths):
    if pathname is None:
        return False
    pathname = pathname.rstrip("/") or "/"
    return pathname in (p.rstrip("/") or "/" for p in paths)

def register_navigation_callbacks(app, df):
    """Enregistre les callbacks de navigation"""
    
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        """Affiche la page correspondante selon l'URL"""
        if _is(pathname, f"{BASE}/organisation", f"{BASE}/organisation/"):
            return create_organization_page(df)
        elif _is(pathname, f"{BASE}/pathologies", f"{BASE}/pathologies/"):
            return create_pathology_page(df)
        elif _is(pathname, f"{BASE}/profil", f"{BASE}/profil/"):
            return create_patient_page(df)
        elif _is(pathname, f"{BASE}/traitements", f"{BASE}/traitements/"):
            return create_treatment_page(df)
        elif _is(pathname, f"{BASE}/risques", f"{BASE}/risques/"):
            return create_risk_page(df)
        elif _is(pathname, f"{BASE}/analyses", f"{BASE}/analyses/"):
            return create_analytics_page(df)
        else:
            return create_home_page(df)
    
    @app.callback(
        [Output('nav-home', 'className'),
         Output('nav-org', 'className'),
         Output('nav-path', 'className'),
         Output('nav-profil', 'className'),
         Output('nav-trait', 'className'),
         Output('nav-risk', 'className'),
         Output('nav-analytics', 'className')],
        [Input('url', 'pathname')]
    )
    def update_active_nav(pathname):
        """Met à jour le style du lien actif dans la navigation"""
        base_class = "nav-link"
        active_class = "nav-link active"
        classes = {k: base_class for k in ['nav-home', 'nav-org', 'nav-path', 'nav-profil', 'nav-trait', 'nav-risk', 'nav-analytics']}
        
        if _is(pathname, f"{BASE}/", f"{BASE}", "/", ""):
            classes['nav-home'] = active_class
        elif _is(pathname, f"{BASE}/organisation"):
            classes['nav-org'] = active_class
        elif _is(pathname, f"{BASE}/pathologies"):
            classes['nav-path'] = active_class
        elif _is(pathname, f"{BASE}/profil"):
            classes['nav-profil'] = active_class
        elif _is(pathname, f"{BASE}/traitements"):
            classes['nav-trait'] = active_class
        elif _is(pathname, f"{BASE}/risques"):
            classes['nav-risk'] = active_class
        elif _is(pathname, f"{BASE}/analyses"):
            classes['nav-analytics'] = active_class
        
        return [classes[k] for k in ['nav-home', 'nav-org', 'nav-path', 'nav-profil', 'nav-trait', 'nav-risk', 'nav-analytics']]
