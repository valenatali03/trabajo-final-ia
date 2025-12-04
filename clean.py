import os
import json
from structs import Dataset
from const import MAX_WORDS, MIN_WORDS


# --- Constantes y Estructuras de Datos ---
ARCHIVO_DATASET = "steam_reviews.json"

# ----------------------------------------
# --- Lógica de Limpieza ---
# ----------------------------------------

def limpiar_reviews_por_longitud(dataset: Dataset, min_words, max_words) -> Dataset:
    """
    Filtra el dataset para eliminar reviews que contienen:
    1. Solo una palabra.
    2. Más de MAX_WORDS (20) palabras.
    """
    reviews_iniciales = len(dataset)
    reviews_conservadas: Dataset = []
    reviews_eliminadas_min = 0
    reviews_eliminadas_max = 0

    print(f"Iniciando limpieza. Total de reviews iniciales: {reviews_iniciales}")
    print(f"Criterio: Conservar reviews entre {min_words} y {max_words} palabras.")

    for review_item in dataset:
        review_text = review_item["review"].strip()

        # Contar palabras
        word_count = len(review_text.split())

        # 1. Filtro Mínimo: ¿Es de solo 1 palabra?
        if word_count < min_words:
            reviews_eliminadas_min += 1
            continue

        # 2. Filtro Máximo: ¿Excede el límite de 20 palabras?
        if word_count > max_words:
            reviews_eliminadas_max += 1
            continue

        # Si pasa ambos filtros, se conserva
        reviews_conservadas.append(review_item)

    reviews_eliminadas_total = reviews_eliminadas_min + reviews_eliminadas_max

    print("--- Resultados del Filtrado ---")
    print(f"Reviews eliminadas (1 palabra): {reviews_eliminadas_min}")
    print(f"Reviews eliminadas (Más de {max_words} palabras): {reviews_eliminadas_max}")
    print(f"Reviews eliminadas (Total): {reviews_eliminadas_total}")
    print(f"Reviews conservadas (final): {len(reviews_conservadas)}")

    return reviews_conservadas

def ejecutar_limpieza(min_words, max_words):
    """Carga el dataset, lo limpia y lo guarda."""

    if not os.path.exists(ARCHIVO_DATASET):
        print(f"Error: No se encontró el archivo de dataset: {ARCHIVO_DATASET}")
        print("Por favor, ejecuta 'dataset.py' primero para crear el archivo.")
        return

    # 1. Cargar el dataset
    print(f"Cargando dataset desde {ARCHIVO_DATASET}...")
    with open(ARCHIVO_DATASET, "r", encoding="utf-8") as f:
        dataset_crudo = json.load(f)

    # 2. Limpiar el dataset
    dataset_limpio = limpiar_reviews_por_longitud(dataset_crudo, min_words, max_words)

    # 3. Guardar el dataset limpio (sobrescribe el original)
    print(f"\nGuardando dataset limpio en {ARCHIVO_DATASET}...")
    with open(ARCHIVO_DATASET, "w", encoding="utf-8") as f:
        json.dump(dataset_limpio, f, ensure_ascii=False, indent=2)

    print("Proceso de limpieza completado.")
    print(f"Tamaño final del archivo: {len(dataset_limpio)}")


if __name__ == "__main__":
    ejecutar_limpieza(MIN_WORDS, MAX_WORDS)