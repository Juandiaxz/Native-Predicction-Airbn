# components/sidebar.py
from dash import html, dcc

def crear_sidebar(current_path="/"):
    """
    Genera la barra lateral de navegación con el logo escalado
    y los estados activos dinámicos para cada pestaña.
    """
    # Definición de rutas e ítems del menú de navegación
    items = [
        ("🏠", "Resumen",        "/"),
        ("💰", "Precios",        "/precios"),
        ("📍", "Ubicaciones",    "/ubicaciones"),
        ("👤", "Anfitriones",    "/anfitriones"),
        ("⭐", "Reseñas",        "/resenas"),
        ("📅", "Disponibilidad", "/disponibilidad"),
        ("📈", "Predicción",     "/prediccion"),
    ]
    
    return html.Div(
        className='sidebar',
        style={
            'width': '240px',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'bottom': 0,
            'padding': '24px 16px',
            'backgroundColor': '#ffffff',
            'borderRight': '1px solid #f0f0f0',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '10px'
        },
        children=[
            # --- CONTENEDOR OPTIMIZADO DEL LOGO ---
            html.Div(
                className='sidebar-logo-area', 
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'flex-start',
                    'padding': '0 8px',
                    'marginBottom': '20px',
                    'height': '60px'
                },
                children=[
                    html.Img(
                        src='/assets/Logo.jpg', 
                        style={
                            'height': '45px',       # Dimensión vertical aumentada para legibilidad
                            'width': 'auto',        # Preserva la relación de aspecto del texto
                            'maxWidth': '100%',     # Restringe desbordamientos
                            'objectFit': 'contain',  # Evita recortes no deseados en el contenedor
                            'flexShrink': '0'       # Bloquea la compresión por flexbox
                        }
                    )
                ]
            ),
            
            # Línea divisoria decorativa
            html.Hr(style={'border': 'none', 'borderTop': '1px solid #f0f0f0', 'margin': '0 0 15px 0'}),
            
            # --- GENERACIÓN DINÁMICA DE ENLACES ---
            * [
                dcc.Link(
                    className=f'sidebar-item {"active" if href == current_path else ""}', 
                    href=href, 
                    children=[
                        html.Span(icon, className='icon', style={'marginRight': '12px'}),
                        label
                    ],
                    style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'padding': '10px 12px',
                        'textDecoration': 'none',
                        'borderRadius': '6px',
                        'color': '#ff5a5f' if href == current_path else '#333333',
                        'backgroundColor': '#fff0f1' if href == current_path else 'transparent',
                        'fontWeight': 'bold' if href == current_path else 'normal'
                    }
                )
                for icon, label, href in items
            ]
        ]
    )