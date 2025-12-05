import os
import json
import requests
from typing import List, Union, Set
from structs import Review, Dataset
import random

MAX_FETCH_LIMIT = 1000 # cant de reseñas a descargar de cada tipo por juego
MAX_DIFF = 50          # diferencia máxima permitida entre clases

# --- Funciones de Obtención de Reviews (CON MODIFICACIONES LEVES) ---

def _error(callbacks, error):
    if callbacks and 'error' in callbacks:
        callbacks['error'](error)

def _progreso(callbacks, valor):
    if callbacks and 'progress' in callbacks:
        callbacks['progress'](valor)

def _check_stop(callbacks):
    if callbacks and 'check_stop' in callbacks:
        if callbacks['check_stop']():
            raise InterruptedError("Detenido por el usuario")
        
def _log(callbacks, msg):
    if callbacks and 'log' in callbacks:
        callbacks['log'](msg)

def obtener_reviews_por_tipo(app_id: int, review_type: str, limit: int, 
                             idioma: str, callbacks = None) -> Dataset:
    """Busca las reviews dependiendo del tipo de valoración de la review"""
    resultado: Dataset = []
    seen_ids: Set[str] = set()
    cursor = "*"

    url = f"https://store.steampowered.com/appreviews/{app_id}"

    _log(callbacks, f"Buscando hasta {limit} reviews de tipo: '{review_type}'")

    while len(resultado) < limit:

        _check_stop(callbacks)

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
            # tiene un control de tiempo para evitar que se bloquee si la API está llena
            response = requests.get(url, params=params, timeout=10).json()
        except Exception as e:
            _error(callbacks, f"Error de conexión: {e}")
            break

        reviews = response.get("reviews", [])
        nuevo_cursor = response.get("cursor")

        if not reviews:
            _log(callbacks, f"La API no devolvió más reviews de tipo '{review_type}'. Fin de la paginación.")
            break

        if nuevo_cursor == cursor:
            # esto puede pasar si ya llegamos al final de todas las reviews
            if len(reviews) == 0:
                 _log(callbacks, "El cursor no cambió (sin más reviews).")
            else:
                 # pausa para evitar sobrecargar la API si el cursor se atasca
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

    _log(callbacks, f"Reviews encontradas para {review_type}: {len(resultado)}")
    return resultado

def obtener_reviews(
        app_ids: Union[int, List[int]],
        pos_limit: int = MAX_FETCH_LIMIT, # Usamos el límite alto
        neg_limit: int = MAX_FETCH_LIMIT, # Usamos el límite alto
        idioma: str = "spanish",
        callbacks = None
    ) -> Dataset:

    if isinstance(app_ids, int):
        app_ids = [app_ids]

    dataset: Dataset = []

    for (i, app_id) in enumerate(app_ids):
        _check_stop(callbacks)

        _log(callbacks, f"\n--- Procesando Juego ID: {app_id} ---")

        positivas = obtener_reviews_por_tipo(app_id, "positive", pos_limit, idioma, callbacks=callbacks)
        negativas = obtener_reviews_por_tipo(app_id, "negative", neg_limit, idioma, callbacks=callbacks)

        total_juego = positivas + negativas
        dataset.extend(total_juego)

        _progreso(callbacks, (i/len(app_ids)) * 100)

        _log(callbacks, f"Total agregado para este juego: {len(total_juego)} (Pos: {len(positivas)}, Neg: {len(negativas)})")

    return dataset

# función de cache con balanceo
def obtener_reviews_cache(
        app_ids: Union[int, List[int]],
        pos_limit: int = MAX_FETCH_LIMIT, # se ignoran si el archivo no existe
        neg_limit: int = MAX_FETCH_LIMIT,
        idioma: str = "spanish",
        archivo: str = "steam_reviews.json",
        max_diff: int = MAX_DIFF,
        callbacks = None
    ) -> Dataset:
    """
    Si el archivo existe, lo carga.
    Si no existe, descarga el dataset (maximizando), lo balancea con max_diff, y lo guarda.
    """

    if os.path.exists(archivo):
        print(f"Cargando dataset desde {archivo}...")
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    _log(callbacks, "No existe el dataset, descargando desde Steam (Maximizando)...")

    # descarga el dataset
    dataset_crudo = obtener_reviews(app_ids, pos_limit, neg_limit, idioma, callbacks=callbacks)

    # separar positivas y negativas
    positivas = [r for r in dataset_crudo if r["voted_up"]]
    negativas = [r for r in dataset_crudo if not r["voted_up"]]

    len_pos = len(positivas)
    len_neg = len(negativas)

    _log(callbacks, f"\n--- Balanceo de Clases ---")
    _log(callbacks, f"Datos crudos: Positivas: {len_pos}, Negativas: {len_neg}")

    # aplicar balanceo si es necesario
    diff = abs(len_pos - len_neg)

    if diff > max_diff:
        _log(callbacks, f"Diferencia ({diff}) excede el límite de {max_diff}. Aplicando downsampling.")

        # la clase menor define el límite base
        min_len = min(len_pos, len_neg)

        nuevo_limite = min_len + max_diff

        if len_pos > len_neg:
            # reducir positivas
            positivas = random.sample(positivas, nuevo_limite)
        else:
            # reducir negativas
            negativas = random.sample(negativas, nuevo_limite)

        _log(callbacks, f"Tamaños ajustados: Positivas: {len(positivas)}, Negativas: {len(negativas)}")
    else:
        _log(callbacks, f"Diferencia ({diff}) está dentro del límite de {max_diff}. No se requiere downsampling.")


    # recombinar de nuevo
    dataset_balanceado = positivas + negativas
    random.shuffle(dataset_balanceado)

    _progreso(callbacks, 100)

    # guardar
    len_pos_final = len(positivas)
    len_neg_final = len(negativas)
    _log(callbacks, f"Dataset final: Positivas: {len_pos_final}, Negativas: {len_neg_final}")
    _log(callbacks, f"Cantidad total de reviews en el dataset final: {len(dataset_balanceado)}")

    return dataset_balanceado

if __name__ == "__main__":

    # Lego indiana jones,
    # lego harry potter,
    # lego starwars complete saga,
    # lego batman,
    # lego indiana jones 2
    # lego jurassic world
    # lego marvel super heroes
    # lego lord of the rings
    # lego movie videogame
    # lego star wars 3
    # lego builder journey
    # lego party
    # lego voyagers
    # lego bricktales
    # lego marvel super heroes 2
    # lego star wars the force awakens
    # lego movie 2 videogame
    dataset = obtener_reviews_cache(
        app_ids=[32330, 311770, 32440, 21000, 32450, 352400, 249130, 214510, 267530, 32510, 1544360, 1969370, 1538550, 1898290, 647830, 438640, 881320, 2428810, 204120, 285160],
        max_diff=50
    )
    print("Cantidad final:", len(dataset))
