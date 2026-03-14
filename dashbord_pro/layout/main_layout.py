"""Layout principal avec sidebar"""
from dash import html, dcc
from layout.sidebar import create_sidebar
from layout.header_main import create_main_header

def create_main_layout(df):
    """Crée le layout principal avec sidebar"""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div([
            create_sidebar(),
            html.Div([
                create_main_header(),
                html.Div(id='page-content', style={'background': '#f5f7fa', 'minHeight': 'calc(100vh - 80px)'})
            ], className="main-content")
        ], className="app-container")
    ])
