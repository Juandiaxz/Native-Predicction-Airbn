# entrenamiento.py
import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, root_mean_squared_error

def ejecutar_entrenamiento_ia(df):
    """
    Recibe el DataFrame directamente procesado desde el upload de index.py,
    entrena los 3 modelos y actualiza los archivos .pkl en /models.
    """
    # 1. Limpieza rápida de registros nulos en las columnas críticas para el modelo
    df_limpio = df.dropna(subset=['price', 'minimum_nights', 'number_of_reviews', 'availability_365', 'neighbourhood_group', 'room_type'])

    features_num = ["minimum_nights", "number_of_reviews", "availability_365"]
    features_cat = ["neighbourhood_group", "room_type"]
    target = "price"

    X = df_limpio[features_num + features_cat]
    y = df_limpio[target]

    # 2. Partición de datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Transformación de columnas (StandardScaler para numéricas, OneHot para categóricas)
    preprocesador = ColumnTransformer([
        ("num", StandardScaler(), features_num),
        ("cat", OneHotEncoder(drop="first", handle_unknown='ignore'), features_cat)
    ])

    # Definición de los 3 algoritmos solicitados en el taller
    modelos = {
        "lineal": {"instancia": LinearRegression(), "archivo": "models/modelo_lineal.pkl"},
        "arbol": {"instancia": DecisionTreeRegressor(max_depth=6, random_state=42), "archivo": "models/modelo_arbol.pkl"},
        "rf": {"instancia": RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1), "archivo": "models/modelo_rf.pkl"}
    }

    # Asegurar la existencia del directorio de destino
    os.makedirs("models", exist_ok=True)

    # 4. Ciclo automatizado de ajuste y evaluación
    for nombre, config in modelos.items():
        pipeline = Pipeline([
            ("preprocesador", preprocesador),
            ("modelo", config["instancia"])
        ])
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)
        
        # Serialización de los artefactos para su posterior lectura en la página de predicción
        joblib.dump(pipeline, config["archivo"])
        joblib.dump({
            "rmse_test": rmse, 
            "r2_test": r2, 
            "features_num": features_num, 
            "features_cat": features_cat
        }, f"models/metadata_{nombre}.pkl")
        
    print("✅ Entrenamiento completado. Archivos .pkl actualizados dinámicamente.")