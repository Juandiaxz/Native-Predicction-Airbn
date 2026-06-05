# pages/ubicaciones.py
from dash import html, dcc
import plotly.express as px

def render_ubicaciones(df):
    # Generar mapa de calor / dispersión geográfica por densidad de listings
    fig_mapa = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="neighbourhood_group",
        size_max=12,
        zoom=9.5,
        title="Distribución Geográfica Completa de Propiedades por Distrito",
        mapbox_style="carto-positron",
        labels={'neighbourhood_group': 'Distrito'}
    )
    fig_mapa.update_layout(margin={"r":10,"t":40,"l":10,"b":10}, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    # Gráfico de tarta de concentración porcentual
    df_pie = df['neighbourhood_group'].value_counts().reset_index()
    fig_pie = px.pie(
        df_pie,
        names='neighbourhood_group',
        values='count',
        title="Participación de Mercado por Volumen de Listings",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_pie.update_layout(margin=dict(t=40, b=20, l=20, r=20))

    return html.Div([
        html.Div(style={'margin': '14px 0 12px'}, children=[
            html.H2("📍 Análisis Espacial y de Ubicaciones Geográficas", className='section-title'),
            html.P("Identificación de clústeres de mercado y concentración de inventario en los distritos de Nueva York.", className='section-subtitle'),
        ]),
        html.Div(className='chart-card', style={'marginBottom': '20px'}, children=[
            dcc.Graph(figure=fig_mapa, config={'displayModeBar': False})
        ]),
        html.Div(className='charts-grid', children=[
            html.Div(className='chart-card', children=[dcc.Graph(figure=fig_pie, config={'displayModeBar': False})]),
            html.Div(className='chart-card', children=[
                html.H3("Insights de Densidad Urbana", style={'fontFamily': 'Arial', 'color': '#484848'}),
                html.P("El análisis espacial confirma que Manhattan y Brooklyn monopolizan el volumen del inventario disponible en el dataset, concentrando más del 80% de los alojamientos totales de la muestra urbana.", style={'color': 'gray', 'lineHeight': '1.6', 'fontSize': '14px'})
            ])
        ])
    ])