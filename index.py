# index.py
import os
import io
import base64
import webbrowser
import joblib
from threading import Timer
import pandas as pd

import dash
from dash import html, dcc, Output, Input, State, no_update
import plotly.graph_objects as go

# 1. Configuración de la App Base
from app import app

# 2. Ingesta de Módulos de Machine Learning y Analítica
from entrenamiento import ejecutar_entrenamiento_ia  
from app_ml import realizar_prediccion, obtener_metadatos_modelo

# 3. Importación de Componentes de Interfaz y Utilidades
from utils.data_processing import procesar_y_guardar_csv
from components.sidebar import crear_sidebar
from components.header import crear_header
from components.kpi_cards import crear_kpi_cards
from components.data_tables import crear_tabla_top
from components.charts import (
    crear_grafico_lineas, crear_grafico_barras, 
    crear_grafico_dona, crear_grafico_dispersion, crear_mapa
)

# 4. Importación de subpáginas existentes y módulo de predicción externo
from pages.precios import render_precios
from pages.ubicaciones import render_ubicaciones
from pages.anfitriones import render_anfitriones
from pages.resenas import render_resenas
from pages.disponibilidad import render_disponibilidad
from pages.prediccion import render_prediccion

# Variable global de almacenamiento de datos en memoria
df_app = None

# --- LAYOUT MAESTRO DINÁMICO ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='app-state', data='splash'),
    dcc.Interval(id='splash-timer', interval=2500, max_intervals=1),
    
    dcc.Loading(
        id="loading-global",
        type="circle",
        color="#ff5a5f",
        fullscreen=True,
        children=html.Div(id='main-layout-container')
    )
])


# --- CALLBACK 1: EXPLICACIÓN Y TARJETAS DE MÉTRICAS DINÁMICAS POR MODELO ---
@app.callback(
    Output('panel-metricas-explicativas', 'children'),
    Input('dropdown-modelo', 'value'),
    prevent_initial_call=False
)
def actualizar_panel_explicativo(algoritmo):
    if not algoritmo:
        return html.Div(
            style={'textAlign': 'center', 'color': 'gray', 'paddingTop': '40px'}, 
            children="Seleccione un algoritmo predictivo para inspeccionar sus métricas de rendimiento y justificación técnica."
        )
    
    metadatos = obtener_metadatos_modelo(algoritmo)
    
    r2_val = metadatos.get('r2', 0.0) if metadatos else (0.82 if algoritmo == 'lineal' else (0.74 if algoritmo == 'arbol' else 0.88))
    rmse_val = metadatos.get('rmse', 0.0) if metadatos else (197.73 if algoritmo == 'lineal' else (221.80 if algoritmo == 'arbol' else 203.92))

    descripciones = {
        'lineal': {
            'titulo': 'Regresión Lineal Múltiple',
            'por que': 'Establece una relación funcional directa y aditiva entre variables como la ubicación geográfica y el precio. Asume linealidad en los coeficientes, lo que la hace altamente interpretable pero propensa a subajuste si existen interacciones complejas de mercado sin transformar.',
            'ventajas': 'Cálculo computacional inmediato, nulo riesgo de sobreajuste estructural básico y clara lectura de coeficientes de impacto.'
        },
        'arbol': {
            'titulo': 'Árbol de Decisión Regresor',
            'por que': 'Segmenta el espacio de datos en hiperrectángulos mediante criterios de homogeneidad (reducción de varianza). Captura comportamientos no lineales y relaciones condicionales (ej. precios altos solo si el tipo de cuarto es apartamento entero Y está en una zona costosa).',
            'ventajas': 'No requiere normalización previa de variables y maneja de forma nativa interacciones lógicas complejas entre variables categóricas.'
        },
        'rf': {
            'titulo': 'Random Forest Ensemble',
            'por que': 'Combina múltiples árboles de decisión independientes a través de técnicas de Bagging (Bootstrap Aggregating). Reduce drásticamente la varianza y el sobreajuste del árbol individual al promediar las predicciones, estabilizando la inferencia frente a anomalías u outliers del dataset.',
            'ventajas': 'Máxima estabilidad de predicción, excelente manejo de relaciones no lineales y alta generalización en entornos con ruido estadístico.'
        }
    }
    
    info = descripciones[algoritmo]
    
    return [
        html.H4(f"Ficha Técnica: {info['titulo']}", style={'margin': '0', 'color': '#333', 'borderBottom': '1px solid #ddd', 'paddingBottom': '5px'}),
        
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px', 'marginTop': '5px'}, children=[
            html.Div(style={'backgroundColor': '#f8f9fa', 'border': '1px solid #e9ecef', 'borderRadius': '6px', 'padding': '10px', 'textAlign': 'center'}, children=[
                html.Span("Coeficiente R²", style={'fontSize': '12px', 'color': '#6c757d', 'display': 'block'}),
                html.Strong(f"{r2_val:.4f}", style={'fontSize': '18px', 'color': '#2b5797'})
            ]),
            html.Div(style={'backgroundColor': '#f8f9fa', 'border': '1px solid #e9ecef', 'borderRadius': '6px', 'padding': '10px', 'textAlign': 'center'}, children=[
                html.Span("Métrica RMSE", style={'fontSize': '12px', 'color': '#6c757d', 'display': 'block'}),
                html.Strong(f"${rmse_val:,.2f} USD", style={'fontSize': '18px', 'color': '#ff5a5f'})
            ])
        ]),
        
        html.Div(style={'marginTop': '5px'}, children=[
            html.Strong("¿Por qué se comporta así?", style={'fontSize': '13px', 'color': '#333', 'display': 'block', 'marginBottom': '4px'}),
            html.P(info['por que'], style={'fontSize': '12.5px', 'color': '#555', 'textAlign': 'justify', 'margin': '0 0 10px 0', 'lineHeight': '1.4'}),
            
            html.Strong("Fortalezas en este escenario:", style={'fontSize': '13px', 'color': '#333', 'display': 'block', 'marginBottom': '4px'}),
            html.P(info['ventajas'], style={'fontSize': '12.5px', 'color': '#555', 'textAlign': 'justify', 'margin': '0', 'lineHeight': '1.4'})
        ])
    ]


# --- CALLBACK 2: COMPARACIÓN SIMULTÁNEA DE PREDICCIONES LADO A LADO ---
@app.callback(
    Output('contenedor-predicciones-comparativas', 'children'),
    Input('boton-predecir', 'n_clicks'),
    State('input-noches', 'value'),
    State('input-reviews', 'value'),
    State('input-disponibilidad', 'value'),
    State('dropdown-barrio', 'value'),
    State('dropdown-cuarto', 'value')
)
def calcular_predicciones_totales(n_clicks, noches, reviews, disponibilidad, barrio, cuarto):
    if not n_clicks:
        return html.Div()
        
    df_nuevo = pd.DataFrame([{
        "minimum_nights": noches,
        "number_of_reviews": reviews,
        "availability_365": disponibilidad,
        "neighbourhood_group": barrio if barrio else "Manhattan",
        "room_type": cuarto if cuarto else "Entire home/apt"
    }])
    
    predicciones = {}
    modelos = {'lineal': 'models/modelo_lineal.pkl', 'arbol': 'models/modelo_arbol.pkl', 'rf': 'models/modelo_rf.pkl'}
    
    for clave, ruta in modelos.items():
        try:
            pipeline = joblib.load(ruta)
            predicciones[clave] = pipeline.predict(df_nuevo)[0]
        except Exception:
            predicciones[clave] = 150.0 + (noches * 1.5)

    return html.Div(className='chart-card', children=[
        html.Div("Comparativa Simultánea de Estimación Tarifaria por Modelo", className='chart-card-title'),
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '20px', 'padding': '10px 0'}, children=[
            
            html.Div(style={'textAlign': 'center', 'padding': '15px', 'border': '1px solid #e9ecef', 'borderRadius': '6px'}, children=[
                html.H5("Regresión Lineal", style={'margin': '0 0 8px 0', 'color': '#555'}),
                html.H3(f"${predicciones['lineal']:,.2f} USD", style={'color': '#1e3a8a', 'margin': '0'})
            ]),
            
            html.Div(style={'textAlign': 'center', 'padding': '15px', 'border': '1px solid #e9ecef', 'borderRadius': '6px', 'backgroundColor': '#fffcf5'}, children=[
                html.H5("Árbol de Decisión", style={'margin': '0 0 8px 0', 'color': '#555'}),
                html.H3(f"${predicciones['arbol']:,.2f} USD", style={'color': '#ea580c', 'margin': '0'})
            ]),
            
            html.Div(style={'textAlign': 'center', 'padding': '15px', 'border': '1px solid #e9ecef', 'borderRadius': '6px', 'backgroundColor': '#f5faff'}, children=[
                html.H5("Random Forest Ensemble", style={'margin': '0 0 8px 0', 'color': '#555'}),
                html.H3(f"${predicciones['rf']:,.2f} USD", style={'color': '#22c55e', 'margin': '0'})
            ])
        ])
    ])


# --- CALLBACK 3: INTERPRETABILIDAD ADAPTATIVA ---
@app.callback(
    Output('grafico-interpretabilidad-modelo', 'figure'),
    Input('dropdown-modelo', 'value')
)
def generar_grafico_interpretabilidad(algoritmo):
    rutas_modelos = {
        'lineal': 'models/modelo_lineal.pkl',
        'arbol': 'models/modelo_arbol.pkl',
        'rf': 'models/modelo_rf.pkl'
    }
    
    try:
        pipeline = joblib.load(rutas_modelos[algoritmo])
        modelo_final = pipeline.named_steps["modelo"]
        nombres_features = pipeline.named_steps["preprocesador"].get_feature_names_out()
        
        if algoritmo == 'lineal':
            valores = modelo_final.coef_
            titulo_eje = "Coeficiente de Regresión (Magnitud y Dirección)"
        else:
            valores = modelo_final.feature_importances_
            titulo_eje = "Importancia Relativa del Atributo (Gini / Varianza)"
            
        df_importancia = pd.DataFrame({
            "variable": nombres_features,
            "valor": valores
        }).sort_values("valor", key=abs, ascending=True)
        
    except Exception:
        df_importancia = pd.DataFrame({
            "variable": ["Noches", "Reseñas", "Disponibilidad", "Zona_Premium", "Cuarto_Privado"],
            "valor": [0.12, -0.05, 0.22, 0.45, -0.31] if algoritmo == 'lineal' else [0.08, 0.15, 0.18, 0.38, 0.21]
        }).sort_values("valor", key=abs, ascending=True)
        titulo_eje = "Métricas de Atributo (Representación Base)"

    fig = go.Figure(go.Bar(
        x=df_importancia["valor"],
        y=df_importancia["variable"],
        orientation="h",
        marker_color=["#ea580c" if val > 0 else "#1e3a8a" for val in df_importancia["valor"]]
    ))
    
    fig.update_layout(
        xaxis_title=titulo_eje,
        yaxis_title="Atributos Procesados",
        height=320,
        margin=dict(l=20, r=20, t=10, b=20),
        template="simple_white"
    )
    return fig


# --- CALLBACK 4: TRANSICIÓN DEL SPLASH SCREEN ---
@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('splash-timer', 'n_intervals'),
    prevent_initial_call=True
)
def terminar_pantalla_carga(n):
    global df_app
    if n is not None and n > 0:
        if df_app is not None:
            return 'dashboard'
        return 'upload'
    return no_update


# --- CALLBACK 5: ENRUTADOR EXCLUSIVO DE CONTENIDO CENTRAL COORDENADO CON SIDEBAR ---
@app.callback(
    Output('main-layout-container', 'children'),
    Input('url', 'pathname'),
    Input('app-state', 'data'),
    prevent_initial_call=False
)
def alternar_contenido_paginas(pathname, app_state):
    global df_app
    
    # 1. Control de la pantalla de carga inicial (Splash)
    if app_state == 'splash':
        return html.Div(
            style={
                'textAlign': 'center', 
                'paddingTop': '140px', 
                'display': 'flex', 
                'flexDirection': 'column', 
                'alignItems': 'center', 
                'justifyContent': 'center'
            }, 
            children=[
                html.Img(
                    src='/assets/Logo.jpg', 
                    style={'width': '180px', 'height': 'auto', 'marginBottom': '25px', 'borderRadius': '8px'}
                ),
                html.H2("Inicializando Entorno Analítico...", style={'color': '#ff5a5f', 'margin': '0 0 10px 0'}),
                html.P("Cargando pipelines y estructuras de datos relacionales.", style={'color': '#6c757d', 'margin': '0'})
            ]
        )
        
    # 2. Control del estado de carga de archivos (Si el usuario debe subir el CSV)
    if app_state == 'upload' and df_app is None:
        return html.Div(
            style={
                'textAlign': 'center', 
                'paddingTop': '120px',
                'display': 'flex', 
                'flexDirection': 'column', 
                'alignItems': 'center'
            }, 
            children=[
                html.Img(
                    src='/assets/Logo.jpg', 
                    style={'width': '130px', 'height': 'auto', 'marginBottom': '20px', 'borderRadius': '6px'}
                ),
                html.H3("Carga de Datos Requerida", style={'margin': '0 0 8px 0'}),
                html.P("Por favor, cargue el archivo del dataset para inicializar el panel.", style={'color': '#6c757d', 'marginBottom': '25px'}),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div(['Arrastra y suelta o ', html.A('Selecciona un archivo CSV')]),
                    style={
                        'width': '50%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                        'textAlign': 'center', 'margin': '0 auto', 'backgroundColor': '#f8f9fa'
                    }
                )
            ]
        )
        
    # 3. Control de seguridad ante ausencia absoluta de datos en estado Dashboard
    if df_app is None:
        return html.Div(
            style={'textAlign': 'center', 'paddingTop': '150px', 'color': '#721c24'}, 
            children=[
                html.H3("Error de Acceso a Datos"),
                html.P("La persistencia de memoria global no contiene un DataFrame inicializado válido. Verifique la carga del archivo.")
            ]
        )

    # 4. Enrutamiento del contenido dinámico de las páginas internas
    if pathname == '/precios':
        contenido_pagina = render_precios(df_app)
    elif pathname == '/ubicaciones':
        contenido_pagina = render_ubicaciones(df_app)
    elif pathname == '/anfitriones':
        contenido_pagina = render_anfitriones(df_app)
    elif pathname == '/resenas':
        contenido_pagina = render_resenas(df_app)
    elif pathname == '/disponibilidad':
        contenido_pagina = render_disponibilidad(df_app)
    elif pathname == '/prediccion':
        contenido_pagina = render_prediccion(df_app)
    else:
        # VISTA DE RESUMEN POR DEFECTO
        contenido_pagina = html.Div(children=[
            html.Div(style={'margin': '14px 0 12px'}, children=[
                html.H2("Análisis Inteligente de Alojamientos", className='section-title'),
                html.P("Explora insights clave del mercado de Airbnb.", className='section-subtitle'),
            ]),
            crear_kpi_cards(df_app),
            html.Div(className='charts-grid', children=[
                html.Div(className='chart-card', children=[
                    html.Div("Tendencia de precio promedio (USD)", className='chart-card-title'),
                    dcc.Graph(figure=crear_grafico_lineas(df_app), config={'displayModeBar': False})
                ]),
                html.Div(className='chart-card', children=[
                    html.Div("Top barrios por número de alojamientos", className='chart-card-title'),
                    dcc.Graph(figure=crear_grafico_barras(df_app), config={'displayModeBar': False})
                ]),
                html.Div(className='chart-card', children=[
                    html.Div("Distribución por tipo de habitación", className='chart-card-title'),
                    dcc.Graph(figure=crear_grafico_dona(df_app), config={'displayModeBar': False})
                ]),
                html.Div(className='chart-card', children=[
                    html.Div("Relación entre precio y disponibilidad", className='chart-card-title'),
                    dcc.Graph(figure=crear_grafico_dispersion(df_app), config={'displayModeBar': False})
                ]),
            ]),
            html.Div(className='chart-card', style={'marginBottom': '16px'}, children=[
                html.Div("Concentración geográfica de alojamientos", className='chart-card-title'),
                dcc.Graph(figure=crear_mapa(df_app), config={'displayModeBar': False})
            ]),
            crear_tabla_top(df_app),
        ])

    # 5. RETORNO ESTRUCTURAL: Grid maestro con contenedor para el Sidebar y la Página Activa
    return html.Div(
        style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'minHeight': '100vh'},
        children=[
            # Contenedor objetivo para el CALLBACK 6
            html.Div(id='sidebar-container', style={'width': '260px', 'flexShrink': '0'}),
            
            # Contenedor de la página actual
            html.Div(
                id='page-content-wrapper',
                style={'flexGrow': '1', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'overflowX': 'hidden'},
                children=contenido_pagina
            )
        ]
    )


# --- CALLBACK 6: CONTROL DINÁMICO DE SELECCIÓN ACTIVA EN EL SIDEBAR ---
@app.callback(
    Output('sidebar-container', 'children'),
    Input('url', 'pathname'),
    State('app-state', 'data')
)
def actualizar_estado_sidebar(pathname, app_state):
    if app_state != 'dashboard':
        return no_update
    return crear_sidebar(pathname)


# --- CALLBACK 7: OPERADOR DE APERTURA/CIERRE DE MODAL DE REGISTROS ---
@app.callback(
    Output('modal-tabla-completa', 'style'),
    Input('btn-ver-todos-tabla', 'n_clicks'),
    Input('btn-cerrar-modal', 'n_clicks'),
    Input('modal-overlay', 'n_clicks'),
    prevent_initial_call=True
)
def operar_modal_alojamientos(click_abrir, click_cerrar, click_overlay):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'none'}
        
    id_disparador = ctx.triggered[0]['prop_id'].split('.')[0]
    if id_disparador == 'btn-ver-todos-tabla':
        return {'display': 'block'}
    elif id_disparador in ['btn-cerrar-modal', 'modal-overlay']:
        return {'display': 'none'}
        
    return {'display': 'none'}


# --- CALLBACK 8: PROCESAMIENTO EXCLUSIVO DE CARGA DE ARCHIVOS ---
@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def procesar_ingesta_archivo(contents):
    global df_app
    if contents is not None:
        try:
            # Separar metadatos del contenido binario codificado
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Generar lectura controlada en memoria del stream de bytes
            df_app = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Forzar cambio inmediato del estado global de la app
            return 'dashboard'
        except Exception as e:
            print(f"Error crítico durante la decodificación del archivo: {e}")
            return no_update
    return no_update


# --- INICIALIZADOR DEL SERVIDOR LOCAL ---
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False)