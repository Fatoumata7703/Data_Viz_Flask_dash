"""Utilitaires pour les graphiques avec thème moderne"""
from callbacks.constants import COLORS

def get_modern_layout(title, xaxis_title, yaxis_title, height=400):
    """Retourne un layout moderne pour les graphiques"""
    return {
        'title': title,
        'xaxis_title': xaxis_title,
        'yaxis_title': yaxis_title,
        'template': 'plotly_dark',
        'plot_bgcolor': COLORS['bg-card'],
        'paper_bgcolor': COLORS['bg-card'],
        'font': dict(color='white', family='Inter'),
        'height': height,
        'hovermode': 'closest'
    }
