"""Page d'accueil - Vue d'ensemble avec KPIs"""
import dash_bootstrap_components as dbc
from dash import html
from ..welcome_card import create_welcome_card
from ..stat_cards import create_stat_cards
from ..alert_card import create_alert_card
from ..filters import create_filters
from ..kpi_bar import create_kpi_bar


def create_home_page(df):
    """Crée la page d'accueil"""
    from dashbord_pro.utils import calculate_kpis

    kpis = calculate_kpis(df)

    return html.Div(
        [
            html.Div(
                [
                    # Bandeau de bienvenue pleine largeur
                    create_welcome_card(df),

                    # Barre horizontale de KPIs (compacte, réutilisable)
                    create_kpi_bar(kpis, df),

                    # Carte alerte pleine colonne (les gros blocs sont retirés)
                    html.Div(
                        create_alert_card(int(kpis["patients_risque"])),
                        className="home-alert-full",
                    ),
                ],
                className="page-container home-page",
            ),
        ]
    )
