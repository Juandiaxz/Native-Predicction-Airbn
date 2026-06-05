# pages/anfitriones.py
from dash import html, dcc
import plotly.express as px

def render_anfitriones(df):
    # Agrupación por anfitriones y obtención de su máximo volumen de listings gestionados
    df_hosts = df.groupby(['host_id', 'host_name'])['calculated_host_listings_count'].max().reset_index()
    df_top_hosts = df_hosts.sort_values(by='calculated_host_listings_count', ascending=False).head(10)

    fig_hosts = px.bar(
        df_top_hosts,
        x='calculated_host_listings_count',
        y='host_name',
        orientation='h',
        title="Top 10 Anfitriones por Gestión de Volumen de Propiedades",
        labels={'calculated_host_listings_count': 'Total de Listings Activos', 'host_name': 'Nombre de Anfitrión'},
        color_discrete_sequence=['#00a699']
    )
    fig_hosts.update_layout(template='plotly_white', yaxis={'categoryorder':'total ascending'}, margin=dict(t=40, b=20, l=20, r=20))

    return html.Div([
        html.Div(style={'margin': '14px 0 12px'}, children=[
            html.H2("👤 Análisis Corporativo y Gestión de Anfitriones", className='section-title'),
            html.P("Evaluación de la tasa de profesionalización del mercado: operaciones comerciales vs. economía colaborativa.", className='section-subtitle'),
        ]),
        html.Div(className='charts-grid', children=[
            html.Div(className='chart-card', style={'gridColumn': 'span 2'}, children=[
                dcc.Graph(figure=fig_hosts, config={'displayModeBar': False})
            ])
        ])
    ])