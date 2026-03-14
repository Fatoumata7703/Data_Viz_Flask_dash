"""
Dashboard Exercice 6 — Suivi et analyse de la production d'énergie solaire.
Style type Power BI : palette professionnelle, filtres clairs, data analytics.
Données : MongoDB Atlas (flash_dash.solar) ou CSV en secours.
"""
import os
import sys
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from datetime import datetime, timedelta

# Config MongoDB Atlas (racine du projet)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
try:
    import config_mongo as _cfg
except ImportError:
    _cfg = None

# —— Thème SOLAIRE : tons doux, moins vifs (terracotta / ambre discret) ——
THEME = dbc.themes.FLATLY
SOLAR_ORANGE = "#b87333"     # Terracotta (primary)
SOLAR_AMBER = "#c99a5c"     # Ambre doux
SOLAR_YELLOW = "#c9a227"    # Or discret
SOLAR_GOLD = "#b8960f"      # Or mat
SOLAR_DARK = "#2d2d2d"      # Texte fort
SOLAR_CREAM = "#f8f5f0"     # Fond crème très doux
SOLAR_CARD = "#ffffff"
SOLAR_BORDER = "#e0d8cc"
SOLAR_TEXT = "#3d3d3d"
SOLAR_TEXT_MUTED = "#6b5b4f"
# Couleurs séries : AC / DC moins saturées
SOLAR_AC = "#b87333"
SOLAR_DC = "#9a5a2e"
SOLAR_SUCCESS = "#3d7a5c"
SOLAR_WARN = "#b85454"

# Palette graphiques — qui colle avec l’interface (image 2) mais variée (comme images 3/4)
GRAPH_PRIMARY = "#ea580c"   # Rouge-orange soleil (série principale AC)
GRAPH_SECONDARY = "#0ea5e9" # Bleu (DC, 2e série — contraste)
GRAPH_TERTIARY = "#3d7a5c"  # Vert (efficiency, MA30, positif)
GRAPH_AMBER = "#d97706"     # Ambre (projection, saisonnalité)
GRAPH_GOLD = "#ca8a04"      # Or (rendement, autres séries)
GRAPH_PURPLE = "#7c3aed"    # Violet (variété, 3e série si besoin)

# Config graphiques (sans xaxis/yaxis pour éviter "multiple values" dans update_layout)
def _graph_layout(**kwargs):
    base = dict(
        template="plotly_white",
        font=dict(family="Segoe UI, system-ui, sans-serif", size=12, color=SOLAR_TEXT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,245,240,0.5)",
        margin=dict(t=50, b=45, l=55, r=25),
        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_color=SOLAR_TEXT, bordercolor=GRAPH_PRIMARY),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.9)", bordercolor=SOLAR_BORDER, borderwidth=1, font=dict(size=11)),
        uirevision="layout_stable",
    )
    base.update(kwargs)
    return base

GRAPH_CFG = {"responsive": True, "displayModeBar": False}
GRAPH_CFG_STATIC = {"responsive": False, "displayModeBar": False, "staticPlot": False}

_AXIS = dict(gridcolor="rgba(232,220,200,0.45)", gridwidth=1,
             zerolinecolor="rgba(232,220,200,0.55)", zerolinewidth=1,
             showline=True, linewidth=1, linecolor="rgba(232,220,200,0.7)")
_XAXIS = {**_AXIS, "tickfont": dict(size=10, color="#6b5b4f")}
_YAXIS = {**_AXIS, "tickfont": dict(size=10, color="#6b5b4f")}
GH = 370
GH_FULL = 420


def load_solar_data():
    df = None
    if _cfg and getattr(_cfg, "MONGO_URI", "").strip() and "mongodb+srv" in getattr(_cfg, "MONGO_URI", ""):
        try:
            from pymongo import MongoClient
            client = MongoClient(_cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
            coll = client[_cfg.FLASH_DASH_DB][_cfg.SOLAR_COLLECTION]
            docs = list(coll.find({}))
            client.close()
            if docs:
                for d in docs:
                    d.pop("_id", None)
                df = pd.DataFrame(docs)
        except Exception:
            pass
    if df is None or len(df) == 0:
        try:
            data_dir = os.path.join(_root, "data")
            df = pd.read_csv(os.path.join(data_dir, "solar_data.csv"), sep=';')
        except FileNotFoundError:
            df = pd.read_csv(os.path.join(_root, "data", "salar_data.csv"), sep=';')
    if 'Time' in df.columns and 'Hour' not in df.columns:
        df['Hour'] = df['Time']
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    # Heure entière 0-23 pour filtres (8h-18h)
    if 'Hour' in df.columns:
        df['Hour'] = pd.to_numeric(df['Hour'], errors='coerce').fillna(0).astype(int).clip(0, 23)
    else:
        df['Hour'] = df['DateTime'].dt.hour
    # Efficacité AC/DC (si DC > 0)
    df['Efficiency'] = np.where(df['DC_Power'] > 0, df['AC_Power'] / df['DC_Power'] * 100, np.nan)
    return df


def create_dash_app(server, url_base_pathname):
    df = load_solar_data()
    date_min = df['Date'].min()
    date_max = df['Date'].max()
    date_min_str = pd.Timestamp(date_min).strftime('%Y-%m-%d') if pd.notna(date_min) else None
    date_max_str = pd.Timestamp(date_max).strftime('%Y-%m-%d') if pd.notna(date_max) else None

    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname=url_base_pathname,
        external_stylesheets=[THEME],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )

    # Filtres appliqués (mis à jour par présets ou bouton Appliquer) — source de vérité pour tous les callbacks
    applied_default = {'start': date_min_str, 'end': date_max_str, 'site': None}
    app.config.suppress_callback_exceptions = True
    sites = [{'label': 'Tous les sites', 'value': None}]
    if 'Country' in df.columns:
        for s in sorted(df['Country'].dropna().unique()):
            sites.append({'label': str(s), 'value': str(s)})

    filter_card = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Icône + Filtres rapides
                dbc.Col([
                    html.Div([
                        html.Span("🔍", style={"fontSize": "1.1rem", "marginRight": "6px"}),
                        html.Span("Filtres", style={"fontWeight": "700", "fontSize": "0.85rem", "color": SOLAR_TEXT, "letterSpacing": "0.02em"}),
                    ], className="d-flex align-items-center mb-2"),
                    html.Div([
                        dbc.Button("7j", id="preset-7", size="sm", className="solar-pill-btn me-1"),
                        dbc.Button("30j", id="preset-30", size="sm", className="solar-pill-btn me-1"),
                        dbc.Button("90j", id="preset-90", size="sm", className="solar-pill-btn me-1"),
                        dbc.Button("Année", id="preset-year", size="sm", className="solar-pill-btn me-1"),
                        dbc.Button("Tout", id="preset-all", size="sm", className="solar-pill-btn"),
                    ], className="d-flex flex-wrap"),
                ], md=4, className="d-flex flex-column justify-content-center"),
                # Du
                dbc.Col([
                    html.Div("📅 Du", style={"fontWeight": "600", "fontSize": "0.75rem", "color": SOLAR_TEXT_MUTED, "marginBottom": "4px"}),
                    dcc.DatePickerSingle(id='date-start', date=date_min_str, display_format='DD/MM/YYYY', className="solar-date-single"),
                ], md=2, className="d-flex flex-column justify-content-center"),
                # Au
                dbc.Col([
                    html.Div("📅 Au", style={"fontWeight": "600", "fontSize": "0.75rem", "color": SOLAR_TEXT_MUTED, "marginBottom": "4px"}),
                    dcc.DatePickerSingle(id='date-end', date=date_max_str, display_format='DD/MM/YYYY', className="solar-date-single"),
                ], md=2, className="d-flex flex-column justify-content-center"),
                # Site
                dbc.Col([
                    html.Div("📍 Site", style={"fontWeight": "600", "fontSize": "0.75rem", "color": SOLAR_TEXT_MUTED, "marginBottom": "4px"}),
                    dcc.Dropdown(id='filter-site', options=sites, value=None, clearable=False, placeholder="Tous les sites", className="solar-dropdown"),
                ], md=3, className="d-flex flex-column justify-content-center"),
            ], className="g-3 align-items-end"),
        ], className="py-3 px-4"),
    ], className="solar-filter-bar mb-4")
    # Bouton caché pour garder la compatibilité
    hidden_apply = html.Button(id="btn-apply-filters", n_clicks=0, style={"display": "none"})

    # —— KPIs : jolies blocs — fond blanc, bordure gauche épaisse arrondie, ombre légère ——
    def kpi_card(icon, title, id_value, border_color, bg_tint):
        return dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span(icon, style={"fontSize": "1.35rem", "marginRight": "8px"}),
                        html.Span(title, className="solar-kpi-label"),
                    ], className="d-flex align-items-center mb-1"),
                    html.H3(id=id_value, className="solar-kpi-value mb-0", style={"color": SOLAR_DARK}),
                ], style={"padding": "1rem 1.15rem"}),
            ], className="solar-kpi-card h-100", style={"borderLeft": f"6px solid {border_color}", "background": "#ffffff"}),
            lg=2, md=4, sm=6, className="mb-3"
        )
    kpi_row = dbc.Row([
        kpi_card("⚡", "Production AC", 'total-ac-power', SOLAR_ORANGE, "#f5efe8"),
        kpi_card("⚡", "Production DC", 'total-dc-power', SOLAR_AMBER, "#f7f2e8"),
        kpi_card("📊", "Rendement AC/DC", 'efficiency-ac-dc', SOLAR_GOLD, "#f5f2e8"),
        kpi_card("⏱", "Prod. moy/h", 'avg-hourly-power', SOLAR_SUCCESS, "#e8f0ea"),
        kpi_card("🚨", "Anomalies", 'anomaly-pct', SOLAR_WARN, "#f5e8e8"),
        kpi_card("🌡", "Temp. module", 'temp-module-kpi', SOLAR_AMBER, "#f7f2e8"),
    ], className="g-3 mb-4")

    # —— Helper : carte graphique élégante (height fixe = pas de décalage au chargement) ——
    def gcard(title, graph_id, full=False, config=None, height=None):
        cfg = config if config is not None else GRAPH_CFG
        graph_el = dcc.Graph(id=graph_id, config=cfg)
        if height is not None:
            graph_el = html.Div(graph_el, className="solar-graph-fixed-height", style={"height": f"{height}px", "minHeight": f"{height}px"})
        return dbc.Col(dbc.Card([
            dbc.CardHeader(title, className="solar-card-title"),
            dbc.CardBody(graph_el, className="p-2"),
        ], className="solar-content-card h-100"), md=12 if full else 6, className="mb-4")

    def gcard_custom(title, children, full=False):
        return dbc.Col(dbc.Card([
            dbc.CardHeader(title, className="solar-card-title"),
            dbc.CardBody(children, className="p-3"),
        ], className="solar-content-card h-100"), md=12 if full else 6, className="mb-4")

    def page_title(icon, title, subtitle):
        return html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "1.4rem", "marginRight": "8px"}),
                html.Span(title, style={"fontSize": "1.15rem", "fontWeight": "800", "color": SOLAR_TEXT}),
            ], className="d-flex align-items-center"),
            html.Div(subtitle, style={"fontSize": "0.8rem", "color": SOLAR_TEXT_MUTED, "marginTop": "2px", "marginLeft": "2rem"}),
        ], className="mb-3 pb-2", style={"borderBottom": f"2px solid {SOLAR_ORANGE}"})

    # ═══════════ PAGE 1 — OVERVIEW ═══════════
    page_overview = html.Div([
        page_title("☀️", "Vue d'ensemble", "Vision synthétique et décisionnelle"),
        dbc.Row([
            gcard("Production Horaire — AC vs DC", 'hourly-production-graph', full=True),
        ]),
        dbc.Row([
            gcard("Production Journalière", 'daily-production-graph'),
            gcard("Production Cumulée", 'overview-cumulative-graph'),
        ]),
        dbc.Row([
            gcard("Efficacité dans le temps (AC/DC %)", 'overview-efficiency-graph'),
            gcard_custom("🤖 IA Insights", html.Div(id='ia-insights-block')),
        ]),
    ], id="page-overview")

    # ═══════════ PAGE 2 — PERFORMANCE ═══════════
    page_performance = html.Div([
        page_title("📊", "Analyse de Performance", "Analyse technique approfondie"),
        dbc.Row([
            gcard("Efficacité AC/DC — seuil 90 %", 'perf-efficiency-graph', config=GRAPH_CFG_STATIC, height=380),
            gcard_custom("Distribution du rendement", [
                html.Div(id='perf-efficiency-stats', style={"minHeight": "44px"}),
                html.Div(dcc.Graph(id='perf-efficiency-histogram', config=GRAPH_CFG_STATIC), className="solar-graph-fixed-height", style={"height": "300px", "minHeight": "300px"}),
            ]),
        ]),
        dbc.Row([
            gcard("Top 5 / Pire 5 jours", 'perf-daily-bar-graph'),
            gcard("Moyenne mobile 7j & 30j", 'perf-rolling-graph'),
        ]),
        dbc.Row([
            gcard_custom("Comparaison périodes", html.Div(id='perf-comparison-block')),
            gcard("Production moyenne par heure", 'avg-hourly-pattern-graph'),
        ]),
    ], id="page-performance", style={"display": "none"})

    # ═══════════ PAGE 3 — ENVIRONNEMENT ═══════════
    page_environment = html.Div([
        page_title("🌡", "Environnement & Impact Climatique", "Analyse scientifique des conditions"),
        dbc.Row([
            gcard_custom("Temp. module vs Production", [
                html.Div(id='env-correlation-r', style={"minHeight": "44px"}),
                html.Div(dcc.Graph(id='temp-vs-production-graph', config=GRAPH_CFG_STATIC), className="solar-graph-fixed-height", style={"height": "380px", "minHeight": "380px"}),
            ]),
            gcard("Temp. ambiante vs Efficacité", 'env-ambient-vs-efficiency-graph', config=GRAPH_CFG_STATIC, height=380),
        ]),
        dbc.Row([
            gcard("Production par plage de température", 'env-temp-bands-graph', config=GRAPH_CFG_STATIC, height=380),
            gcard("Heatmap Horaire (Heure × Date)", 'heatmap-irradiation-production', config=GRAPH_CFG_STATIC, height=420),
        ]),
        dbc.Row([
            gcard_custom("Impact Irradiation", [
                html.Div(id='env-irradiation-corr', style={"minHeight": "44px"}),
                html.Div(dcc.Graph(id='env-irradiation-graph', config=GRAPH_CFG_STATIC), className="solar-graph-fixed-height", style={"height": "380px", "minHeight": "380px"}),
            ], full=True),
        ]),
    ], id="page-environment", style={"display": "none"})

    # ═══════════ PAGE 4 — ANOMALIES ═══════════
    page_anomalies = html.Div([
        page_title("🚨", "Détection d'Anomalies", "Supervision & maintenance"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([html.Div("% prod. nulle", className="solar-kpi-label"), html.H3(id="anom-pct-nulle", className="solar-kpi-value mb-0", style={"color": SOLAR_WARN})])], className="solar-kpi-card h-100"), md=3, className="mb-3"),
            dbc.Col(dbc.Card([dbc.CardBody([html.Div("Nb incidents", className="solar-kpi-label"), html.H3(id="anom-nb-incidents", className="solar-kpi-value mb-0", style={"color": SOLAR_ORANGE})])], className="solar-kpi-card h-100"), md=3, className="mb-3"),
            dbc.Col(dbc.Card([dbc.CardBody([html.Div("Durée moy. panne", className="solar-kpi-label"), html.H3(id="anom-duree-moy", className="solar-kpi-value mb-0", style={"color": SOLAR_AMBER})])], className="solar-kpi-card h-100"), md=3, className="mb-3"),
            dbc.Col(dbc.Card([dbc.CardBody([html.Div("Plus longue panne", className="solar-kpi-label"), html.H3(id="anom-max-panne", className="solar-kpi-value mb-0", style={"color": SOLAR_WARN})])], className="solar-kpi-card h-100"), md=3, className="mb-3"),
        ], className="g-3 mb-2"),
        dbc.Row([
            gcard("Production nulle en journée (8h–18h)", 'anom-nulle-journee-graph'),
            gcard("Efficacité < 80 %", 'anom-efficiency-graph'),
        ]),
        dbc.Row([
            gcard_custom("Tableau des incidents", html.Div(id='anom-table-incidents')),
            gcard("Anomalies par mois", 'anom-by-month-graph'),
        ]),
    ], id="page-anomalies", style={"display": "none"})

    # ═══════════ PAGE 5 — ANALYSE AVANCÉE ═══════════
    page_advanced = html.Div([
        page_title("📈", "Analyse Avancée", "Niveau Data Science"),
        dbc.Row([
            gcard("Prévision — MA 7j + projection 30j", 'adv-forecast-graph'),
            gcard("Outliers (méthode IQR)", 'adv-outliers-graph'),
        ]),
        dbc.Row([
            gcard("Décomposition : Tendance, Saisonnalité, Résidu", 'adv-decomposition-graph'),
            gcard("Performance annuelle comparée", 'adv-annual-graph'),
        ]),
    ], id="page-advanced", style={"display": "none"})

    pages_container = html.Div([
        page_overview, page_performance, page_environment, page_anomalies, page_advanced,
    ], id="pages-container")

    # —— Layout principal : Header (icône, titre, sous-titre, Export), Filtres, Store, KPIs, Sidebar + contenu ——
    header = dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div("☀️", style={"fontSize": "2.2rem", "lineHeight": "1"}), width="auto"),
                dbc.Col([
                    html.Div("Suivi & Analyse de la Production Solaire", style={"fontWeight": "800", "fontSize": "1.25rem", "letterSpacing": "0.01em", "color": "#fff"}),
                    html.Div("Dashboard interactif de suivi de la production d'énergie solaire", style={"fontSize": "0.82rem", "opacity": "0.9", "marginTop": "2px", "color": "#fff"}),
                ], width="auto"),
                dbc.Col([
                    dbc.Button(["📄 Exporter PDF"], id="btn-export-pdf", size="sm", className="solar-btn-pdf"),
                ], width="auto", className="ms-auto d-flex align-items-center"),
            ], className="g-3 align-items-center", style={"width": "100%"}),
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4",
        style={"padding": "0.9rem 0"},
    )
    sidebar_nav = html.Div([
        html.Div("NAVIGATION", style={"fontSize": "0.65rem", "fontWeight": "700", "letterSpacing": "0.1em", "color": SOLAR_TEXT_MUTED, "padding": "0.4rem 0.8rem 0.5rem", "textTransform": "uppercase"}),
        dbc.Button("☀️  Overview", id="nav-overview", n_clicks=0, className="solar-sidebar-btn solar-sidebar-btn-active", color="link"),
        dbc.Button("📊  Performance", id="nav-performance", n_clicks=0, className="solar-sidebar-btn", color="link"),
        dbc.Button("🌡  Environnement", id="nav-environment", n_clicks=0, className="solar-sidebar-btn", color="link"),
        dbc.Button("🚨  Anomalies", id="nav-anomalies", n_clicks=0, className="solar-sidebar-btn", color="link"),
        dbc.Button("📈  Analyse avancée", id="nav-advanced", n_clicks=0, className="solar-sidebar-btn", color="link"),
    ], className="solar-sidebar-nav mb-4")

    app.layout = dbc.Container([
        header,
        dcc.Store(id='applied-filters', data=applied_default),
        dcc.Download(id="download-pdf"),
        html.Div(id="pdf-print-trigger", style={"display": "none"}),
        hidden_apply,
        filter_card,
        kpi_row,
        dbc.Row([
            dbc.Col(sidebar_nav, md=2, className="solar-sidebar-col"),
            dbc.Col(pages_container, md=10),
        ]),
    ], fluid=True, className="py-4", style={"backgroundColor": SOLAR_CREAM, "minHeight": "100vh", "fontFamily": "Segoe UI, system-ui, sans-serif"})

    # —— Sidebar : clic -> afficher/masquer les pages + surligner le bouton actif ——
    @app.callback(
        [Output('page-overview', 'style'), Output('page-performance', 'style'),
         Output('page-environment', 'style'), Output('page-anomalies', 'style'),
         Output('page-advanced', 'style'),
         Output('nav-overview', 'className'), Output('nav-performance', 'className'),
         Output('nav-environment', 'className'), Output('nav-anomalies', 'className'),
         Output('nav-advanced', 'className')],
        [Input('nav-overview', 'n_clicks'), Input('nav-performance', 'n_clicks'),
         Input('nav-environment', 'n_clicks'), Input('nav-anomalies', 'n_clicks'),
         Input('nav-advanced', 'n_clicks')],
    )
    def switch_page(n_o, n_p, n_e, n_a, n_adv):
        from dash import ctx
        pages = ['overview', 'performance', 'environment', 'anomalies', 'advanced']
        nav_map = {'nav-overview': 0, 'nav-performance': 1, 'nav-environment': 2, 'nav-anomalies': 3, 'nav-advanced': 4}
        active_idx = nav_map.get(ctx.triggered_id, 0)
        show = {"display": "block"}
        hide = {"display": "none"}
        styles = [show if i == active_idx else hide for i in range(5)]
        base = "solar-sidebar-btn"
        active_cls = "solar-sidebar-btn solar-sidebar-btn-active"
        classes = [active_cls if i == active_idx else base for i in range(5)]
        return *styles, *classes

    # —— Filtres automatiques : tout changement met à jour immédiatement ——
    @app.callback(
        [Output('date-start', 'date'), Output('date-end', 'date'), Output('applied-filters', 'data')],
        [Input('date-start', 'date'), Input('date-end', 'date'), Input('filter-site', 'value'),
         Input('preset-7', 'n_clicks'), Input('preset-30', 'n_clicks'),
         Input('preset-90', 'n_clicks'), Input('preset-year', 'n_clicks'),
         Input('preset-all', 'n_clicks')],
        prevent_initial_call=True,
    )
    def update_filters(start_d, end_d, site, n7, n30, n90, nyear, nall):
        from dash import ctx
        tid = ctx.triggered_id
        if tid in ('preset-7', 'preset-30', 'preset-90', 'preset-year', 'preset-all'):
            end = pd.Timestamp(date_max)
            if tid == 'preset-7':
                start = end - timedelta(days=7)
            elif tid == 'preset-30':
                start = end - timedelta(days=30)
            elif tid == 'preset-90':
                start = end - timedelta(days=90)
            elif tid == 'preset-year':
                start = end - timedelta(days=365)
            else:
                start = pd.Timestamp(date_min)
            s, e = start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
            return s, e, {'start': s, 'end': e, 'site': site}
        s = start_d or date_min_str
        e = end_d or date_max_str
        return s, e, {'start': s, 'end': e, 'site': site}

    def _filter_df(start_date, end_date, site=None):
        out = df.copy()
        if start_date and end_date:
            out = out[(out['Date'] >= start_date) & (out['Date'] <= end_date)]
        if site and 'Country' in out.columns:
            out = out[out['Country'].astype(str) == str(site)]
        return out.copy()

    # —— Export Excel (données filtrées) ——
    @app.callback(
        Output('download-excel', 'data'),
        Input('btn-export-excel', 'n_clicks'),
        State('applied-filters', 'data'),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks, applied_filters):
        if not n_clicks:
            return dash.no_update
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        from io import StringIO
        buf = StringIO()
        fd.to_csv(buf, index=False, sep=';', decimal=',')
        return dict(content=buf.getvalue(), filename=f"export_solaire_{applied_filters.get('start', '')}_{applied_filters.get('end', '')}.csv")

    # —— Export PDF (ouvre la boîte d'impression du navigateur → Enregistrer en PDF) ——
    app.clientside_callback(
        "function(n) { if (n) window.print(); return null; }",
        Output('pdf-print-trigger', 'children'),
        Input('btn-export-pdf', 'n_clicks'),
    )

    # —— KPIs ——
    @app.callback(
        [Output('total-ac-power', 'children'), Output('total-dc-power', 'children'),
         Output('efficiency-ac-dc', 'children'), Output('avg-hourly-power', 'children'),
         Output('anomaly-pct', 'children'), Output('temp-module-kpi', 'children')],
        Input('applied-filters', 'data'),
    )
    def update_stats(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        total_ac = fd['AC_Power'].sum()
        total_dc = fd['DC_Power'].sum()
        efficiency = (total_ac / total_dc * 100) if total_dc > 0 else 0
        n_hours = max(1, len(fd))
        avg_hourly = total_ac / n_hours
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        journee = fd[(fd['Hour'] >= 8) & (fd['Hour'] <= 18)]
        total_j = len(journee)
        nulle_j = (journee['AC_Power'] == 0).sum() if total_j else 0
        pct_anom = (100.0 * nulle_j / total_j) if total_j else 0
        temp_mod = fd['Module_Temperature'].mean() if 'Module_Temperature' in fd.columns and fd['Module_Temperature'].notna().any() else None
        temp_str = f"{temp_mod:.1f} °C" if temp_mod is not None else "—"
        return (
            f"{total_ac:,.2f} kW",
            f"{total_dc:,.2f} kW",
            f"{efficiency:.1f} %",
            f"{avg_hourly:,.2f} kW",
            f"{pct_anom:.1f} %",
            temp_str,
        )

    # —— Production horaire ——
    @app.callback(
        Output('hourly-production-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_hourly(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fd['DateTime'], y=fd['AC_Power'], mode='lines', name='AC (kW)', line=dict(color=GRAPH_PRIMARY, width=2), fill='tozeroy', fillcolor='rgba(234,88,12,0.08)'))
        fig.add_trace(go.Scatter(x=fd['DateTime'], y=fd['DC_Power'], mode='lines', name='DC (kW)', line=dict(color=GRAPH_SECONDARY, width=2, dash='dot'), opacity=0.9))
        fig.update_layout(**_graph_layout(), height=380, hovermode='x unified', xaxis_title="Date et heure", yaxis_title="Production (kW)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— Production journalière ——
    @app.callback(
        Output('daily-production-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_daily(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Daily_Yield' in fd.columns:
            daily = fd.groupby('Date')['Daily_Yield'].last().reset_index()
            y_col, ylabel = 'Daily_Yield', 'Production (kWh)'
        else:
            daily = fd.groupby('Date')['AC_Power'].sum().reset_index()
            daily = daily.rename(columns={'AC_Power': 'Daily_AC'})
            y_col, ylabel = 'Daily_AC', 'Production AC (kW)'
        daily = daily.sort_values('Date')
        colors = [GRAPH_PRIMARY if v >= daily[y_col].quantile(0.75) else (GRAPH_AMBER if v >= daily[y_col].median() else 'rgba(14,165,233,0.4)') for v in daily[y_col]]
        fig = go.Figure(go.Bar(x=daily['Date'], y=daily[y_col], marker_color=colors, marker_line_width=0, hovertemplate='%{x|%d/%m/%Y}<br><b>%{y:,.0f}</b><extra></extra>'))
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Date", yaxis_title=ylabel, xaxis={**_XAXIS, "tickformat": "%d/%m"}, yaxis=_YAXIS, bargap=0.15)
        return fig

    # —— Production cumulée (onglet Production + Overview) ——
    def _make_cumulative_fig(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        if 'Total_Yield' in fd.columns:
            cumul = fd[['DateTime', 'Total_Yield']].drop_duplicates('DateTime', keep='last').sort_values('DateTime')
            x, y, ylabel = cumul['DateTime'], cumul['Total_Yield'], 'Production cumulée (kWh)'
        else:
            fd = fd.copy()
            fd['Cumul_AC'] = fd['AC_Power'].cumsum()
            x, y, ylabel = fd['DateTime'], fd['Cumul_AC'], 'Production AC cumulée (kW)'
        fig = go.Figure(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy', line=dict(color=GRAPH_PRIMARY, width=2.5, shape='spline'), fillcolor='rgba(234,88,12,0.1)', hovertemplate='%{x}<br><b>%{y:,.0f}</b><extra></extra>'))
        fig.update_layout(**_graph_layout(), height=380, hovermode='x unified', xaxis_title="Date et heure", yaxis_title=ylabel, xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    @app.callback(Output('overview-cumulative-graph', 'figure'), Input('applied-filters', 'data'))
    def update_overview_cumulative(applied_filters):
        return _make_cumulative_fig(applied_filters)

    # —— Courbe efficacité dans le temps (Overview) ——
    @app.callback(
        Output('overview-efficiency-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_overview_efficiency(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        if 'Efficiency' not in fd.columns:
            fig = go.Figure()
            fig.add_annotation(text="Efficiency non disponible", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(**_graph_layout(), height=400)
            return fig
        fig = go.Figure(go.Scatter(x=fd['DateTime'], y=fd['Efficiency'], mode='lines', name='Efficiency (%)', line=dict(color=GRAPH_TERTIARY, width=2, shape='spline'), fill='tozeroy', fillcolor='rgba(61,122,92,0.08)'))
        fig.add_hline(y=90, line_dash="dot", line_color="rgba(45,106,79,0.5)", annotation_text="Seuil 90%", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=380, hovermode='x unified', xaxis_title="Date et heure", yaxis_title="Efficiency (%)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— Bloc IA Insights (résumé auto) ——
    @app.callback(
        Output('ia-insights-block', 'children'),
        Input('applied-filters', 'data'),
    )
    def update_ia_insights(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        total_ac = fd['AC_Power'].sum()
        total_dc = fd['DC_Power'].sum()
        eff = (total_ac / total_dc * 100) if total_dc > 0 else 0
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        journee = fd[(fd['Hour'] >= 8) & (fd['Hour'] <= 18)]
        pct_anom = (100.0 * (journee['AC_Power'] == 0).sum() / len(journee)) if len(journee) else 0
        temp_mod = fd['Module_Temperature'].mean() if 'Module_Temperature' in fd.columns and fd['Module_Temperature'].notna().any() else None
        # Période précédente (même durée)
        start, end = applied_filters.get('start'), applied_filters.get('end')
        if start and end:
            delta = (pd.Timestamp(end) - pd.Timestamp(start)).days
            prev_end = pd.Timestamp(start) - timedelta(days=1)
            prev_start = prev_end - timedelta(days=delta)
            fd_prev = _filter_df(prev_start.strftime('%Y-%m-%d'), prev_end.strftime('%Y-%m-%d'), applied_filters.get('site'))
            ac_prev = fd_prev['AC_Power'].sum()
            var = ((total_ac - ac_prev) / ac_prev * 100) if ac_prev else 0
        else:
            var = 0
        var_color = SOLAR_SUCCESS if var >= 0 else SOLAR_WARN
        var_icon = "▲" if var >= 0 else "▼"
        def insight_row(icon, label, value, accent=SOLAR_ORANGE):
            return html.Div([
                html.Span(icon, style={"fontSize": "1.2rem", "marginRight": "10px"}),
                html.Span(label, style={"fontWeight": "600", "color": SOLAR_TEXT_MUTED, "fontSize": "0.82rem", "marginRight": "8px", "minWidth": "120px", "display": "inline-block"}),
                html.Span(value, style={"fontWeight": "800", "color": accent, "fontSize": "0.95rem"}),
            ], style={"padding": "8px 0", "borderBottom": "1px solid rgba(232,220,200,0.4)", "display": "flex", "alignItems": "center"})
        rows = [
            insight_row("⚡", "Production AC", f"{total_ac:,.0f} kW"),
            insight_row("📊", "Rendement AC/DC", f"{eff:.1f} %", SOLAR_AMBER),
            insight_row(var_icon, "Variation période", f"{var:+.1f} %", var_color),
            insight_row("🚨", "Anomalies", f"{pct_anom:.1f} % créneaux nuls", SOLAR_WARN if pct_anom > 5 else SOLAR_SUCCESS),
            insight_row("🌡", "Temp. module", f"{temp_mod:.1f} °C" if temp_mod is not None else "N/A", SOLAR_TEXT),
        ]
        return html.Div(rows)

    # —— PAGE 2 — Efficacité avec seuil 90 % ——
    @app.callback(
        Output('perf-efficiency-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_perf_efficiency(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        if 'Efficiency' not in fd.columns:
            fig = go.Figure()
            fig.add_annotation(text="Efficiency non disponible", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(**_graph_layout(), height=400, autosize=False)
            return fig
        fig = go.Figure(go.Scatter(x=fd['DateTime'], y=fd['Efficiency'], mode='lines', name='Efficiency (%)', line=dict(color=GRAPH_TERTIARY, width=2, shape='spline'), fill='tozeroy', fillcolor='rgba(61,122,92,0.06)'))
        fig.add_hline(y=90, line_dash="dot", line_color="rgba(230,57,70,0.6)", annotation_text="Seuil 90 %", annotation_font_size=10, annotation_font_color=SOLAR_WARN)
        fig.update_layout(**_graph_layout(), height=380, autosize=False, xaxis_title="Date et heure", yaxis_title="Efficiency (%)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— PAGE 2 — Stats + histogramme efficacité ——
    @app.callback(
        [Output('perf-efficiency-stats', 'children'), Output('perf-efficiency-histogram', 'figure')],
        Input('applied-filters', 'data'),
    )
    def update_perf_histogram(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Efficiency' not in fd.columns:
            return html.P("Efficiency non disponible.", className="text-muted"), go.Figure().update_layout(**_graph_layout(), height=350, autosize=False)
        eff = fd['Efficiency'].dropna()
        mean_e, median_e, std_e = eff.mean(), eff.median(), eff.std()
        def _badge(label, val, color):
            return html.Span([html.Small(label + " ", style={"fontWeight": "600", "color": SOLAR_TEXT_MUTED}), html.B(f"{val:.1f} %")], style={"background": f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)", "color": color, "padding": "4px 10px", "borderRadius": "6px", "fontSize": "0.8rem", "marginRight": "6px"})
        stats = html.Div([_badge("Moy.", mean_e, SOLAR_ORANGE), _badge("Méd.", median_e, SOLAR_AMBER), _badge("σ", std_e, SOLAR_TEXT)], className="mb-2 d-flex flex-wrap gap-1")
        fig = go.Figure(go.Histogram(x=eff, nbinsx=40, marker_color='rgba(14,165,233,0.5)', marker_line_color=GRAPH_SECONDARY, marker_line_width=0.5))
        fig.add_vline(x=mean_e, line_dash="dash", line_color=GRAPH_PRIMARY, line_width=2, annotation_text="μ", annotation_font_size=12, annotation_font_color=GRAPH_PRIMARY)
        fig.add_vline(x=median_e, line_dash="dot", line_color=SOLAR_SUCCESS, line_width=1.5, annotation_text="Med", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=300, autosize=False, xaxis_title="Efficiency (%)", yaxis_title="Effectif", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.05)
        return stats, fig

    # —— PAGE 2 — Bar chart rendement par jour, Top 5 / Pire 5 ——
    @app.callback(
        Output('perf-daily-bar-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_perf_daily_bar(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Efficiency' not in fd.columns:
            return go.Figure().update_layout(**_graph_layout(), height=400)
        daily_eff = fd.groupby('Date')['Efficiency'].mean().reset_index().sort_values('Efficiency', ascending=False)
        daily_eff = daily_eff.rename(columns={'Efficiency': 'Eff'})
        top5 = daily_eff.head(5)
        worst5 = daily_eff.tail(5)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=top5['Date'], y=top5['Eff'], name='Top 5', marker_color=GRAPH_TERTIARY, marker_line_width=0, hovertemplate='%{x|%d/%m}<br><b>%{y:.1f}%</b><extra>Top</extra>'))
        fig.add_trace(go.Bar(x=worst5['Date'], y=worst5['Eff'], name='Pire 5', marker_color=SOLAR_WARN, marker_line_width=0, hovertemplate='%{x|%d/%m}<br><b>%{y:.1f}%</b><extra>Pire</extra>'))
        fig.update_layout(**_graph_layout(), height=380, barmode='group', xaxis_title="Date", yaxis_title="Efficiency moy. (%)", xaxis={**_XAXIS, "tickformat": "%d/%m"}, yaxis=_YAXIS, bargap=0.2)
        return fig

    # —— PAGE 2 — Rolling 7j et 30j ——
    @app.callback(
        Output('perf-rolling-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_perf_rolling(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        if 'Efficiency' not in fd.columns or len(fd) < 7:
            return go.Figure().update_layout(**_graph_layout(), height=400)
        daily = fd.groupby('Date')['Efficiency'].mean().reset_index().sort_values('Date')
        daily['MA7'] = daily['Efficiency'].rolling(7, min_periods=1).mean()
        daily['MA30'] = daily['Efficiency'].rolling(30, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['Date'], y=daily['Efficiency'], mode='lines', name='Quotidien', line=dict(color='rgba(14,165,233,0.3)', width=1), hovertemplate='%{x|%d/%m/%Y}<br><b>Quotidien:</b> %{y:.2f} %<extra></extra>'))
        fig.add_trace(go.Scatter(x=daily['Date'], y=daily['MA7'], mode='lines', name='MA 7j', line=dict(color=GRAPH_PRIMARY, width=2.5, shape='spline'), hovertemplate='%{x|%d/%m/%Y}<br><b>MA 7j:</b> %{y:.2f} %<extra></extra>'))
        fig.add_trace(go.Scatter(x=daily['Date'], y=daily['MA30'], mode='lines', name='MA 30j', line=dict(color=GRAPH_TERTIARY, width=2.5, shape='spline', dash='dash'), hovertemplate='%{x|%d/%m/%Y}<br><b>MA 30j:</b> %{y:.2f} %<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Date", yaxis_title="Efficiency (%)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— PAGE 2 — Comparaison périodes ——
    @app.callback(
        Output('perf-comparison-block', 'children'),
        Input('applied-filters', 'data'),
    )
    def update_perf_comparison(applied_filters):
        applied_filters = applied_filters or applied_default
        start, end = applied_filters.get('start'), applied_filters.get('end')
        fd = _filter_df(start, end, applied_filters.get('site'))
        total_ac = fd['AC_Power'].sum()
        delta = (pd.Timestamp(end) - pd.Timestamp(start)).days if start and end else 0
        prev_end = pd.Timestamp(start) - timedelta(days=1)
        prev_start = prev_end - timedelta(days=delta)
        fd_prev = _filter_df(prev_start.strftime('%Y-%m-%d'), prev_end.strftime('%Y-%m-%d'), applied_filters.get('site'))
        ac_prev = fd_prev['AC_Power'].sum()
        var = ((total_ac - ac_prev) / ac_prev * 100) if ac_prev else 0
        var_c = SOLAR_SUCCESS if var >= 0 else SOLAR_WARN
        var_i = "▲" if var >= 0 else "▼"
        card_s = {"padding": "14px 18px", "borderRadius": "10px", "marginBottom": "10px"}
        return html.Div([
            html.Div([
                html.Div("Période actuelle", style={"fontSize": "0.72rem", "fontWeight": "700", "textTransform": "uppercase", "color": SOLAR_TEXT_MUTED, "letterSpacing": "0.05em"}),
                html.Div(f"{total_ac:,.0f} kW", style={"fontSize": "1.5rem", "fontWeight": "800", "color": SOLAR_ORANGE}),
            ], style={**card_s, "background": "rgba(184,115,51,0.06)"}),
            html.Div([
                html.Div("Période précédente", style={"fontSize": "0.72rem", "fontWeight": "700", "textTransform": "uppercase", "color": SOLAR_TEXT_MUTED, "letterSpacing": "0.05em"}),
                html.Div(f"{ac_prev:,.0f} kW", style={"fontSize": "1.5rem", "fontWeight": "800", "color": SOLAR_TEXT}),
            ], style={**card_s, "background": "rgba(107,91,79,0.05)"}),
            html.Div([
                html.Span(f"{var_i} {var:+.1f} %", style={"fontSize": "1.3rem", "fontWeight": "800", "color": var_c}),
                html.Span("  vs période précédente", style={"fontSize": "0.78rem", "color": SOLAR_TEXT_MUTED, "marginLeft": "8px"}),
            ], style={"padding": "10px 18px"}),
        ])

    # —— Heatmap (utilisé en Page 3 Environnement) ——
    @app.callback(
        Output('heatmap-irradiation-production', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_heatmap(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        pivot = fd.pivot_table(index=fd['Date'].dt.date, columns='Hour', values='AC_Power', aggfunc='mean')
        fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale=[[0, "#f8f5f0"], [0.25, "#bae6fd"], [0.5, "#ca8a04"], [0.75, "#d97706"], [1, "#ea580c"]], hovertemplate='%{y}<br>%{x}h<br><b>%{z:.0f} kW</b><extra></extra>', colorbar=dict(title="kW", thickness=12, len=0.7, outlinewidth=0)))
        fig.update_layout(**_graph_layout(), height=420, autosize=False, xaxis_title="Heure", yaxis_title="Date", xaxis={**_XAXIS, "dtick": 1}, yaxis=_YAXIS)
        return fig

    # —— Température module vs production + tendance + corrélation r ——
    @app.callback(
        [Output('env-correlation-r', 'children'), Output('temp-vs-production-graph', 'figure')],
        Input('applied-filters', 'data'),
    )
    def update_temp(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Module_Temperature' not in fd.columns:
            return html.P("Données Module_Temperature absentes.", className="text-muted"), go.Figure().add_annotation(text="Données absentes", x=0.5, y=0.5, showarrow=False).update_layout(**_graph_layout(), height=420, autosize=False)
        x, y = fd['Module_Temperature'].values, fd['AC_Power'].values
        r = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
        r = np.nan_to_num(r, nan=0)
        # Tendance linéaire
        z = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = np.polyval(z, x_line)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fd['Module_Temperature'], y=fd['AC_Power'], mode='markers', name='Données', marker=dict(size=4, color=fd['AC_Power'], colorscale='YlOrRd', opacity=0.5, line=dict(width=0)), hovertemplate='T°: %{x:.1f} °C<br>AC: %{y:.0f} kW<extra></extra>'))
        fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines', name='Tendance', line=dict(color=GRAPH_AMBER, width=2.5, dash='dash')))
        fig.update_layout(**_graph_layout(), height=380, autosize=False, xaxis_title="Température module (°C)", yaxis_title="Production AC (kW)", xaxis=_XAXIS, yaxis=_YAXIS)
        r_color = SOLAR_SUCCESS if abs(r) > 0.5 else (SOLAR_AMBER if abs(r) > 0.3 else SOLAR_WARN)
        badge = html.Span(f"r = {r:.3f}", style={"background": f"rgba({int(r_color[1:3],16)},{int(r_color[3:5],16)},{int(r_color[5:7],16)},0.1)", "color": r_color, "fontWeight": "800", "padding": "4px 12px", "borderRadius": "6px", "fontSize": "0.85rem"})
        return html.Div(["Corrélation Pearson : ", badge], className="mb-2", style={"fontSize": "0.82rem", "color": SOLAR_TEXT_MUTED}), fig

    # —— Température ambiante vs Efficacité + zone optimale ——
    @app.callback(
        Output('env-ambient-vs-efficiency-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_ambient_vs_efficiency(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Ambient_Temperature' not in fd.columns or 'Efficiency' not in fd.columns:
            return go.Figure().add_annotation(text="Données absentes", x=0.5, y=0.5, showarrow=False).update_layout(**_graph_layout(), height=400, autosize=False)
        fig = go.Figure(go.Scatter(x=fd['Ambient_Temperature'], y=fd['Efficiency'], mode='markers', marker=dict(size=4, color=fd['Efficiency'], colorscale='YlGn', opacity=0.5, line=dict(width=0)), hovertemplate='T° amb.: %{x:.1f} °C<br>Eff: %{y:.1f}%<extra></extra>'))
        fig.add_hrect(y0=85, y1=100, line_width=0, fillcolor="rgba(45,106,79,0.08)", annotation_text="Zone optimale", annotation_font_size=10, annotation_font_color=SOLAR_SUCCESS)
        fig.update_layout(**_graph_layout(), height=380, autosize=False, xaxis_title="Température ambiante (°C)", yaxis_title="Efficiency (%)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— Production par plage de température ——
    @app.callback(
        Output('env-temp-bands-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_temp_bands(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Module_Temperature' not in fd.columns:
            return go.Figure().update_layout(**_graph_layout(), height=400, autosize=False)
        fd = fd.copy()
        fd['Plage'] = pd.cut(fd['Module_Temperature'], bins=[-np.inf, 20, 30, 40, np.inf], labels=['< 20°C', '20–30°C', '30–40°C', '> 40°C'])
        by_band = fd.groupby('Plage', observed=True)['AC_Power'].sum().reset_index()
        band_colors = [GRAPH_TERTIARY, GRAPH_AMBER, GRAPH_PRIMARY, SOLAR_WARN]
        fig = go.Figure(go.Bar(x=by_band['Plage'], y=by_band['AC_Power'], marker_color=band_colors, marker_line_width=0, text=by_band['AC_Power'].apply(lambda v: f"{v:,.0f}"), textposition='outside', textfont=dict(size=11, color=SOLAR_TEXT)))
        fig.update_layout(**_graph_layout(), height=380, autosize=False, xaxis_title="Plage de température", yaxis_title="Production AC (kW)", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    # —— Irradiation vs Production + corrélation ——
    @app.callback(
        [Output('env-irradiation-corr', 'children'), Output('env-irradiation-graph', 'figure')],
        Input('applied-filters', 'data'),
    )
    def update_irradiation(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Irradiation' not in fd.columns:
            return html.P("Colonne Irradiation non disponible.", className="text-muted"), go.Figure().add_annotation(text="Irradiation non disponible", x=0.5, y=0.5, showarrow=False).update_layout(**_graph_layout(), height=400, autosize=False)
        x, y = fd['Irradiation'].values, fd['AC_Power'].values
        r = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
        r = np.nan_to_num(r, nan=0)
        fig = go.Figure(go.Scatter(x=fd['Irradiation'], y=fd['AC_Power'], mode='markers', marker=dict(size=4, color=fd['AC_Power'], colorscale='YlOrRd', opacity=0.5, line=dict(width=0)), hovertemplate='Irrad: %{x:.3f}<br>AC: %{y:.0f} kW<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=380, autosize=False, xaxis_title="Irradiation", yaxis_title="Production AC (kW)", xaxis=_XAXIS, yaxis=_YAXIS)
        r_c = SOLAR_SUCCESS if abs(r) > 0.5 else SOLAR_AMBER
        badge = html.Span(f"r = {r:.3f}", style={"background": f"rgba({int(r_c[1:3],16)},{int(r_c[3:5],16)},{int(r_c[5:7],16)},0.1)", "color": r_c, "fontWeight": "800", "padding": "4px 12px", "borderRadius": "6px", "fontSize": "0.85rem"})
        return html.Div(["Corrélation Irradiation / Production : ", badge], className="mb-2", style={"fontSize": "0.82rem", "color": SOLAR_TEXT_MUTED}), fig

    # —— Pattern horaire moyen ——
    @app.callback(
        Output('avg-hourly-pattern-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_avg_hourly(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        hourly = fd.groupby('Hour').agg({'AC_Power': 'mean', 'DC_Power': 'mean'}).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hourly['Hour'], y=hourly['AC_Power'], mode='lines+markers', name='AC moy.', line=dict(color=GRAPH_PRIMARY, width=2.5, shape='spline'), marker=dict(size=6, color=GRAPH_PRIMARY, line=dict(width=2, color='white')), fill='tozeroy', fillcolor='rgba(234,88,12,0.08)'))
        fig.add_trace(go.Scatter(x=hourly['Hour'], y=hourly['DC_Power'], mode='lines+markers', name='DC moy.', line=dict(color=GRAPH_SECONDARY, width=2, shape='spline', dash='dot'), marker=dict(size=5, color=GRAPH_SECONDARY)))
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Heure", yaxis_title="Production moy. (kW)", xaxis={**_XAXIS, "tickmode": "linear", "dtick": 2, "range": [-0.5, 23.5]}, yaxis=_YAXIS)
        return fig

    # —— PAGE 4 — Anomalies : KPI ——
    @app.callback(
        [Output('anom-pct-nulle', 'children'), Output('anom-nb-incidents', 'children'), Output('anom-duree-moy', 'children'), Output('anom-max-panne', 'children')],
        Input('applied-filters', 'data'),
    )
    def update_anom_kpi(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        fd = fd.copy()
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        journee = fd[(fd['Hour'] >= 8) & (fd['Hour'] <= 18)]
        total_j = len(journee)
        nulle_j = (journee['AC_Power'] == 0).sum()
        pct_nulle = (100.0 * nulle_j / total_j) if total_j else 0
        # Incidents = séquences consécutives de prod nulle en journée
        j = journee.sort_values('DateTime').copy()
        j['zero'] = (j['AC_Power'] == 0).astype(int)
        j['grp'] = (j['zero'].diff().fillna(1) != 0).cumsum()
        incidents = j[j['zero'] == 1].groupby('grp').size()
        nb_incidents = len(incidents)
        # Durée en pas horaires (approx) : on suppose pas = 1h
        duree_moy = float(incidents.mean()) if len(incidents) else 0
        duree_max = float(incidents.max()) if len(incidents) else 0
        return f"{pct_nulle:.1f} %", str(nb_incidents), f"{duree_moy:.1f}", f"{duree_max:.0f}"

    # —— PAGE 4 — Production nulle en journée (8h–18h) ——
    @app.callback(
        Output('anom-nulle-journee-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_anom_nulle_journee(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        fd = fd.copy()
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        journee = fd[(fd['Hour'] >= 8) & (fd['Hour'] <= 18)]
        fig = go.Figure()
        normal = journee[journee['AC_Power'] > 0]
        anom = journee[journee['AC_Power'] == 0]
        fig.add_trace(go.Scatter(x=normal['DateTime'], y=normal['AC_Power'], mode='markers', name='Normale', marker=dict(size=3, color=GRAPH_SECONDARY, opacity=0.4), hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=anom['DateTime'], y=anom['AC_Power'], mode='markers', name='Anomalie', marker=dict(size=8, color=SOLAR_WARN, symbol='x', line=dict(width=2, color=SOLAR_WARN))))
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Date et heure", yaxis_title="AC (kW)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— PAGE 4 — Efficacité < 80 % ——
    @app.callback(
        Output('anom-efficiency-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_anom_efficiency(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        if 'Efficiency' not in fd.columns:
            fig = go.Figure()
            fig.add_annotation(text="Efficiency non disponible", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(**_graph_layout(), height=400)
            return fig
        ok = fd[fd['Efficiency'] >= 80]
        anom = fd[fd['Efficiency'] < 80]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ok['DateTime'], y=ok['Efficiency'], mode='lines', name='≥ 80 %', line=dict(color=GRAPH_TERTIARY, width=1.5, shape='spline')))
        fig.add_trace(go.Scatter(x=anom['DateTime'], y=anom['Efficiency'], mode='markers', name='< 80 %', marker=dict(size=6, color=SOLAR_WARN, symbol='circle', line=dict(width=1, color='white'))))
        fig.add_hline(y=80, line_dash="dot", line_color="rgba(230,57,70,0.5)", annotation_text="80 %", annotation_font_size=10, annotation_font_color=SOLAR_WARN)
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Date et heure", yaxis_title="Efficiency (%)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— PAGE 4 — Tableau incidents ——
    @app.callback(
        Output('anom-table-incidents', 'children'),
        Input('applied-filters', 'data'),
    )
    def update_anom_table(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        fd = fd.copy()
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        journee = fd[(fd['Hour'] >= 8) & (fd['Hour'] <= 18)]
        incidents = journee[journee['AC_Power'] == 0].copy()
        if len(incidents) == 0:
            return html.P("Aucun incident (production nulle 8h–18h) sur la période.", className="text-muted")
        incidents['Type anomalie'] = 'Production nulle en journée'
        if 'Efficiency' in incidents.columns:
            incidents.loc[incidents['Efficiency'] < 80, 'Type anomalie'] = 'Production nulle + efficacité basse'
        cols = ['Date', 'DateTime', 'AC_Power', 'DC_Power', 'Efficiency', 'Type anomalie'] if 'Efficiency' in incidents.columns else ['Date', 'DateTime', 'AC_Power', 'DC_Power', 'Type anomalie']
        cols = [c for c in cols if c in incidents.columns]
        df = incidents[cols].head(500)
        df['Date'] = df['Date'].astype(str)
        df['DateTime'] = df['DateTime'].astype(str)
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=12,
            style_table={"overflowX": "auto", "borderRadius": "10px"},
            style_cell={"textAlign": "left", "padding": "10px 14px", "fontFamily": "Segoe UI, system-ui", "fontSize": "0.82rem", "border": "none", "borderBottom": "1px solid #eedfc8"},
            style_header={"fontWeight": "700", "backgroundColor": "#fff8e1", "color": SOLAR_TEXT, "borderBottom": "2px solid " + SOLAR_ORANGE, "fontSize": "0.78rem", "textTransform": "uppercase", "letterSpacing": "0.04em"},
            style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "rgba(253,246,236,0.4)"}],
        )

    # —— PAGE 4 — Anomalies par mois ——
    @app.callback(
        Output('anom-by-month-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_anom_by_month(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        fd = fd.copy()
        fd['Hour'] = pd.to_numeric(fd.get('Hour', fd.get('Time', 0)), errors='coerce')
        journee = fd[(fd['Hour'] >= 8) & (fd['Hour'] <= 18)]
        nulle = journee[journee['AC_Power'] == 0]
        nulle['Month'] = nulle['Date'].dt.to_period('M').astype(str)
        by_month = nulle.groupby('Month').size().reset_index(name='Nb anomalies')
        fig = go.Figure(go.Bar(x=by_month['Month'], y=by_month['Nb anomalies'], marker_color='rgba(230,57,70,0.7)', marker_line_width=0, text=by_month['Nb anomalies'], textposition='outside', textfont=dict(size=11, color=SOLAR_WARN), hovertemplate='%{x}<br><b>%{y}</b> anomalies<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Mois", yaxis_title="Nb anomalies", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.25)
        return fig

    # —— PAGE 5 — Prévision (moyenne mobile + projection 30j) ——
    @app.callback(
        Output('adv-forecast-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_adv_forecast(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        daily = fd.groupby('Date')['AC_Power'].sum().reset_index()
        daily = daily.rename(columns={'AC_Power': 'Daily_AC'}).sort_values('Date')
        daily['Date'] = pd.to_datetime(daily['Date']).dt.tz_localize(None)
        if len(daily) < 2:
            fig = go.Figure()
            fig.add_annotation(text="Données insuffisantes pour la prévision (min. 2 jours)", x=0.5, y=0.5, showarrow=False, font=dict(size=14))
            fig.update_layout(**_graph_layout(), height=420, xaxis=dict(visible=True), yaxis=dict(visible=True))
            return fig
        daily['MA7'] = daily['Daily_AC'].rolling(7, min_periods=1).mean()
        last = pd.Timestamp(daily['Date'].max())
        if pd.isna(last):
            last = pd.Timestamp.now()
        future = pd.date_range(start=last + timedelta(days=1), periods=30, freq='D')
        x = np.arange(len(daily.tail(30)))
        y = daily.tail(30)['MA7'].values.astype(float)
        if len(x) > 1 and np.all(np.isfinite(y)):
            coef = np.polyfit(x, y, 1)
            proj = np.polyval(coef, np.arange(30))
        else:
            proj = np.full(30, float(daily['MA7'].iloc[-1]) if np.isfinite(daily['MA7'].iloc[-1]) else 0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['Date'], y=daily['Daily_AC'].astype(float), mode='lines', name='Production', line=dict(color='rgba(14,165,233,0.35)', width=1), hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=daily['Date'], y=daily['MA7'].astype(float), mode='lines', name='MA 7j', line=dict(color=GRAPH_PRIMARY, width=2.5, shape='spline'), fill='tozeroy', fillcolor='rgba(234,88,12,0.06)'))
        fig.add_trace(go.Scatter(x=future, y=proj, mode='lines', name='Projection 30j', line=dict(color=GRAPH_AMBER, width=2.5, dash='dash')))
        fig.update_layout(
            **_graph_layout(),
            height=420,
            hovermode='x unified',
            xaxis_title="Date",
            yaxis_title="Production AC (kW)",
            xaxis={**_XAXIS, "type": "date"},
            yaxis=_YAXIS,
        )
        return fig

    # —— PAGE 5 — Outliers IQR ——
    @app.callback(
        Output('adv-outliers-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_adv_outliers(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        if 'Efficiency' not in fd.columns:
            fig = go.Figure()
            fig.add_annotation(text="Efficiency non disponible", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(**_graph_layout(), height=400)
            return fig
        eff = fd['Efficiency'].dropna()
        q1, q3 = eff.quantile(0.25), eff.quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        fd = fd.copy()
        fd['Outlier'] = (fd['Efficiency'] < lo) | (fd['Efficiency'] > hi)
        normal = fd[~fd['Outlier']]
        outliers = fd[fd['Outlier']]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=normal['DateTime'], y=normal['Efficiency'], mode='markers', name='Normal', marker=dict(size=3, color=GRAPH_TERTIARY, opacity=0.35), hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=outliers['DateTime'], y=outliers['Efficiency'], mode='markers', name='Outlier (IQR)', marker=dict(size=7, color=SOLAR_WARN, symbol='diamond', line=dict(width=1, color='white'))))
        fig.update_layout(**_graph_layout(), height=380, xaxis_title="Date et heure", yaxis_title="Efficiency (%)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    # —— PAGE 5 — Décomposition (trend = MA, résidu, saisonnalité par heure) ——
    @app.callback(
        Output('adv-decomposition-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_adv_decomposition(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site')).sort_values('DateTime')
        if len(fd) < 24:
            fig = go.Figure()
            fig.add_annotation(text="Données insuffisantes", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(**_graph_layout(), height=500)
            return fig
        # Série horaire AC
        fd_indexed = fd.set_index('DateTime')
        daily_avg = fd_indexed['AC_Power'].resample('D').mean()
        trend = daily_avg.rolling(7, min_periods=1, center=True).mean().bfill().ffill()
        fd = fd.copy()
        hourly_by_hour = fd.groupby(fd['DateTime'].dt.hour)['AC_Power'].mean()
        seasonal_pattern = hourly_by_hour.reindex(fd['DateTime'].dt.hour).values
        trend_vals = np.interp(fd['DateTime'].astype(np.int64) // 10**9, daily_avg.index.astype(np.int64) // 10**9, trend.values.astype(float))
        residual = fd['AC_Power'].values - trend_vals - np.nan_to_num(seasonal_pattern, nan=0)
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=3, cols=1, subplot_titles=("Tendance (MA 7j)", "Saisonnalité (moyenne par heure)", "Résidu"), shared_xaxes=True, vertical_spacing=0.08)
        fig.add_trace(go.Scatter(x=fd['DateTime'], y=trend_vals, mode='lines', name='Tendance', line=dict(color=GRAPH_PRIMARY, width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=fd['DateTime'], y=seasonal_pattern, mode='lines', name='Saisonnalité', line=dict(color=GRAPH_AMBER, width=1.5)), row=2, col=1)
        fig.add_trace(go.Scatter(x=fd['DateTime'], y=residual, mode='lines', name='Résidu', line=dict(color=GRAPH_SECONDARY, width=1, dash='dot')), row=3, col=1)
        fig.update_layout(height=500, showlegend=True, template='plotly_white', margin=dict(t=50, b=30, l=50, r=25), font=dict(family="Segoe UI, system-ui, sans-serif", size=11, color=SOLAR_TEXT), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(253,246,236,0.3)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)))
        fig.update_xaxes(**_XAXIS)
        fig.update_yaxes(**_YAXIS)
        return fig

    # —— PAGE 5 — Performance annuelle ——
    @app.callback(
        Output('adv-annual-graph', 'figure'),
        Input('applied-filters', 'data'),
    )
    def update_adv_annual(applied_filters):
        applied_filters = applied_filters or applied_default
        fd = _filter_df(applied_filters['start'], applied_filters['end'], applied_filters.get('site'))
        fd['Year'] = fd['Date'].dt.year
        by_year = fd.groupby('Year').agg({'AC_Power': 'sum', 'DC_Power': 'sum'}).reset_index()
        if len(by_year) < 2:
            fig = go.Figure()
            fig.add_annotation(text="Plusieurs années nécessaires pour la comparaison.", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(**_graph_layout(), height=400)
            return fig
        fig = go.Figure()
        fig.add_trace(go.Bar(x=by_year['Year'].astype(str), y=by_year['AC_Power'], name='AC', marker_color=GRAPH_PRIMARY, marker_line_width=0, text=by_year['AC_Power'].apply(lambda v: f"{v:,.0f}"), textposition='outside', textfont=dict(size=10)))
        fig.add_trace(go.Bar(x=by_year['Year'].astype(str), y=by_year['DC_Power'], name='DC', marker_color=GRAPH_SECONDARY, marker_line_width=0))
        fig.update_layout(**_graph_layout(), height=380, barmode='group', xaxis_title="Année", yaxis_title="Production totale (kW)", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.25)
        return fig

    return app
