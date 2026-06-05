# app_visualizacion.py
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def cargar_metadatos_modelos():
    """
    Lee los archivos de metadatos (.pkl) generados por el entrenamiento
    y consolida las métricas de rendimiento en un DataFrame.
    """
    algoritmos = ["lineal", "arbol", "rf"]
    metricas = []
    
    for alg in algoritmos:
        ruta = f"models/metadata_{alg}.pkl"
        try:
            meta = joblib.load(ruta)
            metricas.append({
                "Modelo": alg.upper(),
                "R² (Explicación de varianza)": meta.get("r2_test", 0),
                "RMSE (Error medio $)": meta.get("rmse_test", 0)
            })
        except Exception as e:
            print(f"⚠️ No se pudieron cargar los metadatos de {ruta}: {e}")
            
    return pd.DataFrame(metricas)

def generar_grafico_rendimiento():
    """
    Crea un gráfico de barras comparativo en Plotly que contrasta 
    el R² y el RMSE de los tres modelos de Machine Learning.
    """
    df_metrics = cargar_metadatos_modelos()
    
    if df_metrics.empty:
        return go.Figure().update_layout(title="No hay metadatos de modelos disponibles. Entrene los modelos primero.")
    
    # Crear gráfico con doble eje Y o barras agrupadas. Usaremos subplots/barras agrupadas para claridad.
    fig = go.Figure()
    
    # Barra para R²
    fig.add_trace(go.Bar(
        x=df_metrics["Modelo"],
        y=df_metrics["R² (Explicación de varianza)"],
        name="R² Score (Mayor es mejor)",
        marker_color="rgb(31, 119, 180)",
        text=df_metrics["R² (Explicación de varianza)"].apply(lambda x: f"{x:.4f}"),
        textposition='auto'
    ))
    
    # Barra para RMSE
    fig.add_trace(go.Bar(
        x=df_metrics["Modelo"],
        y=df_metrics["RMSE (Error medio $)"],
        name="RMSE (Menor es mejor)",
        marker_color="rgb(214, 39, 40)",
        text=df_metrics["RMSE (Error medio $)"].apply(lambda x: f"${x:,.2f}"),
        textposition='auto',
        yaxis="y2"
    ))
    
    # Configurar el diseño con doble eje Y
    fig.update_layout(
        title="<b>Comparación de Rendimiento de Modelos (Airbnb)</b>",
        xaxis=dict(title="Algoritmos Evaluados"),
        yaxis=dict(title="R² Score", range=[0, 1]),
        yaxis2=dict(title="RMSE ($ USD)", overlaying="y", side="right"),
        barmode="group",
        legend=dict(x=0.01, y=0.99),
        template="plotly_white"
    )
    
    return fig

def generar_graficos_descriptivos(df):
    """
    Genera gráficos estadísticos del dataset de Airbnb para la pestaña de analítica.
    Recibe el DataFrame global cargado en la aplicación.
    """
    if df is None or df.empty:
        return {}
    
    # 1. Distribución de precios por grupo de vecindario (Boxplot)
    fig_precio_barrio = px.box(
        df, 
        x="neighbourhood_group", 
        y="price",
        color="neighbourhood_group",
        title="<b>Distribución de Precios por Grupo de Vecindario</b>",
        labels={"neighbourhood_group": "Vecindario", "price": "Precio ($)"},
        template="plotly_white"
    )
    # Limitar el rango del eje Y para evitar que los outliers (valores extremos) distorsionen el gráfico
    fig_precio_barrio.update_yaxes(range=[0, df["price"].quantile(0.95)])
    
    # 2. Relación entre número de reviews y precio por tipo de cuarto (Scatter)
    fig_reviews_precio = px.scatter(
        df,
        x="number_of_reviews",
        y="price",
        color="room_type",
        title="<b>Relación: Número de Reseñas vs. Precio por Tipo de Habitación</b>",
        labels={"number_of_reviews": "Cantidad de Reseñas", "price": "Precio ($)"},
        opacity=0.6,
        template="plotly_white"
    )
    fig_reviews_precio.update_yaxes(range=[0, df["price"].quantile(0.95)])
    
    return {
        "precio_barrio": fig_precio_barrio,
        "reviews_precio": fig_reviews_precio
    }