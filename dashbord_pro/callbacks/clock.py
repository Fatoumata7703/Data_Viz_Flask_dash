"""Callback pour l'horloge en temps réel"""
from dash import Input, Output, dcc
from datetime import datetime

def register_clock_callback(app):
    """Enregistre le callback pour l'horloge avec interval"""
    # Ajouter un interval component pour mettre à jour toutes les secondes
    # Ce sera géré côté client avec JavaScript
    
    @app.callback(
        Output('live-clock', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_clock(n):
        """Met à jour l'horloge"""
        return datetime.now().strftime("%H:%M:%S")
