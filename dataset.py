import os
import json
import requests
from typing import TypedDict, List, Union

# --- Estructuras de Datos ---
class Review(TypedDict):
    review_id: str
    review: str
    voted_up: bool

Dataset = List[Review]

def obtener_reviews(
        app_ids: Union[int, List[int]],
        pos_limit: int = 100,
        neg_limit: int = 100,
        idioma: str = "spanish"
    ) -> Dataset:

    if isinstance(app_ids, int):
        app_ids = [app_ids]

    dataset: Dataset = []
    print("Creando dataset...")

    for app_id in app_ids:

        url = f"https://store.steampowered.com/appreviews/{app_id}"

        cursor = "*"
        params = {
            "json": 1,
            "language": idioma,
            "num_per_page": 100,
            "cursor": cursor
        }

        positivas: Dataset = []
        negativas: Dataset = []

        # Seguimos pidiendo hasta llegar al límite
        while len(positivas) < pos_limit or len(negativas) < neg_limit:
            request = requests.get(url, params=params).json()
            reviews = request.get("reviews", [])

            if not reviews:
                break

            for r in reviews:
                if r.get("voted_up") and len(positivas) < pos_limit:
                    positivas.append({"review": r["review"], "voted_up": True})
                elif not r.get("voted_up") and len(negativas) < neg_limit:
                    negativas.append({"review": r["review"], "voted_up": False})

            params["cursor"] = request["cursor"]

        # Mezclamos uno y uno
        for p, n in zip(positivas, negativas):
            dataset.append(p)
            dataset.append(n)

        print(f"Juego {app_id}: terminado.")

    print(f"Dataset creado. Total: {len(dataset)} elementos")
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
    dataset = obtener_reviews_cache(
        app_ids=[32330, 311770, 32440, 21000, 32450],
        max_diff=50 # Máxima diferencia permitida: 50 reviews
    )
    print("Cantidad final:", len(dataset))