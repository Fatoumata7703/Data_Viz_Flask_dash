"""Callbacks pour la navigation entre les pages — préfixe /pro pour montage Flask"""
from dash import Input, Output
from dashbord_pro.layout.pages.home import create_home_page
from dashbord_pro.layout.pages.organization import create_organization_page
from dashbord_pro.layout.pages.pathology import create_pathology_page
from dashbord_pro.layout.pages.patient import create_patient_page
from dashbord_pro.layout.pages.treatment import create_treatment_page
from dashbord_pro.layout.pages.risk import create_risk_page
from dashbord_pro.layout.pages.analytics import create_analytics_page

BASE = "/pro"

def _n(p):
    return (p or "").rstrip("/") or "/"

def _is(pathname, *paths):
    """Vrai si pathname correspond à l'un des paths. En ligne pathname peut être /data_viz/pro/..., /pro/... ou /profil."""
    if pathname is None:
        return False
    pathname = _n(pathname)
    # Chemins complets (ex. /data_viz/pro/organisation)
    if pathname in (_n(p) for p in paths):
        return True
    # Variante sans préfixe (ex. /pro ou /pro/organisation)
    short_base = "/pro"
    for p in paths:
        n = _n(p)
        if n == BASE or n.startswith(BASE + "/"):
            tail = n[len(BASE):] if len(n) > len(BASE) else "/"
            short = _n(short_base + tail)
            if pathname == short:
                return True
    # Dernier recours : pathname peut être juste le segment (ex. /profil, /organisation) en prod
    for p in paths:
        n = _n(p)
        segment = n.split("/")[-1] if n != "/" else ""
        if segment and (pathname == "/" + segment or pathname == segment):
            return True
    return False

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
