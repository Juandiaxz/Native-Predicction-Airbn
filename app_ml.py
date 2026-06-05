# app_ml.py
import joblib
import pandas as pd
import os
import pickle


def obtener_metadatos_modelo(algoritmo):
    """
    Lee los archivos .pkl de metadatos generados en el entrenamiento
    y retorna un diccionario con las métricas del modelo seleccionado.
    """
    # Mapeo de llaves de la interfaz con los nombres de los archivos físicos
    nombres_archivos = {
        'lineal': 'metadata_lineal.pkl',
        'arbol': 'metadata_arbol.pkl',
        'rf': 'metadata_rf.pkl'
    }
    
    archivo_nombre = nombres_archivos.get(algoritmo)
    if not archivo_nombre or not os.path.exists(archivo_nombre):
        return None
        
    try:
        with open(archivo_nombre, 'rb') as f:
            metadatos = pickle.load(f)
        return metadatos  # Debe contener llaves como: 'r2', 'rmse', o las calculadas en tu pipeline
    except Exception as e:
        print(f"❌ Error al cargar metadatos para {algoritmo}: {e}")
        return None
    

def cargar_modelo(algoritmo):
    """
    Carga el pipeline entrenado desde la carpeta /models
    Formatos: 'lineal', 'arbol', 'rf'
    """
    ruta_modelo = f"models/modelo_{algoritmo}.pkl"
    try:
        pipeline = joblib.load(ruta_modelo)
        return pipeline
    except Exception as e:
        print(f"❌ Error al cargar el modelo {ruta_modelo}: {e}")
        return None

def realizar_prediccion(algoritmo, datos_entrada):
    """
    Recibe el algoritmo seleccionado y un diccionario con los datos del formulario.
    Retorna el precio estimado por el modelo.
    """
    pipeline = cargar_modelo(algoritmo)
    if pipeline is None:
        return None
    
    # Convertir el diccionario de entrada a DataFrame con la estructura exacta del entrenamiento
    df_pred = pd.DataFrame([datos_entrada])
    
    # El pipeline aplica automáticamente el ColumnTransformer (StandardScaler y OneHotEncoder)
    prediccion = pipeline.predict(df_pred)
    return prediccion[0]