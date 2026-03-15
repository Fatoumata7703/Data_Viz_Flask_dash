# -*- coding: utf-8 -*-
"""
Dashboard Dash — Positionnement des banques au Sénégal
Interface premium — Top navbar + tabs, graphiques interactifs.
"""
import os, json, base64
import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
RAPPORT_NOTEBOOK_PATH = os.path.join(_APP_DIR, "rapport.ipynb")

try:
    from .data_loader import get_data
except ImportError:
    from data_loader import get_data

# Données : base PROD uniquement (jamais Excel)
df_raw = get_data()
if df_raw is None or len(df_raw) == 0:
    df_raw = pd.DataFrame(columns=["Sigle", "ANNEE", "BILAN", "Groupe_Bancaire", "EMPLOI", "RESSOURCES", "FONDS_PROPRES"])

for old, new in [
    ("sigle", "Sigle"), ("annee", "ANNEE"), ("bilan", "BILAN"),
    ("groupe_bancaire", "Groupe_Bancaire"), ("Goupe_Bancaire", "Groupe_Bancaire"),
    ("emploi", "EMPLOI"), ("ressources", "RESSOURCES"),
    ("fonds_propres", "FONDS_PROPRES"),
]:
    if old in df_raw.columns and new not in df_raw.columns:
        df_raw = df_raw.rename(columns={old: new})

B = "Sigle"
A = "ANNEE"
G = "Groupe_Bancaire"

INDICATEURS = [("BILAN", "Total Bilan")]
for c, l in [("EMPLOI", "Emplois"), ("RESSOURCES", "Ressources"), ("FONDS_PROPRES", "Fonds Propres")]:
    if c in df_raw.columns:
        INDICATEURS.append((c, l))

df_raw[A] = pd.to_numeric(df_raw[A], errors="coerce")
ANNEES = sorted(df_raw[A].dropna().astype(int).unique().tolist())
AN_DEF = int(ANNEES[-1]) if ANNEES else 2020
BANQUES = sorted(df_raw[B].dropna().unique().astype(str))
GROUPES = sorted(df_raw[G].dropna().unique().astype(str)) if G in df_raw.columns else []
# Options initiales pour le dropdown Banque (année par défaut) — évite "No results found" au chargement
_banques_def = sorted(df_raw.loc[df_raw[A] == AN_DEF, B].dropna().unique().astype(str).tolist())
OPTIONS_BANQUE_DEF = [{"label": "Toutes les banques", "value": ""}] + [{"label": b, "value": b} for b in _banques_def]

# ══════ Palette bancaire — Bleu clair & lumineux ══════
C_BG = "#f0f4f8"
C_PRIMARY = "#2563eb"
C_ACCENT = "#3b82f6"
C_SECONDARY = "#8b5cf6"
C_AMBER = "#f59e0b"
C_TEXT = "#334155"
C_MUTED = "#94a3b8"
C_GREEN = "#10b981"
C_RED = "#ef4444"
C_BORDER = "#e2e8f0"
GRP_COLORS = {
    "Groupes Locaux": "#2563eb",
    "Groupes Régionaux": "#8b5cf6",
    "Groupes Internationaux": "#f59e0b",
    "Groupes Continentaux": "#10b981",
    "Groupes Internationnaux": "#f59e0b",
}
BANK_PALETTE = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
                "#06b6d4", "#ec4899", "#14b8a6", "#f97316", "#6366f1",
                "#84cc16", "#0ea5e9", "#d946ef", "#22d3ee", "#a855f7"]

GH = 370
GH_FULL = 430
GRAPH_CFG = {"responsive": True, "displayModeBar": False}


def _gl(ml=50, mr=30, mt=40, mb=40, **kw):
    base = dict(
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color=C_TEXT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,244,248,0.3)",
        margin=dict(l=ml, r=mr, t=mt, b=mb),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=C_PRIMARY,
            font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=C_TEXT),
        ),
        legend=dict(font=dict(size=10), bgcolor="rgba(255,255,255,0.95)", bordercolor=C_BORDER, borderwidth=1),
    )
    base.update(kw)
    return base


_AX = dict(gridcolor="rgba(226,232,240,0.6)", gridwidth=1, zerolinecolor="rgba(226,232,240,0.7)",
           showline=True, linewidth=1, linecolor="rgba(226,232,240,0.8)")
_XAX = {**_AX, "tickfont": dict(size=10, color=C_MUTED)}
_YAX = {**_AX, "tickfont": dict(size=10, color=C_MUTED)}

# ══════ App (créé par create_dash_app pour Flask ou standalone) ══════


# ══════ Helpers ══════
def fmt_val(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if abs(v) >= 1e6:
        return f"{v/1e6:,.1f} Mrd"
    if abs(v) >= 1e3:
        return f"{v/1e3:,.1f} Mrd"
    return f"{v:,.0f} M"


def _hex_to_rgba(hex_str, alpha):
    h = (hex_str or C_ACCENT).lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    return f"rgba(59,130,246,{alpha})"


def kpi(icon, label, value, sub="", color=C_ACCENT, evo=None):
    evo_el = None
    if evo is not None:
        ec = C_GREEN if evo >= 0 else C_RED
        evo_el = html.Span(f"{'+'if evo>=0 else ''}{evo:.1f}%", style={"color": ec, "fontWeight": "700", "fontSize": "0.75rem"})
    grad_start = _hex_to_rgba(color, 0.22)
    grad_end = _hex_to_rgba(color, 0.06)
    card_style = {"background": f"linear-gradient(90deg, {grad_start} 0%, {grad_end} 60%, rgba(255,255,255,0.4) 100%)"}
    icon_circle_style = {"width": "36px", "height": "36px", "borderRadius": "50%", "background": color, "color": "#fff",
                         "display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "1.1rem",
                         "flexShrink": "0", "lineHeight": "1"}
    return dbc.Card(dbc.CardBody([
        html.Div([
            html.Div(icon, style=icon_circle_style),
            html.Div([
                html.Div(label.upper(), style={"fontSize": "0.65rem", "color": "#374151", "fontWeight": "700", "letterSpacing": "0.04em", "marginBottom": "1px"}),
                html.Div(value, style={"fontSize": "1.2rem", "fontWeight": "800", "color": color, "lineHeight": "1.2"}),
                html.Div([
                    html.Span(sub, style={"fontSize": "0.68rem", "color": C_MUTED}),
                    html.Span(" ", style={"marginRight": "4px"}) if evo_el else None,
                    evo_el,
                ], style={"marginTop": "1px"}) if sub or evo_el else None,
            ], style={"flex": "1", "minWidth": "0"}),
        ], style={"display": "flex", "gap": "10px", "alignItems": "flex-start"}),
    ], className=""), className="bk-kpi-card bk-kpi-card-pastel h-100", style=card_style)


def gcard(title, graph_id, h=GH, subtitle=None):
    header_children = [html.Span(title)]
    if subtitle:
        header_children.append(html.Small(subtitle, id=f"{graph_id}-sub" if subtitle else None,
                                          className="text-muted d-block", style={"fontSize": "0.78rem", "fontWeight": "400"}))
    return dbc.Card([
        dbc.CardHeader(header_children, className="bk-card-header"),
        dbc.CardBody(dcc.Graph(id=graph_id, config=GRAPH_CFG, style={"height": f"{h}px"}), className="p-2"),
    ], className="bk-graph-card")


def ptitle(text):
    return html.H4(text, className="bk-page-title")


def _empty(msg, h=370):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(size=13, color=C_MUTED), xref="paper", yref="paper", x=0.5, y=0.5)
    fig.update_layout(**_gl(height=h), xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


# ══════ PAGES ══════
PAGES = [
    {"id": "overview", "icon": "📊", "label": "Vue d'ensemble"},
    {"id": "positioning", "icon": "🎯", "label": "Positionnement"},
    {"id": "compare", "icon": "⚖️", "label": "Comparaison"},
    {"id": "financial", "icon": "💹", "label": "Analyse Financière"},
    {"id": "report", "icon": "📋", "label": "Rapport"},
]


# ── Page 1 ──
page_overview = html.Div([
    ptitle("Vue d'ensemble du secteur bancaire"),
    dbc.Row(id="kpi-overview", className="g-2 mb-2"),
    dbc.Row([
        dbc.Col(gcard("Évolution du bilan sectoriel", "g-evo-bilan", GH_FULL, "Tendance pluriannuelle"), lg=7, md=12),
        dbc.Col(gcard("Répartition par groupe bancaire", "g-repart-groupe", GH_FULL), lg=5, md=12),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(gcard("Top 10 banques par indicateur", "g-top10", GH), lg=6, md=12),
        dbc.Col(gcard("Parts de marché", "g-parts-marche", GH), lg=6, md=12),
    ], className="g-3"),
], id="page-overview")

# ── Page 2 ──
page_positioning = html.Div([
    ptitle("Positionnement stratégique"),
    dbc.Row([
        dbc.Col(gcard("Part de marché vs Croissance (TCAM)", "g-scatter-pos", GH_FULL, "Positionnement des groupes"), lg=7, md=12),
        dbc.Col(gcard("Croissance annuelle moyenne (TCAM)", "g-tcam-groupes", GH_FULL), lg=5, md=12),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(gcard("Positionnement par banque", "g-scatter-banques", GH_FULL, "Part de marché vs TCAM — toutes banques"), lg=12),
    ], className="g-3"),
], id="page-positioning")

# ── Page 3 ──
page_compare = html.Div([
    ptitle("Comparaison interbancaire"),
    dbc.Row([
        dbc.Col(gcard("Classement par indicateur", "g-bar-ranking", GH_FULL), lg=6, md=12),
        dbc.Col(gcard("Évolution comparée (Top 5)", "g-evo-top5", GH_FULL), lg=6, md=12),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(gcard("Concentration du marché (HHI)", "g-hhi", GH), lg=6, md=12),
        dbc.Col(gcard("Écart de performance", "g-ecart-perf", GH), lg=6, md=12),
    ], className="g-3"),
], id="page-compare")

# ── Page 4 ──
page_financial = html.Div([
    ptitle("Analyse financière approfondie"),
    dbc.Row([
        dbc.Col(gcard("Produit Net Bancaire (PNB)", "g-pnb", GH), lg=6, md=12),
        dbc.Col(gcard("Résultat Net", "g-resultat-net", GH), lg=6, md=12),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(gcard("Rentabilité des fonds propres (ROE)", "g-roe", GH), lg=6, md=12),
        dbc.Col(gcard("Coefficient d'exploitation", "g-coef-exploit", GH), lg=6, md=12),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(gcard("Structure Bilan / Emplois / Ressources", "g-structure", GH_FULL), lg=12),
    ], className="g-3"),
], id="page-financial")

# ── Page 5 (Rapport) : un seul bouton « Rapport » dans la barre de filtres, visible sur tous les onglets ──
page_report = html.Div([
    ptitle("Rapport de positionnement"),
    html.P("Sélectionnez une banque dans les filtres puis cliquez sur le bouton « Rapport » dans la barre ci-dessus pour télécharger le rapport HTML.", className="mb-3", style={"color": C_MUTED, "fontSize": "0.9rem"}),
    dbc.Row([
        dbc.Col(gcard("Fiche banque — Indicateurs clés", "g-fiche-banque", GH_FULL), lg=12),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(gcard("Évolution de la banque sélectionnée", "g-evo-banque", GH), lg=6, md=12),
        dbc.Col(gcard("Position dans le classement", "g-rank-banque", GH), lg=6, md=12),
    ], className="g-3"),
], id="page-report")


# ══════ TOP NAVBAR ══════
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.Span("🏦", style={"fontSize": "1.5rem"})),
                dbc.Col(dbc.NavbarBrand([
                    html.Span("Banques Sénégal", style={"fontWeight": "800", "letterSpacing": "-0.02em"}),
                    html.Span(" · Positionnement", style={"fontWeight": "400", "opacity": "0.7", "fontSize": "0.85rem"}),
                ], className="ms-2")),
            ], align="center", className="g-0"),
            href="#", style={"textDecoration": "none"},
        ),
        dbc.Nav([
            dbc.NavItem(
                dbc.Button(
                    [html.Span(p["icon"], style={"marginRight": "6px"}), p["label"]],
                    id=f"btn-{p['id']}", className="bk-nav-btn", n_clicks=0,
                )
            ) for p in PAGES
        ], className="ms-auto bk-nav-pills", navbar=True),
    ], fluid=True),
    className="bk-navbar",
    dark=True,
    expand="lg",
)

# ══════ SUBHEADER ══════
subheader = html.Div([
    html.Div([
        html.Span(id="header-sub", children=f"Analyse stratégique du secteur bancaire — {AN_DEF}",
                  style={"fontSize": "0.85rem", "fontWeight": "500", "color": C_MUTED}),
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
], className="bk-subheader")

# ══════ FILTERS ══════
filters = dbc.Card(dbc.CardBody([
    dbc.Row([
        dbc.Col([
            html.Label("Année", className="bk-filter-label"),
            dcc.Dropdown(id="dd-annee", options=[{"label": str(a), "value": a} for a in ANNEES],
                         value=AN_DEF, clearable=False, className="bk-dropdown"),
        ], lg=2, md=3, xs=6, className="bk-filter-col"),
        dbc.Col([
            html.Label("Indicateur", className="bk-filter-label"),
            dcc.Dropdown(id="dd-indicateur", options=[{"label": l, "value": c} for c, l in INDICATEURS],
                         value=INDICATEURS[0][0], clearable=False, className="bk-dropdown"),
        ], lg=3, md=3, xs=6, className="bk-filter-col"),
        dbc.Col([
            html.Label("Banque", className="bk-filter-label"),
            dcc.Dropdown(id="dd-banque", options=OPTIONS_BANQUE_DEF, value="", placeholder="Toutes les banques", className="bk-dropdown"),
        ], lg=4, md=3, xs=6, className="bk-filter-col"),
        dbc.Col([
            html.Label("\u00a0", className="bk-filter-label"),
            dbc.Button([html.Span("📥 "), "Rapport"], id="quick-report-btn", className="bk-btn-primary bk-filter-btn"),
            dcc.Download(id="quick-download-html"),
        ], lg=3, md=12, className="bk-filter-col bk-filter-col-btn"),
    ], className="bk-filter-row"),
]), className="bk-filter-bar")


# ══════ LAYOUT ══════
LAYOUT = html.Div([
    navbar,
    dbc.Container([
        subheader,
        filters,
        html.Div([
            html.Div(page_overview, id="wrap-overview", style={"display": "block"}),
            html.Div(page_positioning, id="wrap-positioning", style={"display": "none"}),
            html.Div(page_compare, id="wrap-compare", style={"display": "none"}),
            html.Div(page_financial, id="wrap-financial", style={"display": "none"}),
            html.Div(page_report, id="wrap-report", style={"display": "none"}),
        ], id="pages-container"),
    ], fluid=True, className="bk-content"),
    dcc.Store(id="store-filters", data={"annee": AN_DEF, "indicateur": INDICATEURS[0][0], "banque": "", "groupe": ""}),
    html.Div([
        dbc.Toast(
            html.Div([
                html.Div("🏦", className="bk-toast-icon"),
                html.Span("Veuillez sélectionner une banque.", className="bk-toast-line"),
                html.Button("×", id="toast-report-close", className="bk-toast-close", title="Fermer", type="button"),
            ], className="bk-toast-body-inner"),
            id="toast-report",
            header=None,
            is_open=False,
            dismissable=True,
            duration=7000,
            className="bk-toast-report",
        ),
    ], className="bk-toast-container"),
], className="bk-app")


def create_dash_app(server=None, url_base_pathname="/bank/", requests_pathname_prefix=None):
    if url_base_pathname and not url_base_pathname.startswith("/"):
        url_base_pathname = "/" + url_base_pathname
    """
    Crée l'application Dash bancaire (pour montage Flask ou exécution standalone).
    Comme dashboard/dash1.py et dash2.py : appelée par app.py avec server et url_base_pathname.
    """
    _assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    kwargs = dict(
        server=server,
        external_stylesheets=[
            dbc.themes.FLATLY,
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        ],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        suppress_callback_exceptions=True,
        assets_folder=_assets_dir,
    )
    if requests_pathname_prefix is not None:
        kwargs["routes_pathname_prefix"] = url_base_pathname
        kwargs["requests_pathname_prefix"] = requests_pathname_prefix
    else:
        kwargs["url_base_pathname"] = url_base_pathname
    app = dash.Dash(__name__, **kwargs)
    app.title = "Positionnement Bancaire — Sénégal"
    app.layout = LAYOUT
    register_callbacks(app)
    return app


def register_callbacks(app):
    """Enregistre tous les callbacks sur l'instance Dash (Flask ou standalone)."""
    @app.callback(
        [Output(f"wrap-{p['id']}", "style") for p in PAGES] +
        [Output(f"btn-{p['id']}", "className") for p in PAGES],
        [Input(f"btn-{p['id']}", "n_clicks") for p in PAGES],
    )
    def navigate(*clicks):
        triggered = ctx.triggered_id or "btn-overview"
        active_id = triggered.replace("btn-", "")
        styles = [{"display": "block"} if p["id"] == active_id else {"display": "none"} for p in PAGES]
        classes = ["bk-nav-btn active" if p["id"] == active_id else "bk-nav-btn" for p in PAGES]
        return styles + classes


    @app.callback(
        Output("dd-banque", "options"),
        Output("dd-banque", "value"),
        Input("dd-annee", "value"),
    )
    def update_banques_for_year(annee):
        """Affiche uniquement les banques disponibles pour l'année sélectionnée."""
        a = int(annee) if annee else AN_DEF
        d = df_raw[df_raw[A] == a]
        banques_annee = sorted(d[B].dropna().unique().astype(str).tolist())
        options = [{"label": "Toutes les banques", "value": ""}] + [{"label": b, "value": b} for b in banques_annee]
        return options, ""

    @app.callback(
        Output("store-filters", "data"),
        Output("header-sub", "children"),
        Input("dd-annee", "value"),
        Input("dd-indicateur", "value"),
        Input("dd-banque", "value"),
    )
    def update_store(annee, ind, banque):
        a = int(annee) if annee else AN_DEF
        data = {"annee": a, "indicateur": ind or "BILAN", "banque": banque or "", "groupe": ""}
        sub = f"Analyse stratégique du secteur bancaire — {a}"
        if banque:
            sub = f"Focus {banque} — {a}"
        return data, sub


    def _filter(annee=None, groupe=None, banque=None):
        d = df_raw.copy()
        if annee:
            d = d[d[A] == int(annee)]
        if groupe:
            d = d[d[G].astype(str).str.strip() == str(groupe).strip()]
        if banque and str(banque).strip():
            d = d[d[B].astype(str).str.strip().str.upper() == str(banque).strip().upper()]
        return d


    # ── KPIs ── (secteur = année + indicateur ; si banque choisie = données de cette banque)
    @app.callback(Output("kpi-overview", "children"), Input("store-filters", "data"))
    def update_kpi(sf):
        if not sf:
            sf = {"annee": AN_DEF, "indicateur": INDICATEURS[0][0], "banque": "", "groupe": ""}
        an = sf["annee"]
        ind = sf["indicateur"]
        banque = (sf.get("banque") or "").strip()
        d = _filter(an, banque=banque)
        total = d[ind].sum() if ind in d.columns else 0
        n_banks = d[B].nunique()
        d_prev = _filter(an - 1, banque=banque)
        total_prev = d_prev[ind].sum() if ind in d_prev.columns and len(d_prev) else 0
        evo = ((total / total_prev) - 1) * 100 if total_prev > 0 else None
        pnb = d["produit_net_bancaire"].sum() if "produit_net_bancaire" in d.columns else None
        rn = d["resultat_net"].sum() if "resultat_net" in d.columns else None
        effectif = d["effectif"].sum() if "effectif" in d.columns else None
        agences = d["agence"].sum() if "agence" in d.columns else None
        ctx_label = f"{banque} {an}" if banque else f"Secteur {an}"
        an_label = f"Année {an}" if not banque else f"{banque} {an}"
        cards = [
            dbc.Col(kpi("🏦", f"Total {ind}", fmt_val(total), an_label, C_ACCENT, evo), xl=2, lg=4, md=6, xs=12),
            dbc.Col(kpi("🏢", "Banques actives", str(n_banks), an_label, C_PRIMARY), xl=2, lg=4, md=6, xs=12),
            dbc.Col(kpi("📈", "Produit Net Bancaire", fmt_val(pnb) if pnb else "—", ctx_label, C_SECONDARY), xl=2, lg=4, md=6, xs=12),
            dbc.Col(kpi("💎", "Résultat Net", fmt_val(rn) if rn else "—", ctx_label, C_GREEN if rn and rn > 0 else C_RED), xl=2, lg=4, md=6, xs=12),
            dbc.Col(kpi("👥", "Effectifs", f"{int(effectif):,}".replace(",", " ") if effectif else "—", ctx_label, C_TEXT), xl=2, lg=4, md=6, xs=12),
            dbc.Col(kpi("🏪", "Agences", f"{int(agences):,}".replace(",", " ") if agences else "—", ctx_label, C_AMBER), xl=2, lg=4, md=6, xs=12),
        ]
        return cards


    def _default_sf(sf):
        if not sf:
            return {"annee": AN_DEF, "indicateur": INDICATEURS[0][0], "banque": "", "groupe": ""}
        return sf

    # ── Evolution bilan ──
    @app.callback(Output("g-evo-bilan", "figure"), Input("store-filters", "data"))
    def update_evo_bilan(sf):
        sf = _default_sf(sf)
        ind = sf["indicateur"]
        an = sf["annee"]
        a_start = max(an - 4, min(ANNEES)) if ANNEES else an
        d = df_raw[df_raw[A].between(a_start, an)] if len(df_raw) else pd.DataFrame()
        if ind not in d.columns or len(d) == 0:
            return _empty("Indicateur non disponible" if ind not in df_raw.columns else "Pas de données pour cette période")
        by_y = d.groupby(A)[ind].sum().reset_index().sort_values(A)
        if len(by_y) == 0:
            return _empty("Pas de données pour cette période")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=by_y[A].astype(int), y=by_y[ind], mode="lines+markers",
                                 line=dict(color=C_ACCENT, width=3, shape="spline"),
                                 marker=dict(size=10, color=C_PRIMARY, line=dict(color="#fff", width=2)),
                                 fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
                                 hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL), xaxis={**_XAX, "title": "Année", "dtick": 1},
                          yaxis={**_YAX, "title": ind}, showlegend=False)
        return fig


    # ── Répartition groupes ──
    @app.callback(Output("g-repart-groupe", "figure"), Input("store-filters", "data"))
    def update_repart_groupe(sf):
        sf = _default_sf(sf)
        d = _filter(sf["annee"])
        ind = sf["indicateur"]
        if G not in d.columns or ind not in d.columns:
            return _empty("Données insuffisantes")
        agg = d.groupby(G)[ind].sum().reset_index().sort_values(ind, ascending=False)
        colors = [GRP_COLORS.get(g, "#94a3b8") for g in agg[G]]
        fig = go.Figure(go.Pie(labels=agg[G], values=agg[ind], hole=0.55,
                               marker=dict(colors=colors, line=dict(color="#fff", width=2.5)),
                               textinfo="label+percent", textposition="outside",
                               textfont=dict(size=11),
                               hovertemplate="%{label}<br>%{value:,.0f} (%{percent})<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL), showlegend=False)
        return fig


    # ── Top 10 ──
    @app.callback(Output("g-top10", "figure"), Input("store-filters", "data"))
    def update_top10(sf):
        d = _filter(sf["annee"])
        ind = sf["indicateur"]
        if ind not in d.columns:
            return _empty("Indicateur non disponible")
        agg = d.groupby(B)[ind].sum().reset_index().sort_values(ind, ascending=True).tail(10)
        banque_sel = sf.get("banque", "")
        colors = [C_RED if str(b).strip().upper() == banque_sel.strip().upper() else C_ACCENT for b in agg[B]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg[ind], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:,.0f}" for v in agg[ind]], textposition="outside",
                               textfont=dict(size=10),
                               hovertemplate="%{y}: %{x:,.0f}<extra></extra>"))
        fig.update_layout(**_gl(height=GH, ml=90, mr=60, mt=30, mb=40),
                          xaxis={**_XAX, "title": ind},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── Parts de marché ──
    @app.callback(Output("g-parts-marche", "figure"), Input("store-filters", "data"))
    def update_parts(sf):
        sf = _default_sf(sf)
        d = _filter(sf["annee"])
        ind = sf["indicateur"]
        if ind not in d.columns:
            return _empty("Indicateur non disponible")
        agg = d.groupby(B)[ind].sum().reset_index()
        total = agg[ind].sum()
        agg["part"] = (agg[ind] / total * 100).round(1) if total > 0 else 0
        agg = agg.sort_values("part", ascending=False)
        fig = go.Figure(go.Pie(labels=agg[B], values=agg[ind], hole=0.5,
                               marker=dict(colors=BANK_PALETTE[:len(agg)], line=dict(color="#fff", width=1.5)),
                               textinfo="label+percent", textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>"))
        fig.update_layout(**_gl(height=GH, ml=20, mr=20, mt=30, mb=20), showlegend=False)
        return fig


    # ── Scatter positionnement groupes ──
    @app.callback(Output("g-scatter-pos", "figure"), Input("store-filters", "data"))
    def update_scatter_pos(sf):
        sf = _default_sf(sf)
        ind = sf["indicateur"]
        an = sf["annee"]
        if ind not in df_raw.columns or G not in df_raw.columns:
            return _empty("Données insuffisantes")
        a_start = max(min(ANNEES), an - 5)
        d_s = df_raw[df_raw[A] == a_start].groupby(G)[ind].sum().reset_index()
        d_e = df_raw[df_raw[A] == an].groupby(G)[ind].sum().reset_index()
        d_s.columns = [G, "v0"]
        d_e.columns = [G, "v1"]
        m = pd.merge(d_s, d_e, on=G, how="inner")
        m = m[(m["v0"] > 0) & (m["v1"] > 0)]
        if len(m) == 0:
            return _empty("Pas assez de données")
        n = an - a_start or 1
        m["tcam"] = ((m["v1"] / m["v0"]) ** (1 / n) - 1) * 100
        m["part"] = (m["v1"] / m["v1"].sum()) * 100
        fig = go.Figure()
        for _, row in m.iterrows():
            c = GRP_COLORS.get(row[G], "#94a3b8")
            fig.add_trace(go.Scatter(x=[row["part"]], y=[row["tcam"]], mode="markers+text",
                                     name=row[G], text=[row[G]], textposition="top center",
                                     marker=dict(size=22, color=c, line=dict(color="#fff", width=2.5), opacity=0.9),
                                     textfont=dict(size=10, color=c),
                                     hovertemplate=f"{row[G]}<br>Part: {row['part']:.1f}%<br>TCAM: {row['tcam']:.1f}%<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL), xaxis={**_XAX, "title": "Part de marché (%)"},
                          yaxis={**_YAX, "title": f"TCAM {a_start}-{an} (%)"},
                          showlegend=False)
        return fig


    # ── TCAM groupes ──
    @app.callback(Output("g-tcam-groupes", "figure"), Input("store-filters", "data"))
    def update_tcam_groupes(sf):
        sf = _default_sf(sf)
        ind = sf["indicateur"]
        an = sf["annee"]
        if ind not in df_raw.columns or G not in df_raw.columns:
            return _empty("Données insuffisantes")
        a_start = max(min(ANNEES), an - 5) if ANNEES else an
        d_s = df_raw[df_raw[A] == a_start].groupby(G)[ind].sum().reset_index()
        d_e = df_raw[df_raw[A] == an].groupby(G)[ind].sum().reset_index()
        d_s.columns = [G, "v0"]
        d_e.columns = [G, "v1"]
        m = pd.merge(d_s, d_e, on=G, how="inner")
        m = m[(m["v0"] > 0) & (m["v1"] > 0)]
        if len(m) == 0:
            return _empty("Pas assez de données")
        n = an - a_start or 1
        m["tcam"] = ((m["v1"] / m["v0"]) ** (1 / n) - 1) * 100
        m = m.sort_values("tcam", ascending=True)
        colors = [GRP_COLORS.get(g, "#94a3b8") for g in m[G]]
        fig = go.Figure(go.Bar(y=m[G], x=m["tcam"], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:.1f}%" for v in m["tcam"]], textposition="outside",
                               hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL, ml=130, mr=60, mt=30, mb=40),
                          xaxis={**_XAX, "title": "TCAM (%)"},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── Scatter banques ──
    @app.callback(Output("g-scatter-banques", "figure"), Input("store-filters", "data"))
    def update_scatter_banques(sf):
        sf = _default_sf(sf)
        ind = sf["indicateur"]
        an = sf["annee"]
        banque_sel = sf.get("banque", "")
        if ind not in df_raw.columns:
            return _empty("Indicateur non disponible")
        a_start = max(min(ANNEES), an - 5) if ANNEES else an
        d_s = df_raw[df_raw[A] == a_start].groupby(B)[ind].sum().reset_index()
        d_e = df_raw[df_raw[A] == an].groupby(B)[ind].sum().reset_index()
        d_s.columns = [B, "v0"]
        d_e.columns = [B, "v1"]
        m = pd.merge(d_s, d_e, on=B, how="inner")
        m = m[(m["v0"] > 0) & (m["v1"] > 0)]
        if len(m) == 0:
            return _empty("Pas assez de données")
        n = an - a_start or 1
        m["tcam"] = ((m["v1"] / m["v0"]) ** (1 / n) - 1) * 100
        m["part"] = (m["v1"] / m["v1"].sum()) * 100
        fig = go.Figure()
        for _, row in m.iterrows():
            is_sel = banque_sel and str(row[B]).strip().upper() == banque_sel.strip().upper()
            c = C_RED if is_sel else C_ACCENT
            sz = 18 if is_sel else 11
            fig.add_trace(go.Scatter(x=[row["part"]], y=[row["tcam"]], mode="markers+text",
                                     name=row[B], text=[row[B]] if is_sel or row["part"] > 5 else [""],
                                     textposition="top center",
                                     marker=dict(size=sz, color=c, line=dict(color="#fff", width=2), opacity=0.85),
                                     textfont=dict(size=9 if not is_sel else 11, color=C_PRIMARY),
                                     hovertemplate=f"{row[B]}<br>Part: {row['part']:.1f}%<br>TCAM: {row['tcam']:.1f}%<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL), xaxis={**_XAX, "title": "Part de marché (%)"},
                          yaxis={**_YAX, "title": f"TCAM {a_start}-{an} (%)"},
                          showlegend=False)
        return fig


    # ── Ranking ──
    @app.callback(Output("g-bar-ranking", "figure"), Input("store-filters", "data"))
    def update_ranking(sf):
        sf = _default_sf(sf)
        d = _filter(sf["annee"])
        ind = sf["indicateur"]
        banque_sel = sf.get("banque", "")
        if ind not in d.columns:
            return _empty("Indicateur non disponible")
        agg = d.groupby(B)[ind].sum().reset_index().sort_values(ind, ascending=True)
        colors = [C_RED if banque_sel and str(b).strip().upper() == banque_sel.strip().upper() else C_ACCENT for b in agg[B]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg[ind], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:,.0f}" for v in agg[ind]], textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{y}: %{x:,.0f}<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL, ml=90, mr=70, mt=30, mb=40),
                          xaxis={**_XAX, "title": ind},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── Evo Top 5 ──
    @app.callback(Output("g-evo-top5", "figure"), Input("store-filters", "data"))
    def update_evo_top5(sf):
        sf = _default_sf(sf)
        ind = sf["indicateur"]
        an = sf["annee"]
        if ind not in df_raw.columns:
            return _empty("Indicateur non disponible")
        d_last = _filter(an)
        top5 = d_last.groupby(B)[ind].sum().nlargest(5).index.tolist()
        fig = go.Figure()
        for i, bank in enumerate(top5):
            db = df_raw[df_raw[B] == bank].groupby(A)[ind].sum().reset_index().sort_values(A)
            fig.add_trace(go.Scatter(x=db[A].astype(int), y=db[ind], mode="lines+markers",
                                     name=bank, line=dict(width=2.5, shape="spline"),
                                     marker=dict(size=7),
                                     hovertemplate=f"{bank}<br>%{{x}}: %{{y:,.0f}}<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL), xaxis={**_XAX, "title": "Année", "dtick": 1},
                          yaxis={**_YAX, "title": ind})
        return fig


    # ── HHI ──
    @app.callback(Output("g-hhi", "figure"), Input("store-filters", "data"))
    def update_hhi(sf):
        sf = _default_sf(sf)
        ind = sf["indicateur"]
        if ind not in df_raw.columns:
            return _empty("Indicateur non disponible")
        hhis = []
        for y in ANNEES:
            dy = df_raw[df_raw[A] == y]
            agg = dy.groupby(B)[ind].sum()
            total = agg.sum()
            if total > 0:
                shares = (agg / total * 100)
                hhi = (shares ** 2).sum()
                hhis.append({"annee": y, "hhi": hhi})
        if not hhis:
            return _empty("Pas assez de données")
        dh = pd.DataFrame(hhis)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dh["annee"], y=dh["hhi"], mode="lines+markers",
                                 line=dict(color=C_SECONDARY, width=3, shape="spline"),
                                 marker=dict(size=9, color=C_PRIMARY, line=dict(color="#fff", width=2)),
                                 fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
                                 hovertemplate="%{x}: HHI = %{y:.0f}<extra></extra>"))
        fig.add_hline(y=1800, line_dash="dash", line_color=C_RED, annotation_text="Concentration élevée",
                      annotation_font_size=10, annotation_font_color=C_RED)
        fig.add_hline(y=1000, line_dash="dash", line_color=C_GREEN, annotation_text="Concentration modérée",
                      annotation_font_size=10, annotation_font_color=C_GREEN)
        fig.update_layout(**_gl(height=GH), xaxis={**_XAX, "title": "Année", "dtick": 1},
                          yaxis={**_YAX, "title": "Indice HHI"}, showlegend=False)
        return fig


    # ── Écart performance ──
    @app.callback(Output("g-ecart-perf", "figure"), Input("store-filters", "data"))
    def update_ecart(sf):
        sf = _default_sf(sf)
        d = _filter(sf["annee"])
        ind = sf["indicateur"]
        if ind not in d.columns or len(d) == 0:
            return _empty("Indicateur non disponible")
        agg = d.groupby(B)[ind].sum().reset_index()
        if len(agg) == 0:
            return _empty("Pas de données")
        mean_v = agg[ind].mean()
        if mean_v == 0:
            return _empty("Pas de données")
        agg["ecart"] = ((agg[ind] - mean_v) / mean_v * 100).round(1)
        agg = agg.sort_values("ecart", ascending=True)
        colors = [C_GREEN if e >= 0 else C_RED for e in agg["ecart"]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg["ecart"], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:+.1f}%" for v in agg["ecart"]], textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{y}: %{x:+.1f}% vs moyenne<extra></extra>"))
        fig.add_vline(x=0, line_color=C_MUTED, line_width=1)
        fig.update_layout(**_gl(height=GH, ml=90, mr=60, mt=30, mb=40),
                          xaxis={**_XAX, "title": "Écart vs moyenne (%)"},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── PNB ──
    @app.callback(Output("g-pnb", "figure"), Input("store-filters", "data"))
    def update_pnb(sf):
        sf = _default_sf(sf)
        col = "produit_net_bancaire"
        if col not in df_raw.columns:
            return _empty("PNB non disponible")
        d = _filter(sf["annee"])
        agg = d.groupby(B)[col].sum().reset_index().sort_values(col, ascending=True).tail(12)
        banque_sel = sf.get("banque", "")
        colors = [C_RED if banque_sel and str(b).strip().upper() == banque_sel.strip().upper() else C_AMBER for b in agg[B]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg[col], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:,.0f}" for v in agg[col]], textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{y}: %{x:,.0f}<extra></extra>"))
        fig.update_layout(**_gl(height=GH, ml=90, mr=70, mt=30, mb=40),
                          xaxis={**_XAX, "title": "PNB"},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── Résultat Net ──
    @app.callback(Output("g-resultat-net", "figure"), Input("store-filters", "data"))
    def update_rn(sf):
        sf = _default_sf(sf)
        col = "resultat_net"
        if col not in df_raw.columns:
            return _empty("Résultat net non disponible")
        d = _filter(sf["annee"])
        agg = d.groupby(B)[col].sum().reset_index().sort_values(col, ascending=True)
        colors = [C_GREEN if v >= 0 else C_RED for v in agg[col]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg[col], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:,.0f}" for v in agg[col]], textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{y}: %{x:,.0f}<extra></extra>"))
        fig.add_vline(x=0, line_color=C_MUTED, line_width=1)
        fig.update_layout(**_gl(height=GH, ml=90, mr=70, mt=30, mb=40),
                          xaxis={**_XAX, "title": "Résultat Net"},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── ROE ──
    @app.callback(Output("g-roe", "figure"), Input("store-filters", "data"))
    def update_roe(sf):
        sf = _default_sf(sf)
        rn_col = "resultat_net"
        fp_col = "FONDS_PROPRES" if "FONDS_PROPRES" in df_raw.columns else "fonds_propres"
        if rn_col not in df_raw.columns or fp_col not in df_raw.columns:
            return _empty("Données insuffisantes pour ROE")
        d = _filter(sf["annee"])
        agg = d.groupby(B).agg({rn_col: "sum", fp_col: "sum"}).reset_index()
        agg["roe"] = np.where(agg[fp_col] > 0, (agg[rn_col] / agg[fp_col]) * 100, 0)
        agg = agg.sort_values("roe", ascending=True)
        colors = [C_GREEN if v >= 0 else C_RED for v in agg["roe"]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg["roe"], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:.1f}%" for v in agg["roe"]], textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{y}: ROE = %{x:.1f}%<extra></extra>"))
        fig.add_vline(x=0, line_color=C_MUTED, line_width=1)
        fig.update_layout(**_gl(height=GH, ml=90, mr=60, mt=30, mb=40),
                          xaxis={**_XAX, "title": "ROE (%)"},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── Coefficient exploitation ──
    @app.callback(Output("g-coef-exploit", "figure"), Input("store-filters", "data"))
    def update_coef(sf):
        sf = _default_sf(sf)
        pnb_col = "produit_net_bancaire"
        cge_col = "charges_generales_d'exploitation"
        if pnb_col not in df_raw.columns or cge_col not in df_raw.columns:
            return _empty("Données insuffisantes")
        d = _filter(sf["annee"])
        agg = d.groupby(B).agg({pnb_col: "sum", cge_col: "sum"}).reset_index()
        agg["coef"] = np.where(agg[pnb_col] > 0, (agg[cge_col] / agg[pnb_col]) * 100, 0)
        agg = agg.sort_values("coef", ascending=True)
        colors = [C_GREEN if v < 60 else (C_AMBER if v < 75 else C_RED) for v in agg["coef"]]
        fig = go.Figure(go.Bar(y=agg[B], x=agg["coef"], orientation="h",
                               marker=dict(color=colors, line=dict(color="#fff", width=1)),
                               text=[f"{v:.1f}%" for v in agg["coef"]], textposition="outside",
                               textfont=dict(size=9),
                               hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        fig.add_vline(x=60, line_dash="dash", line_color=C_GREEN, annotation_text="Seuil efficient",
                      annotation_font_size=10)
        fig.update_layout(**_gl(height=GH, ml=90, mr=60, mt=30, mb=40),
                          xaxis={**_XAX, "title": "Coef. d'exploitation (%)"},
                          yaxis={**_YAX, "automargin": True}, showlegend=False)
        return fig


    # ── Structure ──
    @app.callback(Output("g-structure", "figure"), Input("store-filters", "data"))
    def update_structure(sf):
        sf = _default_sf(sf)
        cols = [c for c, _ in INDICATEURS if c in df_raw.columns]
        if not cols:
            return _empty("Pas d'indicateurs")
        fig = go.Figure()
        palette = [C_ACCENT, C_SECONDARY, C_AMBER, C_GREEN]
        for i, c in enumerate(cols):
            by_y = df_raw.groupby(A)[c].sum().reset_index().sort_values(A)
            fig.add_trace(go.Scatter(x=by_y[A].astype(int), y=by_y[c], mode="lines+markers",
                                     name=c, line=dict(width=2.5, color=palette[i % len(palette)], shape="spline"),
                                     marker=dict(size=7),
                                     hovertemplate=f"{c}<br>%{{x}}: %{{y:,.0f}}<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL), xaxis={**_XAX, "title": "Année", "dtick": 1},
                          yaxis={**_YAX, "title": "Montant"})
        return fig


    # ── Fiche banque ──
    @app.callback(Output("g-fiche-banque", "figure"), Input("store-filters", "data"))
    def update_fiche(sf):
        sf = _default_sf(sf)
        banque_sel = sf.get("banque", "")
        an = sf["annee"]
        if not banque_sel:
            return _empty("Sélectionnez une banque dans les filtres")
        d = df_raw[(df_raw[B].astype(str).str.strip().str.upper() == banque_sel.strip().upper()) & (df_raw[A] == an)]
        if len(d) == 0:
            return _empty(f"Pas de données pour {banque_sel} en {an}")
        cols_show = ["BILAN", "EMPLOI", "RESSOURCES", "FONDS_PROPRES", "fonds_propres",
                     "produit_net_bancaire", "resultat_net", "effectif", "agence", "COMPTE"]
        cols_show = [c for c in cols_show if c in d.columns and d[c].notna().any()]
        labels = {"BILAN": "Bilan", "EMPLOI": "Emplois", "RESSOURCES": "Ressources",
                  "FONDS_PROPRES": "Fonds Propres", "fonds_propres": "Fonds Propres",
                  "produit_net_bancaire": "PNB", "resultat_net": "Résultat Net",
                  "effectif": "Effectifs", "agence": "Agences", "COMPTE": "Comptes"}
        vals = [d[c].sum() for c in cols_show]
        names = [labels.get(c, c) for c in cols_show]
        pal = [C_ACCENT, C_SECONDARY, C_AMBER, C_GREEN, "#a855f7", "#ec4899", C_MUTED, "#f97316", "#14b8a6"]
        fig = go.Figure(go.Bar(x=names, y=vals,
                               marker=dict(color=pal[:len(vals)], line=dict(color="#fff", width=1.5)),
                               text=[f"{v:,.0f}" for v in vals], textposition="outside",
                               textfont=dict(size=10),
                               hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
        fig.update_layout(**_gl(height=GH_FULL, ml=60, mr=30, mt=60, mb=40, title=f"{banque_sel} — {an}"),
                          xaxis={**_XAX}, yaxis={**_YAX, "title": "Montant"}, showlegend=False)
        return fig


    # ── Evo banque ──
    @app.callback(Output("g-evo-banque", "figure"), Input("store-filters", "data"))
    def update_evo_banque(sf):
        sf = _default_sf(sf)
        banque_sel = sf.get("banque", "")
        ind = sf["indicateur"]
        if not banque_sel:
            return _empty("Sélectionnez une banque")
        db = df_raw[df_raw[B].astype(str).str.strip().str.upper() == banque_sel.strip().upper()]
        if len(db) == 0 or ind not in db.columns:
            return _empty(f"Pas de données pour {banque_sel}")
        by_y = db.groupby(A)[ind].sum().reset_index().sort_values(A)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=by_y[A].astype(int), y=by_y[ind],
                             marker=dict(color=C_ACCENT, line=dict(color="#fff", width=1)),
                             hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=by_y[A].astype(int), y=by_y[ind], mode="lines",
                                 line=dict(color=C_PRIMARY, width=2.5, shape="spline"),
                                 showlegend=False))
        fig.update_layout(**_gl(height=GH, ml=60, mr=30, mt=60, mb=40, title=f"{banque_sel} — {ind}"),
                          xaxis={**_XAX, "title": "Année", "dtick": 1},
                          yaxis={**_YAX, "title": ind}, showlegend=False)
        return fig


    # ── Rank banque ──
    @app.callback(Output("g-rank-banque", "figure"), Input("store-filters", "data"))
    def update_rank_banque(sf):
        sf = _default_sf(sf)
        banque_sel = sf.get("banque", "")
        ind = sf["indicateur"]
        if not banque_sel or ind not in df_raw.columns:
            return _empty("Sélectionnez une banque")
        ranks = []
        for y in ANNEES:
            dy = df_raw[df_raw[A] == y]
            agg = dy.groupby(B)[ind].sum().sort_values(ascending=False).reset_index()
            agg["rank"] = range(1, len(agg) + 1)
            r = agg[agg[B].astype(str).str.strip().str.upper() == banque_sel.strip().upper()]
            if len(r):
                ranks.append({"annee": y, "rank": int(r["rank"].iloc[0]), "total": len(agg)})
        if not ranks:
            return _empty(f"Pas de données pour {banque_sel}")
        dr = pd.DataFrame(ranks)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dr["annee"], y=dr["rank"], mode="lines+markers+text",
                                 line=dict(color=C_SECONDARY, width=3, shape="spline"),
                                 marker=dict(size=12, color=C_PRIMARY, line=dict(color="#fff", width=2)),
                                 text=[f"#{r}" for r in dr["rank"]], textposition="top center",
                                 textfont=dict(size=11, color=C_PRIMARY),
                                 hovertemplate="%{x}: Rang %{y}<extra></extra>"))
        fig.update_layout(**_gl(height=GH, ml=60, mr=30, mt=60, mb=40, title=f"Rang de {banque_sel}"),
                          xaxis={**_XAX, "title": "Année", "dtick": 1},
                          yaxis={**_YAX, "title": "Position", "autorange": "reversed"},
                          showlegend=False)
        return fig


    # ── Download rapport (cache 10 min pour téléchargement rapide si même banque/année) ──
    _rapport_cache = {}
    _rapport_cache_ttl = 600  # secondes

    def _gen_rapport(banque, annee):
        try:
            from .generate_rapport.convert_to_html import notebook_to_html
        except ImportError:
            from projet_positionnement_bank.generate_rapport.convert_to_html import notebook_to_html
        import time
        b = (banque or "").strip() or None
        a = int(annee) if annee is not None else None
        key = (b, a)
        now = time.time()
        if key in _rapport_cache:
            cached_html, cached_at = _rapport_cache[key]
            if now - cached_at < _rapport_cache_ttl:
                return cached_html, f"_{b}" if b else ""
        if not os.path.isfile(RAPPORT_NOTEBOOK_PATH):
            raise FileNotFoundError(f"Notebook introuvable: {RAPPORT_NOTEBOOK_PATH}")
        html_c = notebook_to_html(RAPPORT_NOTEBOOK_PATH, banque=b, annee=a)
        suffix = f"_{b}" if b else ""
        _rapport_cache[key] = (html_c, now)
        return html_c, suffix


    toast_rapport_msg = html.Div([
        html.Div("🏦", className="bk-toast-icon"),
        html.Span("Veuillez sélectionner une banque.", className="bk-toast-line"),
        html.Button("×", id="toast-report-close", className="bk-toast-close", title="Fermer", type="button"),
    ], className="bk-toast-body-inner")

    @app.callback(
        Output("quick-download-html", "data"),
        Output("toast-report", "is_open"),
        Output("toast-report", "children"),
        Input("quick-report-btn", "n_clicks"),
        Input("toast-report-close", "n_clicks"),
        State("dd-banque", "value"),
        State("dd-annee", "value"),
        prevent_initial_call=True,
    )
    def rapport_download_and_close(n_quick, n_close, banque, annee):
        triggered = ctx.triggered_id or ""
        if triggered == "toast-report-close":
            return no_update, False, no_update
        if triggered != "quick-report-btn" or not n_quick:
            return no_update, no_update, no_update
        if not (banque and str(banque).strip()):
            return no_update, True, toast_rapport_msg
        try:
            html_c, suffix = _gen_rapport(banque, annee)
            payload = dict(content=html_c, filename=f"rapport_bancaire{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            return payload, False, no_update
        except Exception as e:
            err_msg = str(e).strip()
            if "Kernel died" in err_msg or "kernel" in err_msg.lower() or "nbconvert" in err_msg or "nbclient" in err_msg:
                user_msg = "La génération du rapport (notebook Jupyter) n'est pas disponible sur ce serveur. Exportez le rapport en local."
            else:
                user_msg = err_msg
            print(f"Erreur rapport: {e}")
            import traceback
            traceback.print_exc()
            return no_update, True, [html.Strong("Rapport non disponible"), html.P(user_msg, className="mb-0 mt-2 small")]


if __name__ == "__main__":
    app = create_dash_app(None, "/")
    app.run(debug=True, port=8050)
