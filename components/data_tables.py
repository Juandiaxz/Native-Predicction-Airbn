# components/data_tables.py
from dash import html, dash_table

def crear_tabla_top(df):
    # Validar que el DataFrame no esté vacío
    if df is None or df.empty:
        return html.Div("No hay datos disponibles para mostrar la tabla.")

    # Filtrar u ordenar para la vista previa (Top 5)
    df_top = df.sort_values(by=['number_of_reviews', 'price'], ascending=[False, True]).head(5)
    
    # Columnas mapeadas para la visualización estándar
    columnas = [
        {"name": "Nombre", "id": "name"},
        {"name": "Barrio", "id": "neighbourhood"},
        {"name": "Tipo", "id": "room_type"},
        {"name": "Precio/noche", "id": "price"},
        {"name": "Reviews", "id": "number_of_reviews"},
        {"name": "Disponibilidad", "id": "availability_365"}
    ]

    return html.Div([
        # Contenedor de la tabla pequeña (Fija en el Home)
        html.Div(className='table-container', children=[
            html.Div(className='table-header-row', children=[
                html.Div("Top alojamientos", className='table-title'),
                # Convertimos el texto en un botón interactivo con ID
                html.Button("Ver todos →", id='btn-ver-todos-tabla', className='table-ver-todos')
            ]),
            
            dash_table.DataTable(
                id='tabla-completa-render',
                data=df.to_dict('records'),
                columns=columnas,
                page_size=15,
                
                # --- PROPIEDADES CRÍTICAS PARA FORZAR EL SCROLL HORIZONTAL ---
                style_table={
                    'overflowX': 'auto',        # Habilita el scroll horizontal cuando el contenido exceda el ancho
                    'minWidth': '100%',         # Fuerza a la tabla a ocupar el contenedor
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px 10px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px',
                    'minWidth': '140px',        # Ancho mínimo por defecto para celdas estándar
                    'maxWidth': '300px',        # Evita que columnas gigantes deformen la tabla
                    'whiteSpace': 'normal',     # Permite que el texto largo salte de línea si es necesario
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'borderBottom': '2px solid #dee2e6',
                    'color': '#495057'
                },
                style_data={
                    'borderBottom': '1px solid #f4f4f4',
                    'backgroundColor': 'white'
                },
                
                # Estilo específico para congelar o dar más espacio a la columna del Nombre
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'name'},
                        'minWidth': '280px',    # Le damos más espacio al nombre del alojamiento
                        'maxWidth': '400px',
                    }
                ]
            )
        ]),

        # --- ESTRUCTURA DEL MODAL OCULTO (CONTENEDOR DE TODOS LOS ALOJAMIENTOS) ---
        html.Div(
            id='modal-tabla-completa',
            style={'display': 'none'}, # Oculto por defecto mediante CSS inline
            children=[
                # Fondo oscuro semitransparente
                html.Div(style={
                    'position': 'fixed', 'top': '0', 'left': '0', 'width': '100vw', 'height': '100vh',
                    'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000'
                }, id='modal-overlay'),
                
                # Caja de contenido del Modal
                html.Div(style={
                    'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)',
                    'width': '85%', 'maxHeight': '80vh', 'backgroundColor': 'white', 'borderRadius': '12px',
                    'padding': '24px', 'boxShadow': '0 4px 24px rgba(0,0,0,0.2)', 'zIndex': '1001',
                    'display': 'flex', 'flexDirection': 'column'
                }, children=[
                    html.Div(style={'display': 'flex', 'justifyContent': 'between', 'alignItems': 'center', 'marginBottom': '16px'}, children=[
                        html.H3("Todos los alojamientos disponibles", style={'margin': '0', 'fontSize': '16px', 'fontWeight': '700'}),
                        html.Button("✕ Cerrar", id='btn-cerrar-modal', style={
                            'background': '#FF5A5F', 'color': 'white', 'border': 'none', 
                            'borderRadius': '6px', 'padding': '6px 12px', 'cursor': 'pointer', 'fontWeight': '600'
                        })
                    ]),
                    
                    # Contenedor con Scroll para albergar el dataset completo en DataTable
                    html.Div(style={'overflowY': 'auto', 'flex': '1'}, children=[
                        dash_table.DataTable(
                            id='tabla-completa-render',
                            data=df.to_dict('records'), # Carga el DataFrame completo aquí
                            columns=columnas,
                            page_size=15, # Paginación integrada para optimizar rendimiento de renderizado
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Arial', 'fontSize': '12px'},
                            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
                        )
                    ])
                ])
            ]
        )
    ])