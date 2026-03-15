"""Barre horizontale de KPIs réutilisable sur les onglets."""
from dash import html
from .icons import create_icon_svg


def create_kpi_bar(kpis, df):
    """Retourne une barre de KPIs compacte, scrollable horizontalement."""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        create_icon_svg("hospital-building", 20),
                        className="kpi-icon",
                        style={"background": "rgba(16,185,129,0.35)"},
                    ),
                    html.Div(
                        [
                            html.Div("Départements", className="kpi-title"),
                            html.Div(f"{len(df['Departement'].unique())}", className="kpi-value"),
                            html.P("Actifs", className="kpi-change"),
                        ]
                    ),
                ],
                className="kpi-card",
                style={"--stat-color": "#10b981"},
            ),
            html.Div(
                [
                    html.Div(
                        create_icon_svg("users-group", 20),
                        className="kpi-icon",
                        style={"background": "rgba(59,130,246,0.35)"},
                    ),
                    html.Div(
                        [
                            html.Div("Total Patients", className="kpi-title"),
                            html.Div(f"{kpis['total_patients']:.0f}", className="kpi-value"),
                            html.P("Enregistrés", className="kpi-change"),
                        ]
                    ),
                ],
                className="kpi-card",
                style={"--stat-color": "#3b82f6"},
            ),
            html.Div(
                [
                    html.Div(
                        create_icon_svg("pill", 20),
                        className="kpi-icon",
                        style={"background": "rgba(139,92,246,0.18)"},
                    ),
                    html.Div(
                        [
                            html.Div("Traitements", className="kpi-title"),
                            html.Div(f"{len(df['Traitement'].unique())}", className="kpi-value"),
                            html.P("Disponibles", className="kpi-change"),
                        ]
                    ),
                ],
                className="kpi-card",
                style={"--stat-color": "#8b5cf6"},
            ),
            html.Div(
                [
                    html.Div(
                        create_icon_svg("alert-warning", 20),
                        className="kpi-icon",
                        style={"background": "rgba(251,191,36,0.4)"},
                    ),
                    html.Div(
                        [
                            html.Div("À risque", className="kpi-title"),
                            html.Div(f"{kpis['patients_risque']:.0f}", className="kpi-value"),
                            html.P("Nouveau à traiter", className="kpi-change"),
                        ]
                    ),
                ],
                className="kpi-card",
                style={"--stat-color": "#fbbf24"},
            ),
        ],
        className="kpi-bar",
    )

