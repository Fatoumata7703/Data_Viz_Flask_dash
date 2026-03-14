"""Cartes d'indicateurs clés (KPI)"""
import dash_bootstrap_components as dbc
from dash import html

def create_kpi_cards(kpis):
    """Crée les cartes d'indicateurs clés"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div("📊", className="kpi-icon"),
                    html.P("Durée Moyenne de Séjour", className="kpi-title"),
                    html.H3(f"{kpis['duree_moyenne']:.1f} jours", className="kpi-value"),
                    html.P("jours", className="kpi-change", style={'color': 'var(--text-muted)'})
                ])
            ], className="kpi-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div("💰", className="kpi-icon"),
                    html.P("Coût Moyen par Patient", className="kpi-title"),
                    html.H3(f"{kpis['cout_moyen_patient']:.0f} €", className="kpi-value"),
                    html.P("par patient", className="kpi-change", style={'color': 'var(--text-muted)'})
                ])
            ], className="kpi-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div("📅", className="kpi-icon"),
                    html.P("Coût par Jour", className="kpi-title"),
                    html.H3(f"{kpis['cout_par_jour']:.0f} €", className="kpi-value"),
                    html.P("par jour", className="kpi-change", style={'color': 'var(--text-muted)'})
                ])
            ], className="kpi-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div("👥", className="kpi-icon"),
                    html.P("Total Patients", className="kpi-title"),
                    html.H3(f"{kpis['total_patients']:.0f}", className="kpi-value"),
                    html.P("patients", className="kpi-change", style={'color': 'var(--text-muted)'})
                ])
            ], className="kpi-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div("⚠️", className="kpi-icon"),
                    html.P("Patients à Risque", className="kpi-title"),
                    html.H3(f"{kpis['patients_risque']:.0f}", className="kpi-value"),
                    html.P(f"{kpis['taux_risque']:.1f}% du total", className="kpi-change")
                ])
            ], className="kpi-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div("📈", className="kpi-icon"),
                    html.P("Efficacité Globale", className="kpi-title"),
                    html.H3(f"{(1/(kpis['cout_par_jour']*kpis['duree_moyenne']/1000)):.2f}", className="kpi-value"),
                    html.P("score", className="kpi-change", style={'color': 'var(--text-muted)'})
                ])
            ], className="kpi-card")
        ], width=12, md=6, lg=2),
    ], className="mb-4")
