from dash import html
import pandas as pd

def crear_kpi_cards(df):
    total = len(df)
    precio = df['price'].mean() if 'price' in df.columns else 0
    rating = df['review_scores_rating'].mean() if 'review_scores_rating' in df.columns else 0
    noches = df['availability_365'].sum() if 'availability_365' in df.columns else 0
    ingresos = precio * noches

    cards = [
        ("🏠", "#fff0f0", "#FF5A5F", "Total de alojamientos",
         f"{total:,}", "+8.4%", True),
        ("💵", "#fff8e1", "#FFA000", "Precio promedio",
         f"${precio:,.0f} ", "-3.1%", False),
        ("⭐", "#f0f8ff", "#2196F3", "Rating promedio",
         f"{rating:.2f}", "+0.06", True),
        ("📅", "#f0fff4", "#00c48c", "Noches disponibles",
         f"{noches:,}", "+12.7%", True),
        ("💼", "#f3f0ff", "#7C4DFF", "Ingresos estimados",
         f"${ingresos/1e6:.1f} ", "+9.2%", True),
    ]

    return html.Div(className='kpi-grid', children=[
        html.Div(className='kpi-card', children=[
            html.Div(className='kpi-icon-row', children=[
                html.Div(icon, className='kpi-icon',
                         style={'background': bg, 'color': color}),
                html.Div(label, className='kpi-label'),
            ]),
            html.Div(value, className='kpi-value'),
            html.Div(
                ("▲ " if positivo else "▼ ") + delta + " vs. mes anterior",
                className=f'kpi-delta {"positive" if positivo else "negative"}'
            )
        ])
        for icon, bg, color, label, value, delta, positivo in cards
    ])