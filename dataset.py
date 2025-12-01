import os
import json
import requests
from typing import TypedDict, List, Union, Set
import random

# --- Estructuras de Datos ---
class Review(TypedDict):
    review_id: str
    review: str
    voted_up: bool

Dataset = List[Review]

# Definimos un límite muy alto para maximizar la recolección
MAX_FETCH_LIMIT = 1000
MAX_DIFF = 50 # Diferencia máxima permitida entre clases

# --- Funciones de Obtención de Reviews (CON MODIFICACIONES LEVES) ---

def obtener_reviews_por_tipo(app_id: int, review_type: str, limit: int, idioma: str) -> Dataset:
    """Busca las reviews dependiendo del tipo de valoración de la review"""
    resultado: Dataset = []
    seen_ids: Set[str] = set()
    cursor = "*"

    url = f"https://store.steampowered.com/appreviews/{app_id}"

    # Nota: Aquí limit será un valor muy grande (MAX_FETCH_LIMIT)
    print(f"Buscando hasta {limit} reviews de tipo: '{review_type}'")

    while len(resultado) < limit:
        params = {
            "json": 1,
            "filter": "recent",
            "language": idioma,
            "review_type": review_type,
            "purchase_type": "all",
            "num_per_page": 100,
            "cursor": cursor
        }

        try:
            # Añadir un control de tiempo para evitar bloquearse si la API está lenta
            response = requests.get(url, params=params, timeout=10).json()
        except Exception as e:
            print(f"Error de conexión: {e}")
            break

        reviews = response.get("reviews", [])
        nuevo_cursor = response.get("cursor")

        if not reviews:
            print(f"La API no devolvió más reviews de tipo '{review_type}'. Fin de la paginación.")
            break

        if nuevo_cursor == cursor:
            # Esto puede pasar si ya llegamos al final de todas las reviews
            if len(reviews) == 0:
                 print("El cursor no cambió (sin más reviews).")
            else:
                 # Pequeña pausa para evitar sobrecargar la API si el cursor se atasca
                 import time; time.sleep(1)

            break

        cursor = nuevo_cursor

        for r in reviews:
            if len(resultado) >= limit:
                break

            review_id = str(r["recommendationid"])

            if review_id in seen_ids:
                continue

            review_text = r["review"].strip()

            if not review_text:
                continue

            item: Review = {
                "review_id": review_id,
                "review": review_text,
                "voted_up": True if review_type == "positive" else False
            }

            resultado.append(item)
            seen_ids.add(review_id)

    print(f"Reviews encontradas para {review_type}: {len(resultado)}")
    return resultado

def obtener_reviews(
        app_ids: Union[int, List[int]],
        pos_limit: int = MAX_FETCH_LIMIT, # Usamos el límite alto
        neg_limit: int = MAX_FETCH_LIMIT, # Usamos el límite alto
        idioma: str = "spanish"
    ) -> Dataset:

    if isinstance(app_ids, int):
        app_ids = [app_ids]

    dataset: Dataset = []

    for app_id in app_ids:
        print(f"\n--- Procesando Juego ID: {app_id} ---")

        # Intenta obtener el máximo de ambas
        positivas = obtener_reviews_por_tipo(app_id, "positive", pos_limit, idioma)
        negativas = obtener_reviews_por_tipo(app_id, "negative", neg_limit, idioma)

        total_juego = positivas + negativas
        dataset.extend(total_juego)

        print(f"Total agregado para este juego: {len(total_juego)} (Pos: {len(positivas)}, Neg: {len(negativas)})")

    return dataset

# --- Función de Cache con Balanceo Óptimo (MODIFICADA) ---

def obtener_reviews_cache(
        app_ids: Union[int, List[int]],
        pos_limit: int = MAX_FETCH_LIMIT, # Se ignoran si el archivo no existe
        neg_limit: int = MAX_FETCH_LIMIT, # Se ignoran si el archivo no existe
        idioma: str = "spanish",
        archivo: str = "steam_reviews.json",
        max_diff: int = MAX_DIFF
    ) -> Dataset:
    """
    Si el archivo existe, lo carga.
    Si no existe, descarga el dataset (maximizando), lo balancea con max_diff, y lo guarda.
    """

    if os.path.exists(archivo):
        print(f"Cargando dataset desde {archivo}...")
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    print("No existe el dataset, descargando desde Steam (Maximizando)...")

    # 1. Descarga el dataset con el límite alto
    dataset_crudo = obtener_reviews(app_ids, MAX_FETCH_LIMIT, MAX_FETCH_LIMIT, idioma)

    # 2. Separar Positivas y Negativas
    positivas = [r for r in dataset_crudo if r["voted_up"]]
    negativas = [r for r in dataset_crudo if not r["voted_up"]]

    len_pos = len(positivas)
    len_neg = len(negativas)

    print(f"\n--- Balanceo de Clases ---")
    print(f"Datos crudos: Positivas: {len_pos}, Negativas: {len_neg}")

    # 3. Aplicar Balanceo (Downsampling solo si es necesario)
    diff = abs(len_pos - len_neg)

    if diff > max_diff:
        print(f"Diferencia ({diff}) excede el límite de {max_diff}. Aplicando downsampling.")

        # Clase menor define el límite base
        min_len = min(len_pos, len_neg)

        # El objetivo es min_len + max_diff
        nuevo_limite = min_len + max_diff

        if len_pos > len_neg:
            # Reducir Positivas para que queden con el nuevo límite
            positivas = random.sample(positivas, nuevo_limite)
        else:
            # Reducir Negativas para que queden con el nuevo límite
            negativas = random.sample(negativas, nuevo_limite)

        print(f"Tamaños ajustados: Positivas: {len(positivas)}, Negativas: {len(negativas)}")
    else:
        print(f"Diferencia ({diff}) está dentro del límite de {max_diff}. No se requiere downsampling.")


    # 4. Recombinar y Mezclar
    dataset_balanceado = positivas + negativas
    random.shuffle(dataset_balanceado)

    # 5. Guardar
    len_pos_final = len(positivas)
    len_neg_final = len(negativas)
    print(f"Dataset final: Positivas: {len_pos_final}, Negativas: {len_neg_final}")
    print(f"Cantidad total de reviews en el dataset final: {len(dataset_balanceado)}")

    print(f"Guardando dataset en {archivo}...")
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(dataset_balanceado, f, ensure_ascii=False, indent=2)

    return dataset_balanceado

# Ejecución directa para probar
if __name__ == "__main__":
    # Nota: Los límites de pos_limit y neg_limit en esta llamada son ignorados por la función
    # ya que internamente usa MAX_FETCH_LIMIT, a menos que uses el archivo de caché.

    # Lego indiana jones,
    # lego harry potter,
    # lego starwars complete saga,
    # lego batman,
    # lego indiana jones 2
    # lego jurassic world
    # lego marvel super heroes
    # lego lord of the rings
    dataset = obtener_reviews_cache(
        app_ids=[32330, 311770, 32440, 21000, 32450, 352400, 249130, 214510, ],
        max_diff=50 # Máxima diferencia permitida: 50 reviews
    )
    print("Cantidad final:", len(dataset))
