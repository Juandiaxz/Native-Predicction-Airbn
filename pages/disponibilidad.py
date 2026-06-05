# pages/disponibilidad.py
from dash import html, dcc
import plotly.express as px

def render_disponibilidad(df):
    # 1. Histograma de disponibilidad anual agregada
    fig_hist = px.histogram(
        df,
        x="availability_365",
        color="room_type",
        nbins=40,
        title="Distribución de Disponibilidad Operativa Anual (Días)",
        labels={'availability_365': 'Días Disponibles al Año', 'count': 'Frecuencia de Alojamientos', 'room_type': 'Tipo de Habitación'},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_hist.update_layout(template='plotly_white', barmode='stack', margin=dict(t=40, b=20, l=20, r=20))

    return html.Div([
        html.Div(style={'margin': '14px 0 12px'}, children=[
            html.H2("📅 Análisis Operativo de Disponibilidad e Inventario", className='section-title'),
            html.P("Estudio logístico de la retención de propiedades y su exposición anual activa en la plataforma.", className='section-subtitle'),
        ]),
        html.Div(className='charts-grid', children=[
            html.Div(className='chart-card', style={'gridColumn': 'span 2'}, children=[
                dcc.Graph(figure=fig_hist, config={'displayModeBar': False})
            ])
        ])
    ])