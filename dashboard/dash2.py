"""
Dashboard Exercice 5 — Analyse des sinistres et profil des assurés.
Thème assurance : bleu profond / bordeaux / gris élégant.
Données : MongoDB Atlas (flash_dash.assurance) ou CSV en secours.
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

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
try:
    import config_mongo as _cfg
except ImportError:
    _cfg = None

# ══════ Palette assurance ══════
THEME = dbc.themes.FLATLY
INS_PRIMARY = "#1a3a5c"
INS_SECONDARY = "#2c5f8a"
INS_ACCENT = "#c0392b"
INS_GOLD = "#d4a017"
INS_SUCCESS = "#27ae60"
INS_WARN = "#e74c3c"
INS_LIGHT = "#f0f4f8"
INS_CARD = "#ffffff"
INS_BORDER = "#d5dce6"
INS_TEXT = "#1e293b"
INS_TEXT_MUTED = "#64748b"
INS_CREAM = "#f8fafc"

GRAPH_CFG = {"responsive": True, "displayModeBar": False}

_AXIS = dict(gridcolor="rgba(213,220,230,0.5)", gridwidth=1,
             zerolinecolor="rgba(213,220,230,0.6)", zerolinewidth=1,
             showline=True, linewidth=1, linecolor="rgba(213,220,230,0.7)")
_XAXIS = {**_AXIS, "tickfont": dict(size=10, color=INS_TEXT_MUTED)}
_YAXIS = {**_AXIS, "tickfont": dict(size=10, color=INS_TEXT_MUTED)}
GH = 370


def _graph_layout(**kwargs):
    base = dict(
        template="plotly_white",
        font=dict(family="Segoe UI, system-ui, sans-serif", size=12, color=INS_TEXT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,244,248,0.35)",
        margin=dict(t=50, b=45, l=55, r=25),
        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_color=INS_TEXT, bordercolor=INS_PRIMARY),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(255,255,255,0.9)", bordercolor=INS_BORDER, borderwidth=1, font=dict(size=11)),
        uirevision="layout_stable",
    )
    base.update(kwargs)
    return base


COLORS_TYPE = {"Auto": "#1a3a5c", "Santé": "#27ae60", "Habitation": "#d4a017", "Vie": "#8e44ad"}
COLORS_SEQ = ["#1a3a5c", "#2c5f8a", "#c0392b", "#d4a017", "#27ae60", "#8e44ad", "#e67e22", "#16a085"]


def _load_assurance_data():
    df = None
    if _cfg and getattr(_cfg, "MONGO_URI", "").strip() and "mongodb+srv" in getattr(_cfg, "MONGO_URI", ""):
        try:
            from pymongo import MongoClient
            client = MongoClient(_cfg.MONGO_URI, serverSelectionTimeoutMS=500, connectTimeoutMS=500)
            coll = client[_cfg.FLASH_DASH_DB][_cfg.ASSURANCE_COLLECTION]
            docs = list(coll.find({}))
            client.close()
            if docs:
                for d in docs:
                    d.pop("_id", None)
                df = pd.DataFrame(docs)
        except Exception:
            pass
    if df is None or len(df) == 0:
        df = pd.read_csv(os.path.join(_root, "data", "assurance_data_1000.csv"), sep=';')
    return df


def create_dash_app(server, url_base_pathname, requests_pathname_prefix=None):
    if url_base_pathname and not url_base_pathname.startswith("/"):
        url_base_pathname = "/" + url_base_pathname
    df = _load_assurance_data()
    df['date_derniere_sinistre'] = pd.to_datetime(df['date_derniere_sinistre'], errors='coerce')
    df['annee_sinistre'] = df['date_derniere_sinistre'].dt.year
    df['mois_sinistre'] = df['date_derniere_sinistre'].dt.to_period('M').astype(str)
    df['tranche_age'] = pd.cut(df['age'], bins=[18, 25, 35, 45, 55, 65, 100],
                                labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])
    df['ratio_sinistre_prime'] = np.where(df['montant_prime'] > 0,
                                           df['montant_sinistres'] / df['montant_prime'], 0)

    _assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    kwargs = dict(
        server=server,
        external_stylesheets=[THEME],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        assets_folder=_assets_dir,
    )
    if requests_pathname_prefix is not None:
        kwargs["routes_pathname_prefix"] = url_base_pathname
        kwargs["requests_pathname_prefix"] = requests_pathname_prefix
    else:
        kwargs["url_base_pathname"] = url_base_pathname
    app = dash.Dash(__name__, **kwargs)
    app.config.suppress_callback_exceptions = True

    types_assurance = sorted(df['type_assurance'].dropna().unique())
    regions = sorted(df['region'].dropna().unique())
    sexes = sorted(df['sexe'].dropna().unique())

    # ══════ Helper functions ══════
    def _filter_df(type_a, region, sexe):
        out = df.copy()
        if type_a and type_a != 'Tous':
            out = out[out['type_assurance'] == type_a]
        if region and region != 'Toutes':
            out = out[out['region'] == region]
        if sexe and sexe != 'Tous':
            out = out[out['sexe'] == sexe]
        return out

    # ══════ FILTER BAR ══════
    filter_card = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("🔍", style={"fontSize": "1.1rem", "marginRight": "6px"}),
                        html.Span("Filtres", style={"fontWeight": "700", "fontSize": "0.85rem", "color": INS_TEXT}),
                    ], className="d-flex align-items-center mb-2"),
                ], md=1, className="ins-filter-col ins-filter-col-label"),
                dbc.Col([
                    html.Div("📋 Type", className="ins-filter-label"),
                    dcc.Dropdown(id='f-type', options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': t, 'value': t} for t in types_assurance],
                                 value='Tous', clearable=False, className="ins-dropdown"),
                ], md=2, className="ins-filter-col"),
                dbc.Col([
                    html.Div("📍 Région", className="ins-filter-label"),
                    dcc.Dropdown(id='f-region', options=[{'label': 'Toutes', 'value': 'Toutes'}] + [{'label': r, 'value': r} for r in regions],
                                 value='Toutes', clearable=False, className="ins-dropdown"),
                ], md=2, className="ins-filter-col"),
                dbc.Col([
                    html.Div("👤 Sexe", className="ins-filter-label"),
                    dcc.Dropdown(id='f-sexe', options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': s.capitalize(), 'value': s} for s in sexes],
                                 value='Tous', clearable=False, className="ins-dropdown"),
                ], md=2, className="ins-filter-col"),
                dbc.Col([
                    html.Div("📊 Tranche d'âge", className="ins-filter-label"),
                    dcc.Dropdown(id='f-age', options=[{'label': 'Toutes', 'value': 'Toutes'}] + [{'label': str(t), 'value': str(t)} for t in df['tranche_age'].dropna().unique()],
                                 value='Toutes', clearable=False, className="ins-dropdown"),
                ], md=5, className="ins-filter-col"),
            ], className="ins-filter-row"),
        ], className="ins-filter-body"),
    ], className="ins-filter-bar mb-4")

    # ══════ KPIs — jolies blocs : fond blanc, bordure gauche épaisse arrondie, ombre ─════
    def kpi(icon, label, kid, color):
        return dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([html.Span(icon, style={"fontSize": "1.35rem", "marginRight": "8px"}), html.Span(label, className="ins-kpi-label")], className="d-flex align-items-center mb-1"),
                html.H3(id=kid, className="ins-kpi-value mb-0", style={"color": color}),
            ], style={"padding": "1rem 1.15rem"}),
        ], className="ins-kpi-card h-100", style={"borderLeft": f"6px solid {color}", "background": "#ffffff"}), lg=2, md=4, sm=6, className="mb-3")

    kpi_row = dbc.Row([
        kpi("👥", "Assurés", 'k-assures', INS_PRIMARY),
        kpi("⚠️", "Sinistres", 'k-sinistres', INS_ACCENT),
        kpi("💰", "Montant total", 'k-montant', INS_WARN),
        kpi("📊", "Moy. / sinistre", 'k-moy', INS_GOLD),
        kpi("💵", "Prime moyenne", 'k-prime', INS_SUCCESS),
        kpi("📈", "Ratio S/P", 'k-ratio', INS_SECONDARY),
    ], className="g-3 mb-4")

    # ══════ Graph card helpers ══════
    def gcard(title, gid, full=False):
        return dbc.Col(dbc.Card([
            dbc.CardHeader(title, className="ins-card-title"),
            dbc.CardBody(dcc.Graph(id=gid, config=GRAPH_CFG), className="p-2"),
        ], className="ins-content-card h-100"), md=12 if full else 6, className="mb-4")

    def gcard_custom(title, children, full=False):
        return dbc.Col(dbc.Card([
            dbc.CardHeader(title, className="ins-card-title"),
            dbc.CardBody(children, className="p-3"),
        ], className="ins-content-card h-100"), md=12 if full else 6, className="mb-4")

    def ptitle(icon, title, subtitle):
        return html.Div([
            html.Div([html.Span(icon, style={"fontSize": "1.4rem", "marginRight": "8px"}),
                       html.Span(title, style={"fontSize": "1.15rem", "fontWeight": "800", "color": INS_TEXT})], className="d-flex align-items-center"),
            html.Div(subtitle, style={"fontSize": "0.8rem", "color": INS_TEXT_MUTED, "marginTop": "2px", "marginLeft": "2rem"}),
        ], className="mb-3 pb-2", style={"borderBottom": f"2px solid {INS_PRIMARY}"})

    # ═══════════ PAGE 1 — VUE D'ENSEMBLE ═══════════
    page_overview = html.Div([
        ptitle("🏠", "Vue d'ensemble", "Synthèse des sinistres et du portefeuille"),
        dbc.Row([
            gcard("Sinistres par type d'assurance", 'g-sinistres-type'),
            gcard("Sinistres par région", 'g-sinistres-region'),
        ]),
        dbc.Row([
            gcard("Évolution des sinistres dans le temps", 'g-evolution-temps'),
            gcard("Répartition Homme / Femme", 'g-repartition-sexe'),
        ]),
    ], id="page2-overview")

    # ═══════════ PAGE 2 — PROFIL DES ASSURÉS ═══════════
    page_profil = html.Div([
        ptitle("👤", "Profil des Assurés", "Caractéristiques démographiques et contractuelles"),
        dbc.Row([
            gcard("Distribution par âge", 'g-dist-age'),
            gcard("Prime moyenne par tranche d'âge", 'g-prime-age'),
        ]),
        dbc.Row([
            gcard("Durée de contrat par type", 'g-duree-type'),
            gcard("Répartition par type d'assurance", 'g-repartition-type'),
        ]),
    ], id="page2-profil", style={"display": "none"})

    # ═══════════ PAGE 3 — ANALYSE FINANCIÈRE ═══════════
    page_finance = html.Div([
        ptitle("💰", "Analyse Financière", "Primes, sinistres et rentabilité"),
        dbc.Row([
            gcard("Montant des sinistres par type", 'g-montant-type'),
            gcard("Ratio Sinistres / Primes par type", 'g-ratio-type'),
        ]),
        dbc.Row([
            gcard("Prime vs Montant sinistres (scatter)", 'g-prime-vs-sinistre'),
            gcard("Distribution des montants de sinistres", 'g-dist-montant'),
        ]),
    ], id="page2-finance", style={"display": "none"})

    # ═══════════ PAGE 4 — PROFILS À RISQUE ═══════════
    page_risque = html.Div([
        ptitle("⚠️", "Profils à Risque", "Identification et segmentation des assurés à risque"),
        dbc.Row([
            gcard("Âge vs Montant sinistres", 'g-age-montant'),
            gcard("Bonus/Malus par tranche d'âge", 'g-bonus-age'),
        ]),
        dbc.Row([
            gcard("Nb sinistres par type et sexe", 'g-sinistres-type-sexe'),
            gcard("Top 10 régions par sinistralité", 'g-top-regions'),
        ]),
        dbc.Row([
            gcard_custom("Tableau des assurés à haut risque", html.Div(id='g-table-risque'), full=True),
        ]),
    ], id="page2-risque", style={"display": "none"})

    # ═══════════ PAGE 5 — BONUS / MALUS ═══════════
    page_bonus = html.Div([
        ptitle("📈", "Analyse Bonus / Malus", "Coefficient et impact sur la sinistralité"),
        dbc.Row([
            gcard("Distribution du coefficient B/M", 'g-dist-bm'),
            gcard("Bonus/Malus vs Nb sinistres", 'g-bm-sinistres'),
        ]),
        dbc.Row([
            gcard("Bonus/Malus moyen par région", 'g-bm-region'),
            gcard("Bonus/Malus moyen par type d'assurance", 'g-bm-type'),
        ]),
    ], id="page2-bonus", style={"display": "none"})

    pages = html.Div([page_overview, page_profil, page_finance, page_risque, page_bonus], id="pages2-container")

    # ══════ HEADER ══════
    header = dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div("🛡️", style={"fontSize": "2.2rem", "lineHeight": "1"}), width="auto"),
                dbc.Col([
                    html.Div("Analyse des Sinistres & Profil des Assurés", style={"fontWeight": "800", "fontSize": "1.25rem", "letterSpacing": "0.01em"}),
                    html.Div("Dashboard interactif — Compagnie d'assurance", style={"fontSize": "0.82rem", "opacity": "0.75", "marginTop": "2px"}),
                ], width="auto"),
                dbc.Col([
                    dbc.Button(["📄 PDF"], id="btn-pdf2", size="sm", className="ins-btn-pdf"),
                ], width="auto", className="ms-auto d-flex align-items-center"),
            ], className="g-3 align-items-center", style={"width": "100%"}),
        ], fluid=True),
        color="dark", dark=True, className="mb-4 ins-navbar", style={"padding": "0.9rem 0"},
    )

    # ══════ SIDEBAR ══════
    sidebar = html.Div([
        html.Div("NAVIGATION", style={"fontSize": "0.65rem", "fontWeight": "700", "letterSpacing": "0.1em", "color": INS_TEXT_MUTED, "padding": "0.4rem 0.8rem 0.5rem", "textTransform": "uppercase"}),
        dbc.Button("🏠  Vue d'ensemble", id="n2-overview", n_clicks=0, className="ins-sidebar-btn ins-sidebar-btn-active", color="link"),
        dbc.Button("👤  Profil assurés", id="n2-profil", n_clicks=0, className="ins-sidebar-btn", color="link"),
        dbc.Button("💰  Analyse financière", id="n2-finance", n_clicks=0, className="ins-sidebar-btn", color="link"),
        dbc.Button("⚠️  Profils à risque", id="n2-risque", n_clicks=0, className="ins-sidebar-btn", color="link"),
        dbc.Button("📈  Bonus / Malus", id="n2-bonus", n_clicks=0, className="ins-sidebar-btn", color="link"),
    ], className="ins-sidebar-nav mb-4")

    # ══════ LAYOUT ══════
    app.layout = dbc.Container([
        header,
        html.Div(id="pdf-trigger2", style={"display": "none"}),
        filter_card,
        kpi_row,
        dbc.Row([
            dbc.Col(sidebar, md=2, className="ins-sidebar-col"),
            dbc.Col(pages, md=10),
        ]),
    ], fluid=True, className="py-4", style={"backgroundColor": INS_CREAM, "minHeight": "100vh", "fontFamily": "Segoe UI, system-ui, sans-serif"})

    # ══════════════════════════════════════════════════════════
    #  CALLBACKS
    # ══════════════════════════════════════════════════════════

    INPUTS = [Input('f-type', 'value'), Input('f-region', 'value'), Input('f-sexe', 'value'), Input('f-age', 'value')]

    def _fd(type_a, region, sexe, age=None):
        out = _filter_df(type_a, region, sexe)
        if age and age != 'Toutes':
            out = out[out['tranche_age'].astype(str) == age]
        return out

    # — Navigation sidebar —
    @app.callback(
        [Output('page2-overview', 'style'), Output('page2-profil', 'style'),
         Output('page2-finance', 'style'), Output('page2-risque', 'style'),
         Output('page2-bonus', 'style'),
         Output('n2-overview', 'className'), Output('n2-profil', 'className'),
         Output('n2-finance', 'className'), Output('n2-risque', 'className'),
         Output('n2-bonus', 'className')],
        [Input('n2-overview', 'n_clicks'), Input('n2-profil', 'n_clicks'),
         Input('n2-finance', 'n_clicks'), Input('n2-risque', 'n_clicks'),
         Input('n2-bonus', 'n_clicks')],
    )
    def switch_page(n1, n2, n3, n4, n5):
        from dash import ctx
        nav_map = {'n2-overview': 0, 'n2-profil': 1, 'n2-finance': 2, 'n2-risque': 3, 'n2-bonus': 4}
        idx = nav_map.get(ctx.triggered_id, 0)
        show, hide = {"display": "block"}, {"display": "none"}
        styles = [show if i == idx else hide for i in range(5)]
        base, active = "ins-sidebar-btn", "ins-sidebar-btn ins-sidebar-btn-active"
        classes = [active if i == idx else base for i in range(5)]
        return *styles, *classes

    # — Export PDF —
    app.clientside_callback("function(n){if(n)window.print();return null;}", Output('pdf-trigger2', 'children'), Input('btn-pdf2', 'n_clicks'))

    # — KPIs —
    @app.callback(
        [Output('k-assures', 'children'), Output('k-sinistres', 'children'),
         Output('k-montant', 'children'), Output('k-moy', 'children'),
         Output('k-prime', 'children'), Output('k-ratio', 'children')],
        INPUTS)
    def update_kpis(t, r, s, a):
        fd = _fd(t, r, s, a)
        n_assures = len(fd)
        tot_sin = fd['nb_sinistres'].sum()
        tot_mt = fd['montant_sinistres'].sum()
        moy = fd.loc[fd['nb_sinistres'] > 0, 'montant_sinistres'].mean() if (fd['nb_sinistres'] > 0).any() else 0
        prime_moy = fd['montant_prime'].mean()
        tot_primes = fd['montant_prime'].sum()
        ratio = (tot_mt / tot_primes * 100) if tot_primes > 0 else 0
        return (f"{n_assures:,}", f"{tot_sin:,}", f"{tot_mt:,.0f} €",
                f"{moy:,.0f} €", f"{prime_moy:,.0f} €", f"{ratio:.1f} %")

    # ═══════════ PAGE 1 callbacks ═══════════

    @app.callback(Output('g-sinistres-type', 'figure'), INPUTS)
    def cb_sin_type(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('type_assurance').agg(nb=('nb_sinistres', 'sum'), mt=('montant_sinistres', 'sum')).reset_index()
        colors = [COLORS_TYPE.get(x, INS_PRIMARY) for x in grp['type_assurance']]
        fig = go.Figure(go.Bar(x=grp['type_assurance'], y=grp['nb'], marker_color=colors, marker_line_width=0,
                                text=grp['nb'], textposition='outside', textfont=dict(size=11, color=INS_TEXT),
                                hovertemplate='%{x}<br><b>%{y}</b> sinistres<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Type", yaxis_title="Nb sinistres", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    @app.callback(Output('g-sinistres-region', 'figure'), INPUTS)
    def cb_sin_region(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('region')['nb_sinistres'].sum().reset_index().sort_values('nb_sinistres', ascending=True)
        fig = go.Figure(go.Bar(y=grp['region'], x=grp['nb_sinistres'], orientation='h',
                                marker_color=INS_SECONDARY, marker_line_width=0,
                                text=grp['nb_sinistres'], textposition='outside', textfont=dict(size=10),
                                hovertemplate='%{y}<br><b>%{x}</b> sinistres<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Nb sinistres", yaxis_title="", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.25)
        return fig

    @app.callback(Output('g-evolution-temps', 'figure'), INPUTS)
    def cb_evolution(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('mois_sinistre').agg(nb=('nb_sinistres', 'sum'), mt=('montant_sinistres', 'sum')).reset_index().sort_values('mois_sinistre')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=grp['mois_sinistre'], y=grp['nb'], mode='lines+markers', name='Nb sinistres',
                                  line=dict(color=INS_PRIMARY, width=2.5, shape='spline'),
                                  marker=dict(size=6, color=INS_PRIMARY, line=dict(width=2, color='white')),
                                  fill='tozeroy', fillcolor='rgba(26,58,92,0.06)'))
        fig.update_layout(**_graph_layout(), height=GH, hovermode='x unified', xaxis_title="Mois", yaxis_title="Nb sinistres", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    @app.callback(Output('g-repartition-sexe', 'figure'), INPUTS)
    def cb_sexe(t, r, s, a):
        fd = _fd(t, r, s, a)
        rep = fd['sexe'].value_counts()
        fig = go.Figure(go.Pie(labels=rep.index.str.capitalize(), values=rep.values, hole=0.55,
                                marker=dict(colors=[INS_PRIMARY, INS_ACCENT], line=dict(color='white', width=3)),
                                textinfo='label+percent', textfont=dict(size=12),
                                hovertemplate='%{label}<br><b>%{value}</b> (%{percent})<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=GH, showlegend=False)
        return fig

    # ═══════════ PAGE 2 callbacks ═══════════

    @app.callback(Output('g-dist-age', 'figure'), INPUTS)
    def cb_dist_age(t, r, s, a):
        fd = _fd(t, r, s, a)
        fig = go.Figure(go.Histogram(x=fd['age'], nbinsx=25, marker_color='rgba(26,58,92,0.65)',
                                      marker_line_color=INS_PRIMARY, marker_line_width=0.5))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Âge", yaxis_title="Effectif", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.05)
        return fig

    @app.callback(Output('g-prime-age', 'figure'), INPUTS)
    def cb_prime_age(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('tranche_age', observed=True)['montant_prime'].mean().reset_index()
        fig = go.Figure(go.Bar(x=grp['tranche_age'].astype(str), y=grp['montant_prime'],
                                marker_color=INS_GOLD, marker_line_width=0,
                                text=grp['montant_prime'].apply(lambda v: f"{v:.0f} €"), textposition='outside', textfont=dict(size=10)))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Tranche d'âge", yaxis_title="Prime moy. (€)", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    @app.callback(Output('g-duree-type', 'figure'), INPUTS)
    def cb_duree_type(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('type_assurance')['duree_contrat'].mean().reset_index()
        colors = [COLORS_TYPE.get(x, INS_PRIMARY) for x in grp['type_assurance']]
        fig = go.Figure(go.Bar(x=grp['type_assurance'], y=grp['duree_contrat'], marker_color=colors, marker_line_width=0,
                                text=grp['duree_contrat'].apply(lambda v: f"{v:.1f} ans"), textposition='outside', textfont=dict(size=10)))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Type", yaxis_title="Durée moy. (ans)", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    @app.callback(Output('g-repartition-type', 'figure'), INPUTS)
    def cb_rep_type(t, r, s, a):
        fd = _fd(t, r, s, a)
        rep = fd['type_assurance'].value_counts()
        fig = go.Figure(go.Pie(labels=rep.index, values=rep.values, hole=0.55,
                                marker=dict(colors=[COLORS_TYPE.get(x, INS_PRIMARY) for x in rep.index],
                                            line=dict(color='white', width=3)),
                                textinfo='label+percent', textfont=dict(size=11)))
        fig.update_layout(**_graph_layout(), height=GH, showlegend=False)
        return fig

    # ═══════════ PAGE 3 callbacks ═══════════

    @app.callback(Output('g-montant-type', 'figure'), INPUTS)
    def cb_mt_type(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('type_assurance')['montant_sinistres'].sum().reset_index().sort_values('montant_sinistres', ascending=False)
        colors = [COLORS_TYPE.get(x, INS_PRIMARY) for x in grp['type_assurance']]
        fig = go.Figure(go.Bar(x=grp['type_assurance'], y=grp['montant_sinistres'], marker_color=colors, marker_line_width=0,
                                text=grp['montant_sinistres'].apply(lambda v: f"{v:,.0f} €"), textposition='outside', textfont=dict(size=10)))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Type", yaxis_title="Montant total (€)", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    @app.callback(Output('g-ratio-type', 'figure'), INPUTS)
    def cb_ratio_type(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('type_assurance').agg(primes=('montant_prime', 'sum'), sinistres=('montant_sinistres', 'sum')).reset_index()
        grp['ratio'] = np.where(grp['primes'] > 0, grp['sinistres'] / grp['primes'] * 100, 0)
        colors = [INS_WARN if v > 100 else INS_SUCCESS for v in grp['ratio']]
        fig = go.Figure(go.Bar(x=grp['type_assurance'], y=grp['ratio'], marker_color=colors, marker_line_width=0,
                                text=grp['ratio'].apply(lambda v: f"{v:.0f} %"), textposition='outside', textfont=dict(size=11)))
        fig.add_hline(y=100, line_dash="dot", line_color="rgba(231,76,60,0.5)", annotation_text="Seuil 100%", annotation_font_size=10, annotation_font_color=INS_WARN)
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Type", yaxis_title="Ratio S/P (%)", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    @app.callback(Output('g-prime-vs-sinistre', 'figure'), INPUTS)
    def cb_prime_sin(t, r, s, a):
        fd = _fd(t, r, s, a)
        fd_sin = fd[fd['nb_sinistres'] > 0]
        fig = go.Figure()
        for tp in fd_sin['type_assurance'].unique():
            sub = fd_sin[fd_sin['type_assurance'] == tp]
            fig.add_trace(go.Scatter(x=sub['montant_prime'], y=sub['montant_sinistres'], mode='markers', name=tp,
                                      marker=dict(size=6, color=COLORS_TYPE.get(tp, INS_PRIMARY), opacity=0.6, line=dict(width=0)),
                                      hovertemplate='Prime: %{x:.0f} €<br>Sinistre: %{y:.0f} €<extra>' + tp + '</extra>'))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Prime annuelle (€)", yaxis_title="Montant sinistres (€)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    @app.callback(Output('g-dist-montant', 'figure'), INPUTS)
    def cb_dist_mt(t, r, s, a):
        fd = _fd(t, r, s, a)
        fd_sin = fd[fd['montant_sinistres'] > 0]
        fig = go.Figure(go.Histogram(x=fd_sin['montant_sinistres'], nbinsx=40, marker_color='rgba(192,57,43,0.6)',
                                      marker_line_color=INS_ACCENT, marker_line_width=0.5))
        med = fd_sin['montant_sinistres'].median()
        fig.add_vline(x=med, line_dash="dash", line_color=INS_PRIMARY, line_width=2, annotation_text=f"Méd. {med:,.0f} €", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Montant (€)", yaxis_title="Effectif", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.05)
        return fig

    # ═══════════ PAGE 4 callbacks ═══════════

    @app.callback(Output('g-age-montant', 'figure'), INPUTS)
    def cb_age_mt(t, r, s, a):
        fd = _fd(t, r, s, a)
        fd_sin = fd[fd['nb_sinistres'] > 0]
        fig = go.Figure()
        for sx in fd_sin['sexe'].unique():
            sub = fd_sin[fd_sin['sexe'] == sx]
            fig.add_trace(go.Scatter(x=sub['age'], y=sub['montant_sinistres'], mode='markers', name=sx.capitalize(),
                                      marker=dict(size=7, opacity=0.55, line=dict(width=0),
                                                  color=INS_PRIMARY if sx == 'masculin' else INS_ACCENT)))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Âge", yaxis_title="Montant sinistres (€)", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    @app.callback(Output('g-bonus-age', 'figure'), INPUTS)
    def cb_bm_age(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('tranche_age', observed=True)['bonus_malus'].mean().reset_index()
        colors = [INS_SUCCESS if v < 1 else (INS_GOLD if v < 1.2 else INS_WARN) for v in grp['bonus_malus']]
        fig = go.Figure(go.Bar(x=grp['tranche_age'].astype(str), y=grp['bonus_malus'], marker_color=colors, marker_line_width=0,
                                text=grp['bonus_malus'].apply(lambda v: f"{v:.2f}"), textposition='outside', textfont=dict(size=10)))
        fig.add_hline(y=1.0, line_dash="dot", line_color="rgba(100,116,139,0.5)", annotation_text="Neutre (1.0)", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Tranche d'âge", yaxis_title="Coeff. B/M moyen", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    @app.callback(Output('g-sinistres-type-sexe', 'figure'), INPUTS)
    def cb_sin_ts(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby(['type_assurance', 'sexe'])['nb_sinistres'].sum().reset_index()
        fig = go.Figure()
        for sx in grp['sexe'].unique():
            sub = grp[grp['sexe'] == sx]
            fig.add_trace(go.Bar(x=sub['type_assurance'], y=sub['nb_sinistres'], name=sx.capitalize(),
                                  marker_color=INS_PRIMARY if sx == 'masculin' else INS_ACCENT, marker_line_width=0))
        fig.update_layout(**_graph_layout(), height=GH, barmode='group', xaxis_title="Type", yaxis_title="Nb sinistres", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.2)
        return fig

    @app.callback(Output('g-top-regions', 'figure'), INPUTS)
    def cb_top_reg(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('region').agg(nb=('nb_sinistres', 'sum'), mt=('montant_sinistres', 'sum')).reset_index()
        grp['sinistralite'] = np.where(grp['nb'] > 0, grp['mt'] / grp['nb'], 0)
        grp = grp.sort_values('mt', ascending=True).tail(10)
        fig = go.Figure(go.Bar(y=grp['region'], x=grp['mt'], orientation='h', marker_color=INS_WARN, marker_line_width=0,
                                text=grp['mt'].apply(lambda v: f"{v:,.0f} €"), textposition='outside', textfont=dict(size=10)))
        fig.update_layout(**_graph_layout(), height=GH + 30, xaxis_title="Montant total (€)", yaxis_title="", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.25)
        return fig

    @app.callback(Output('g-table-risque', 'children'), INPUTS)
    def cb_table_risque(t, r, s, a):
        fd = _fd(t, r, s, a)
        risk = fd[fd['nb_sinistres'] >= 2].sort_values('montant_sinistres', ascending=False).head(50)
        if len(risk) == 0:
            return html.P("Aucun assuré à haut risque (≥ 2 sinistres) trouvé.", className="text-muted")
        cols = ['id_assure', 'age', 'sexe', 'type_assurance', 'region', 'nb_sinistres', 'montant_sinistres', 'bonus_malus']
        show = risk[cols].copy()
        show['montant_sinistres'] = show['montant_sinistres'].apply(lambda v: f"{v:,.0f} €")
        show['bonus_malus'] = show['bonus_malus'].apply(lambda v: f"{v:.2f}")
        return dash_table.DataTable(
            data=show.to_dict('records'),
            columns=[{"name": c.replace('_', ' ').title(), "id": c} for c in show.columns],
            page_size=12,
            style_table={"overflowX": "auto", "borderRadius": "10px"},
            style_cell={"textAlign": "left", "padding": "10px 14px", "fontFamily": "Segoe UI, system-ui", "fontSize": "0.82rem", "border": "none", "borderBottom": "1px solid #d5dce6"},
            style_header={"fontWeight": "700", "backgroundColor": "#e8edf2", "color": INS_TEXT, "borderBottom": f"2px solid {INS_PRIMARY}", "fontSize": "0.78rem", "textTransform": "uppercase", "letterSpacing": "0.04em"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgba(240,244,248,0.5)"},
                {"if": {"filter_query": "{nb_sinistres} >= 3"}, "backgroundColor": "rgba(231,76,60,0.08)", "color": INS_WARN},
            ],
        )

    # ═══════════ PAGE 5 callbacks ═══════════

    @app.callback(Output('g-dist-bm', 'figure'), INPUTS)
    def cb_dist_bm(t, r, s, a):
        fd = _fd(t, r, s, a)
        fig = go.Figure(go.Histogram(x=fd['bonus_malus'], nbinsx=35, marker_color='rgba(26,58,92,0.6)',
                                      marker_line_color=INS_PRIMARY, marker_line_width=0.5))
        fig.add_vline(x=1.0, line_dash="dot", line_color=INS_WARN, line_width=2, annotation_text="Neutre", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Coeff. B/M", yaxis_title="Effectif", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.05)
        return fig

    @app.callback(Output('g-bm-sinistres', 'figure'), INPUTS)
    def cb_bm_sin(t, r, s, a):
        fd = _fd(t, r, s, a)
        fig = go.Figure(go.Scatter(x=fd['bonus_malus'], y=fd['nb_sinistres'], mode='markers',
                                    marker=dict(size=6, color=fd['montant_sinistres'], colorscale='RdYlGn_r', opacity=0.55,
                                                colorbar=dict(title="Mt. sin.", thickness=12, len=0.6), line=dict(width=0)),
                                    hovertemplate='B/M: %{x:.2f}<br>Sinistres: %{y}<br>Montant: %{marker.color:,.0f} €<extra></extra>'))
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Coeff. Bonus/Malus", yaxis_title="Nb sinistres", xaxis=_XAXIS, yaxis=_YAXIS)
        return fig

    @app.callback(Output('g-bm-region', 'figure'), INPUTS)
    def cb_bm_reg(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('region')['bonus_malus'].mean().reset_index().sort_values('bonus_malus', ascending=True)
        colors = [INS_SUCCESS if v < 1 else (INS_GOLD if v < 1.2 else INS_WARN) for v in grp['bonus_malus']]
        fig = go.Figure(go.Bar(y=grp['region'], x=grp['bonus_malus'], orientation='h', marker_color=colors, marker_line_width=0,
                                text=grp['bonus_malus'].apply(lambda v: f"{v:.2f}"), textposition='outside', textfont=dict(size=10)))
        fig.add_vline(x=1.0, line_dash="dot", line_color="rgba(100,116,139,0.5)", annotation_text="1.0", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=GH + 30, xaxis_title="Coeff. B/M moyen", yaxis_title="", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.25)
        return fig

    @app.callback(Output('g-bm-type', 'figure'), INPUTS)
    def cb_bm_type(t, r, s, a):
        fd = _fd(t, r, s, a)
        grp = fd.groupby('type_assurance')['bonus_malus'].mean().reset_index()
        colors = [COLORS_TYPE.get(x, INS_PRIMARY) for x in grp['type_assurance']]
        fig = go.Figure(go.Bar(x=grp['type_assurance'], y=grp['bonus_malus'], marker_color=colors, marker_line_width=0,
                                text=grp['bonus_malus'].apply(lambda v: f"{v:.2f}"), textposition='outside', textfont=dict(size=11)))
        fig.add_hline(y=1.0, line_dash="dot", line_color="rgba(100,116,139,0.5)", annotation_text="Neutre (1.0)", annotation_font_size=10)
        fig.update_layout(**_graph_layout(), height=GH, xaxis_title="Type", yaxis_title="Coeff. B/M moyen", xaxis=_XAXIS, yaxis=_YAXIS, bargap=0.3)
        return fig

    return app
