"""Module callbacks - Enregistre tous les callbacks"""
from callbacks.navigation import register_navigation_callbacks
from callbacks.organization import register_organization_callbacks
from callbacks.pathology import register_pathology_callbacks
from callbacks.patient import register_patient_callbacks
from callbacks.treatment import register_treatment_callbacks
from callbacks.risk import register_risk_callbacks
from callbacks.analytics import register_analytics_callbacks
from callbacks.clock import register_clock_callback

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
