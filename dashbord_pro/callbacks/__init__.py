"""Module callbacks - Enregistre tous les callbacks (imports relatifs pour éviter circular import sous uWSGI)."""
from .navigation import register_navigation_callbacks
from .organization import register_organization_callbacks
from .pathology import register_pathology_callbacks
from .patient import register_patient_callbacks
from .treatment import register_treatment_callbacks
from .risk import register_risk_callbacks
from .analytics import register_analytics_callbacks
from .clock import register_clock_callback

def register_all_callbacks(app, df):
    """Enregistre tous les callbacks du dashboard"""
    register_navigation_callbacks(app, df)
    register_organization_callbacks(app, df)
    register_pathology_callbacks(app, df)
    register_patient_callbacks(app, df)
    register_treatment_callbacks(app, df)
    register_risk_callbacks(app, df)
    register_analytics_callbacks(app, df)
    register_clock_callback(app)
