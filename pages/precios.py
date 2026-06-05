# pages/precios.py
from dash import html, dcc
import plotly.express as px

def render_precios(df):
    # Filtrado estadístico para análisis visual claro (excluyendo valores atípicos > $500 USD)
    df_clean = df[df['price'] <= 500]
    
    # 1. Boxplot de distribución de precios por tipo de alojamiento
    fig_box = px.box(
        df_clean,
        x='room_type',
        y='price',
        color='room_type',
        title="Distribución de Precios por Tipo de Habitación (Filtro <= $500 USD)",
        color_discrete_sequence=['#ff5a5f', '#00a699', '#fc642d', '#484848'],
        labels={'room_type': 'Tipo de Habitación', 'price': 'Precio por noche (USD)'}
    )
    fig_box.update_layout(template='plotly_white', showlegend=False, margin=dict(t=40, b=20, l=20, r=20))

    # 2. Gráfico de barras: Precio promedio por Grupo de Vecindarios (Distritos)
    df_bar = df.groupby('neighbourhood_group')['price'].mean().reset_index().sort_values(by='price', ascending=False)
    fig_bar = px.bar(
        df_bar,
        x='neighbourhood_group',
        y='price',
        title="Precio Promedio por Distrito (New York)",
        labels={'neighbourhood_group': 'Distrito', 'price': 'Precio Promedio (USD)'},
        color_discrete_sequence=['#ff5a5f']
    )
    fig_bar.update_layout(template='plotly_white', margin=dict(t=40, b=20, l=20, r=20))

    return html.Div([
        html.Div(style={'margin': '14px 0 12px'}, children=[
            html.H2("💰 Análisis Económico y Estructura de Precios", className='section-title'),
            html.P("Evaluación del impacto del tipo de propiedad y la ubicación geográfica sobre las tarifas de reserva.", className='section-subtitle'),
        ]),
        html.Div(className='charts-grid', children=[
            html.Div(className='chart-card', children=[dcc.Graph(figure=fig_box, config={'displayModeBar': False})]),
            html.Div(className='chart-card', children=[dcc.Graph(figure=fig_bar, config={'displayModeBar': False})])
        ])
    ])