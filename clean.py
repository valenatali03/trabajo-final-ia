import os
import json
from structs import Dataset
from const import MAX_WORDS, MIN_WORDS

ARCHIVO_DATASET = "steam_reviews.json"

# filtra el dataset para eliminar reviews que contienen menos de 'MIN_WORDS' palabras ó mas de 'MAX_WORDS' palabras
def limpiar_reviews_por_longitud(dataset: Dataset, min_words, max_words) -> Dataset:
    reviews_iniciales = len(dataset)
    reviews_conservadas: Dataset = []
    reviews_eliminadas_min = 0
    reviews_eliminadas_max = 0

    print(f"Iniciando limpieza. Total de reviews iniciales: {reviews_iniciales}")
    print(f"Criterio: Conservar reviews entre {min_words} y {max_words} palabras.")

    # chequear que cada review tenga entre MIN_WORDS y MAX_WORDS palabras,
    # sino se descarta
    for review_item in dataset:
        review_text = review_item["review"].strip()

        word_count = len(review_text.split())

        if word_count < min_words:
            reviews_eliminadas_min += 1
            continue

        if word_count > max_words:
            reviews_eliminadas_max += 1
            continue

        reviews_conservadas.append(review_item) # se conserva la palabra

    reviews_eliminadas_total = reviews_eliminadas_min + reviews_eliminadas_max

    print("--- Resultados del Filtrado ---")
    print(f"Reviews eliminadas (1 palabra): {reviews_eliminadas_min}")
    print(f"Reviews eliminadas (Más de {max_words} palabras): {reviews_eliminadas_max}")
    print(f"Reviews eliminadas (Total): {reviews_eliminadas_total}")
    print(f"Reviews conservadas (final): {len(reviews_conservadas)}")

    return reviews_conservadas

# carga el dataset, lo limpia y lo guarda.
def ejecutar_limpieza(min_words, max_words):

    if not os.path.exists(ARCHIVO_DATASET):
        print(f"Error: No se encontró el archivo de dataset: {ARCHIVO_DATASET}")
        print("Ejecuta 'dataset.py' primero para crear el archivo.")
        return

    # cargar el dataset
    print(f"Cargando dataset desde {ARCHIVO_DATASET}...")
    with open(ARCHIVO_DATASET, "r", encoding="utf-8") as f:
        dataset_crudo = json.load(f)

    # limpiar el dataset
    dataset_limpio = limpiar_reviews_por_longitud(dataset_crudo, min_words, max_words)

    # guardar el dataset limpio (sobrescribe el archivo json original)
    print(f"\nGuardando dataset limpio en {ARCHIVO_DATASET}...")
    with open(ARCHIVO_DATASET, "w", encoding="utf-8") as f:
        json.dump(dataset_limpio, f, ensure_ascii=False, indent=2)

    print("Proceso de limpieza completado.")
    print(f"Tamaño final del archivo: {len(dataset_limpio)}")


if __name__ == "__main__":
    ejecutar_limpieza(MIN_WORDS, MAX_WORDS)
