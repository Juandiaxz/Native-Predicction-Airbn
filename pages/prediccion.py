# pages/prediccion.py
from dash import html, dcc
from app_visualizacion import generar_grafico_rendimiento, generar_graficos_descriptivos

def render_prediccion(df_app):
    """
    Genera el layout visual para la pestaña de predicción, simulación de tarifas
    y analítica explicativa de los modelos de IA basándose en la guía del taller.
    """
    if df_app is None or df_app.empty:
        return html.Div("⚠️ Error de datos: No hay un dataset válido cargado para el análisis predictivo.")

    # Generación de gráficos e información base compartida
    graficos_base = generar_graficos_descriptivos(df_app)
    grafico_modelos = generar_grafico_rendimiento()

    # Extracción de categorías únicas reales del dataset para los Dropdowns
    barrios_unicos = sorted(df_app['neighbourhood_group'].dropna().unique())
    cuartos_unicos = sorted(df_app['room_type'].dropna().unique())

    return html.Div([
        html.H2("📈 Módulo de Predicción Avanzada con Inteligencia Artificial", className='section-title'),
        html.P("Compare la precisión de los algoritmos y simule tarifas óptimas por noche.", className='section-subtitle'),
        
        # BLOQUE 1: Rendimiento Comparativo General de la Carpeta Models
        html.Div(className='chart-card', style={'marginBottom': '25px'}, children=[
            html.Div("Evaluación Cruzada de Modelos Ajustados (Fase de Test)", className='chart-card-title'),
            dcc.Graph(figure=grafico_modelos, config={'displayModeBar': False})
        ]),
        
        # BLOQUE 2: Formulario de Inferencia y Panel de Calidad del Modelo Seleccionado
        html.Div(className='chart-card', style={'marginBottom': '25px'}, children=[
            html.Div("Simulador de Tarifas e Información del Modelo Seleccionado", className='chart-card-title'),
            
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1.2fr 0.8fr', 'gap': '25px', 'padding': '15px 0'}, children=[
                
                # Columna Izquierda: Entradas del Formulario de Simulación
                html.Div([
                    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
                        html.Div([
                            html.Label("Algoritmo Predictivo Principal:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(id='dropdown-modelo', options=[
                                {'label': 'Regresión Lineal Múltiple', 'value': 'lineal'},
                                {'label': 'Árbol de Decisión Regresor', 'value': 'arbol'},
                                {'label': 'Random Forest Ensemble', 'value': 'rf'}
                            ], value='lineal', clearable=False),
                            
                            html.Label("Noches Mínimas de Estadía:", style={'marginTop': '12px', 'display': 'block', 'fontWeight': 'bold'}),
                            dcc.Input(id='input-noches', type='number', min=1, value=1, className='input-style', style={'width': '100%'}),
                            
                            html.Label("Número de Reseñas Acumuladas:", style={'marginTop': '12px', 'display': 'block', 'fontWeight': 'bold'}),
                            dcc.Input(id='input-reviews', type='number', min=0, value=10, className='input-style', style={'width': '100%'})
                        ]),
                        html.Div([
                            html.Label("Disponibilidad Anual (Días al año):", style={'fontWeight': 'bold'}),
                            dcc.Input(id='input-disponibilidad', type='number', min=0, max=365, value=180, className='input-style', style={'width': '100%'}),
                            
                            html.Label("Grupo de Vecindario:", style={'marginTop': '12px', 'display': 'block', 'fontWeight': 'bold'}),
                            dcc.Dropdown(id='dropdown-barrio', options=[{'label': b, 'value': b} for b in barrios_unicos], placeholder="Seleccione zona"),
                            
                            html.Label("Tipo de Habitación / Alojamiento:", style={'marginTop': '12px', 'display': 'block', 'fontWeight': 'bold'}),
                            dcc.Dropdown(id='dropdown-cuarto', options=[{'label': c, 'value': c} for c in cuartos_unicos], placeholder="Seleccione tipo de espacio")
                        ])
                    ]),
                    
                    # Acción de Inferencia
                    html.Div(style={'textAlign': 'center', 'marginTop': '25px'}, children=[
                        html.Button(
                            "🔮 Ejecutar Predicción Óptima", 
                            id='boton-predecir', 
                            className='btn-style', 
                            style={
                                'padding': '12px 35px', 'backgroundColor': '#ff5a5f', 'color': 'white', 
                                'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer',
                                'fontSize': '16px', 'fontWeight': 'bold'
                            }
                        )
                    ])
                ]),
                
                # Columna Derecha: Tarjetas de Métricas dinámicas desde metadatos (.pkl)
                html.Div(id='panel-metricas-explicativas', style={
                    'borderLeft': '2px solid #f0f0f0', 'paddingLeft': '20px', 'display': 'flex', 'flexDirection': 'column', 'gap': '15px'
                })
                
            ])
        ]),

        # BLOQUE 3: Comparación simultánea lado a lado de los 3 modelos (Requerimiento Taller)
        html.Div(id='contenedor-predicciones-comparativas', style={'marginBottom': '25px'}),

        # BLOQUE 4: Gráficos de interpretabilidad e importancia de variables del modelo activo
        html.Div(className='chart-card', style={'marginBottom': '25px'}, children=[
            html.Div("Análisis de Interpretabilidad (Importancia de Variables / Coeficientes)", className='chart-card-title'),
            dcc.Graph(id='grafico-interpretabilidad-modelo', config={'displayModeBar': False})
        ]),
        
        # BLOQUE 5: Análisis Exploratorio Relacionado
        html.Div(className='charts-grid', children=[
            html.Div(className='chart-card', children=[
                html.Div("Rango Estadístico de Tarifas por Zona", className='chart-card-title'),
                dcc.Graph(figure=graficos_base.get("precio_barrio"), config={'displayModeBar': False})
            ]),
            html.Div(className='chart-card', children=[
                html.Div("Densidad de Demanda vs Elasticidad de Precio", className='chart-card-title'),
                dcc.Graph(figure=graficos_base.get("reviews_precio"), config={'displayModeBar': False})
            ])
        ])
    ])