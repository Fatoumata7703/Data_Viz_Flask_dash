"""Icônes SVG professionnelles en blanc pour la sidebar"""
from dash import html

def create_icon_svg(icon_name, size=24, color=None):
    """Crée une icône SVG professionnelle avec couleur personnalisable"""
    # Couleur par défaut : blanc pour la sidebar, sinon utiliser la couleur fournie
    stroke_color = color if color else "white"
    fill_color = color if color else "white"
    icons = {
        'home': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9.55228 21 10 20.5523 10 20V16C10 15.4477 10.4477 15 11 15H13C13.5523 15 14 15.4477 14 16V20C14 20.5523 14.4477 21 15 21M9 21H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'hospital': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 21H21M5 21V7L12 3L19 7V21M9 9V21M9 9H15M15 9V21M9 13H15M9 17H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 7V11M12 11V15M12 11H8M12 11H16" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'virus': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="3" stroke="{stroke_color}" stroke-width="2"/>
            <path d="M12 1V3M12 21V23M1 12H3M21 12H23M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round"/>
            <circle cx="12" cy="12" r="1" fill="{fill_color}"/>
        </svg>''',
        'user': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="7" r="4" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'pill': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.5 8.5L15.5 15.5M15.5 8.5L8.5 15.5" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="white" stroke-width="2"/>
        </svg>''',
        'warning': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'chart': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 3V21H21" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 16L12 11L16 15L21 10" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 10H16V15" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'dashboard': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="7" height="7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="14" y="3" width="7" height="7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="3" y="14" width="7" height="7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="14" y="14" width="7" height="7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'logo': f'''<svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 21H21M5 21V7L12 3L19 7V21M9 9V21M9 9H15M15 9V21M9 13H15M9 17H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 7V11M12 11V15M12 11H8M12 11H16" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'crown': f'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5Z" fill="url(#crownGradient)" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="8" cy="12" r="1.5" fill="#dc2626"/>
            <circle cx="12" cy="10" r="1.5" fill="#10b981"/>
            <circle cx="16" cy="12" r="1.5" fill="#dc2626"/>
            <defs>
                <linearGradient id="crownGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#fbbf24;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#f59e0b;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>''',
        'hospital-building': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 21H21M5 21V7L12 3L19 7V21M9 9V21M9 9H15M15 9V21M9 13H15M9 17H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 7V11M12 11V15M12 11H8M12 11H16" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'users-group': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 11C10.6569 11 12 9.65685 12 8C12 6.34315 10.6569 5 9 5C7.34315 5 6 6.34315 6 8C6 9.65685 7.34315 11 9 11Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'alert-warning': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9V13M12 17H12.01M10.29 3.86L1.82 18C1.64538 18.3024 1.55299 18.6453 1.55201 18.9945C1.55103 19.3437 1.64151 19.6871 1.81445 19.9905C1.98738 20.2939 2.23675 20.5467 2.53773 20.7239C2.83871 20.901 3.18082 20.9962 3.53 21H20.47C20.8192 20.9962 21.1613 20.901 21.4623 20.7239C21.7633 20.5467 22.0126 20.2939 22.1856 19.9905C22.3585 19.6871 22.449 19.3437 22.448 18.9945C22.447 18.6453 22.3546 18.3024 22.18 18L13.71 3.86C13.5325 3.56611 13.2805 3.32311 12.9782 3.15448C12.6759 2.98585 12.3336 2.89725 11.985 2.89725C11.6364 2.89725 11.2941 2.98585 10.9918 3.15448C10.6895 3.32311 10.4375 3.56611 10.26 3.86Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 9V13" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <circle cx="12" cy="17" r="0.5" fill="white"/>
        </svg>''',
        'clock': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 6V12L16 14" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'location': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 10C21 17 12 23 12 23C12 23 3 17 3 10C3 5.02944 7.02944 1 12 1C16.9706 1 21 5.02944 21 10Z" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="10" r="3" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'online': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="6" fill="{fill_color}"/>
        </svg>''',
        'hospital-welcome': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 21H21M5 21V7L12 3L19 7V21M9 9V21M9 9H15M15 9V21M9 13H15M9 17H15" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 7V11M12 11V15M12 11H8M12 11H16" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'bell': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 8C18 6.4087 17.3679 4.88258 16.2426 3.75736C15.1174 2.63214 13.5913 2 12 2C10.4087 2 8.88258 2.63214 7.75736 3.75736C6.63214 4.88258 6 6.4087 6 8C6 15 3 17 3 17H21C21 17 18 15 18 8Z" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.73 21C13.5542 21.3031 13.3019 21.5547 12.9982 21.7295C12.6946 21.9044 12.3504 21.9965 12 21.9965C11.6496 21.9965 11.3054 21.9044 11.0018 21.7295C10.6982 21.5547 10.4458 21.3031 10.27 21" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'user-avatar': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="{stroke_color}" stroke-width="2" fill="none"/>
            <circle cx="12" cy="9" r="3" stroke="{stroke_color}" stroke-width="2" fill="none"/>
            <path d="M6 20C6 17 8 15 12 15C16 15 18 17 18 20" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'x-circle': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="{stroke_color}" stroke-width="2" fill="none"/>
            <path d="M15 9L9 15M9 9L15 15" stroke="{stroke_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'medical-cross': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2V8M12 8V14M12 14V22M8 12H2M8 12H14M14 12H22" stroke="{stroke_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="10" stroke="{stroke_color}" stroke-width="2" fill="none"/>
        </svg>''',
        'organization': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>''',
        'smiley': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="{stroke_color}" stroke-width="2" fill="none"/>
            <circle cx="8" cy="10" r="1.5" fill="{fill_color}"/>
            <circle cx="16" cy="10" r="1.5" fill="{fill_color}"/>
            <path d="M8 14C8 14 9.5 16 12 16C14.5 16 16 14 16 14" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
    }
    svg_html = icons.get(icon_name, '')
    if not svg_html:
        return html.Div()
    
    # Dans Dash, on peut utiliser html.Div avec le HTML brut directement
    # Dash va automatiquement échapper le HTML, donc on doit utiliser une approche différente
    # Utilisons html.Iframe avec data URI ou créons le SVG directement
    from dash import dcc
    return html.Div(
        children=[dcc.Markdown(svg_html, dangerously_allow_html=True, mathjax=False)],
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'width': f'{size}px', 'height': f'{size}px'}
    )
