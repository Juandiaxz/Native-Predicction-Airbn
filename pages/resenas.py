# pages/resenas.py
from dash import html, dcc
import plotly.express as px

def render_resenas(df):
    # Limpieza de registros para análisis de dispersión correlativa (Precios <= $400 USD)
    df_filtered = df[(df['price'] <= 400) & (df['reviews_per_month'] > 0)]

    fig_scatter = px.scatter(
        df_filtered,
        x="reviews_per_month",
        y="price",
        color="room_type",
        title="Volumen de Reseñas Mensuales en Función de la Tarifa de Alquiler",
        labels={'reviews_per_month': 'Índice de Reseñas Mensuales', 'price': 'Precio por Noche (USD)', 'room_type': 'Tipo de Habitación'},
        color_discrete_sequence=['#ff5a5f', '#00a699', '#fc642d', '#484848']
    )
    fig_scatter.update_layout(template='plotly_white', margin=dict(t=40, b=20, l=20, r=20))

    return html.Div([
        html.Div(style={'margin': '14px 0 12px'}, children=[
            html.H2("⭐ Análisis de Feedback, Interacciones y Reseñas", className='section-title'),
            html.P("Evaluación cualitativa indirecta del flujo de reservas con relación al espectro tarifario establecido.", className='section-subtitle'),
        ]),
        html.Div(className='charts-grid', children=[
            html.Div(className='chart-card', style={'gridColumn': 'span 2'}, children=[
                dcc.Graph(figure=fig_scatter, config={'displayModeBar': False})
            ])
        ])
    ])