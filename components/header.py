# components/header.py
from dash import html

def crear_header():
    return html.Div(className='header-container', children=[
        html.Div("Dashboard Global", className='header-title'),
        html.Div(className='header-actions', children=[
            # Volvemos a dejarlo como un div estático sin IDs ni lógica reactiva
           
            
        ])
    ])