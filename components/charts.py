import plotly.express as px
import plotly.graph_objects as go

AIRBNB_COLOR  = '#FF5A5F'
PALETTE       = ['#FF5A5F','#FC642D','#00A699','#484848','#767676']
TEMPLATE      = 'plotly_white'
CHART_HEIGHT  = 260   # altura uniforme para todos los gráficos pequeños
MAP_HEIGHT    = 420   # altura del mapa

def _base_layout(fig, title='', subtitle=''):
    fig.update_layout(
        template=TEMPLATE,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Arial', size=11, color='#555'),
        margin=dict(l=10, r=10, t=36, b=10),
        height=CHART_HEIGHT,
        title=dict(text=title, font=dict(size=13, color='#222'), x=0, pad=dict(l=4)),
        showlegend=True,
        legend=dict(font=dict(size=10), bgcolor='rgba(0,0,0,0)',
                    orientation='v', x=1, y=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0',
                     zeroline=False, tickfont=dict(size=10))
    return fig


def crear_grafico_lineas(df):
    col_fecha = None
    for c in ['last_review','host_since','date']:
        if c in df.columns:
            col_fecha = c
            break

    if col_fecha:
        df = df.copy()
        df[col_fecha] = df[col_fecha].astype(str).str[:7]   # YYYY-MM
        price_month = (df.groupby(col_fecha)['price']
                         .mean().reset_index()
                         .sort_values(col_fecha).tail(18))
        fig = px.line(price_month, x=col_fecha, y='price',
                      color_discrete_sequence=[AIRBNB_COLOR],
                      labels={col_fecha:'', 'price':'Precio (MXN)'})
    else:
        fig = go.Figure()

    fig = _base_layout(fig, 'Tendencia de precio promedio (MXN)')
    fig.update_traces(line=dict(width=2.5), mode='lines+markers',
                      marker=dict(size=5))
    return fig


def crear_grafico_barras(df):
    col_barrio = next((c for c in ['neighbourhood','neighbourhood_cleansed',
                                    'neighbourhood_group'] if c in df.columns), None)
    if col_barrio:
        top = df[col_barrio].value_counts().nlargest(7).reset_index()
        top.columns = ['barrio', 'cantidad']
        fig = px.bar(top, x='cantidad', y='barrio', orientation='h',
                     color_discrete_sequence=[AIRBNB_COLOR],
                     labels={'cantidad':'', 'barrio':''})
        fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    else:
        fig = go.Figure()

    fig = _base_layout(fig, 'Top barrios por número de alojamientos')
    fig.update_traces(marker_cornerradius=4)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    return fig


def crear_grafico_dona(df):
    if 'room_type' in df.columns:
        dist = df['room_type'].value_counts()
        fig = px.pie(names=dist.index, values=dist.values,
                     hole=0.55,
                     color_discrete_sequence=PALETTE)
        fig.update_traces(textposition='outside', textfont_size=10,
                          marker=dict(line=dict(color='white', width=2)))
    else:
        fig = go.Figure()

    fig = _base_layout(fig, 'Distribución por tipo de habitación')
    fig.update_layout(
        legend=dict(orientation='v', x=1, y=0.5,
                    font=dict(size=10)),
        margin=dict(l=10, r=100, t=36, b=10),
    )
    return fig


def crear_grafico_dispersion(df):
    col_y = 'review_scores_rating' if 'review_scores_rating' in df.columns else 'reviews_per_month'
    col_color = 'room_type' if 'room_type' in df.columns else None

    df_plot = df[df['price'] < df['price'].quantile(0.97)].copy()   # quita outliers extremos

    if col_color:
        fig = px.scatter(df_plot, x='price', y=col_y,
                         color=col_color,
                         color_discrete_sequence=PALETTE,
                         labels={'price':'Precio (MXN)', col_y:'Rating'},
                         opacity=0.55)
    else:
        fig = px.scatter(df_plot, x='price', y=col_y,
                         color_discrete_sequence=[AIRBNB_COLOR],
                         opacity=0.55)

    fig = _base_layout(fig, 'Relación entre precio y rating')
    fig.update_traces(marker=dict(size=4))

    # línea de tendencia manual
    import numpy as np
    mask = df_plot[col_y].notna() & df_plot['price'].notna()
    if mask.sum() > 10:
        x = df_plot.loc[mask, 'price'].values
        y = df_plot.loc[mask, col_y].values
        m, b = np.polyfit(x, y, 1)
        x_line = [x.min(), x.max()]
        y_line = [m*xi + b for xi in x_line]
        fig.add_trace(go.Scatter(x=x_line, y=y_line,
                                 mode='lines',
                                 line=dict(color='#484848', width=1.5, dash='dash'),
                                 showlegend=False))
    return fig


def crear_mapa(df):
    col_lat = next((c for c in ['latitude','lat'] if c in df.columns), None)
    col_lon = next((c for c in ['longitude','lon','lng'] if c in df.columns), None)

    if col_lat and col_lon:
        center_lat = df[col_lat].median()
        center_lon = df[col_lon].median()
        fig = px.density_mapbox(
            df, lat=col_lat, lon=col_lon, z='price',
            radius=10,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=10,
            mapbox_style='open-street-map',
            color_continuous_scale='RdYlGn_r',
        )
    else:
        fig = go.Figure()

    fig.update_layout(
        template=TEMPLATE,
        paper_bgcolor='white',
        height=MAP_HEIGHT,
        margin=dict(l=0, r=0, t=36, b=0),
        title=dict(text='Concentración de alojamientos',
                   font=dict(size=13, color='#222'), x=0),
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(thickness=10, len=0.6,
                                tickfont=dict(size=9)),
    )
    return fig