# utils/data_processing.py
import pandas as pd
import io
import os

def procesar_y_guardar_csv(contents, filename):
    """
    Recibe los datos en base64 desde el navegador, los convierte a DataFrame,
    los guarda en la carpeta data/ y devuelve el DataFrame limpio.
    """
    import base64
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # 1. Leer el archivo subido
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    # 2. Limpieza básica que ya tenías
    df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')
    df['reviews_per_month'] = df['reviews_per_month'].fillna(0)
    df['last_review'] = df['last_review'].fillna(pd.Timestamp('1900-01-01'))
    
    # 3. Guardar en la carpeta data local
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/data.csv", index=False)
    
    return df