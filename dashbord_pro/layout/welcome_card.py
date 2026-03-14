"""Carte de bienvenue - Vert clair couleur hospitalière"""
from dash import html, dcc
from datetime import datetime
from layout.icons import create_icon_svg

def create_welcome_card(df):
    """Crée la carte de bienvenue avec les couleurs vertes hospitalières"""
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    # Déterminer le moment de la journée
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Bonjour"
    elif hour < 18:
        greeting = "Bon après-midi"
    else:
        greeting = "Bonsoir"
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div(create_icon_svg('smiley', 64, color='#10b981'), className="welcome-icon"),
                    html.Div([
                        html.H2(f"{greeting} 👋", style={'margin': 0, 'color': '#10b981', 'fontSize': '1.5rem', 'fontWeight': '700'}),
                        html.Div([
                            html.Div([
                                html.Div(create_icon_svg('clock', 18, color='#6b7280'), style={'display': 'flex', 'alignItems': 'center'}),
                                html.Span(f"{current_date} à {current_time}")
                            ], className="welcome-info-item"),
                            html.Div([
                                html.Div(create_icon_svg('location', 18, color='#dc2626'), style={'display': 'flex', 'alignItems': 'center'}),
                                html.Span("Hôpital Central")
                            ], className="welcome-info-item"),
                            html.Div([
                                html.Div(create_icon_svg('online', 18, color='#10b981'), style={'display': 'flex', 'alignItems': 'center'}),
                                html.Span("En ligne")
                            ], className="welcome-info-item")
                        ], className="welcome-info")
                    ])
                ], className="welcome-left"),
                html.Div([
                    html.Div(current_time, className="clock-display", id="live-clock"),
                    html.Div("Temps réel", className="realtime-badge"),
                    dcc.Interval(
                        id='interval-component',
                        interval=1000,  # en millisecondes
                        n_intervals=0
                    )
                ], className="welcome-right")
            ], className="welcome-card")
        ])
    ])
