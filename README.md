# trabajo-final-ia

Este proyecto implementa un clasificador de sentimiento (positivo / negativo) aplicado a las reviews de la plataforma de videojuegos Steam, mediante fine-tuning de DistilBERT, un modelo Transformer preentrenado de la biblioteca HuggingFace.

El objetivo del trabajo fue adaptar un modelo de lenguaje general para la tarea específica de clasificación binaria, entrenarlo con datos reales, compararlo con otros modelos y evaluar métricas como accuracy, precision, recall y F1-score.

# Estructura del proyecto
- dataset.py: permite la obtención y descarga de reviews desde la API de Steam
- clean.py: script para filtrar y eliminar las reviews muy cortas o muy largas
- train.py: para el entrenamiento (fine-tuning) de DistilBERT
- predict.py: permite probar el modelo en el cmd
- steam_reviews.json: dataset limpio obtenido
- steam_apps_cache.json: dataset con reviews de todos los juegos de steam sin filtrar
- app.py: script para ejecutar la aplicación de escritorio
- const.py:
- dataset_manager.py:
- structs.py:
- workers.py:
