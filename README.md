# trabajo-final-ia

Este proyecto implementa un clasificador de sentimiento (positivo / negativo) aplicado a las reviews de la plataforma de videojuegos Steam, mediante fine-tuning de DistilBERT, un modelo Transformer preentrenado de la biblioteca HuggingFace.

El objetivo del trabajo fue adaptar un modelo de lenguaje general para la tarea específica de clasificación binaria, entrenarlo con datos reales, compararlo con otros modelos y evaluar métricas como accuracy, precision, recall y F1-score.

# Estructura del proyecto
- dataset.py: Permite la obtención y descarga de reviews desde la API de Steam.
- clean.py: Script para filtrar y eliminar las reviews muy cortas o muy largas.
- train.py: Para el entrenamiento (fine-tuning) de DistilBERT.
- predict.py: Permite probar el modelo en el cmd.
- steam_reviews.json: Dataset limpio obtenido.
- steam_apps_cache.json: Dataset con reviews de todos los juegos de steam sin filtrar.
- app.py: Script para ejecutar la aplicación de escritorio.
- const.py: Archivo de configuración que define constantes globales, como rutas de archivos, hiperparámetros del modelo (epochs, learning rate) y límites de validación.
- dataset_manager.py: Clase utilitaria para la gestión de archivos JSON, encargada de guardar y cargar tanto el caché de aplicaciones como los datasets de reviews.
- structs.py: Definiciones de tipos de datos (TypedDict) para estructurar la información de las reviews y las aplicaciones, asegurando consistencia en el manejo de datos.
- workers.py: Implementación de hilos en segundo plano (QObjects) para realizar tareas pesadas (como descargas de la API o procesamiento de datos) sin congelar la interfaz gráfica.
- views/: Carpeta que contiene las ventanas de la interfaz gráfica (MainWindow, SteamAppsWindow).
- tabs/: Carpeta que contiene la lógica y diseño de las pestañas individuales de la aplicación (Dataset, Limpieza, Entrenamiento, Prueba).
- requirements.txt: Lista de dependencias y librerías necesarias para ejecutar el proyecto
