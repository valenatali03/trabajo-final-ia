import os
import json
import requests
from typing import TypedDict, List, Union

class Review(TypedDict):
    review: str
    voted_up: bool


Dataset = List[Review]

def obtener_reviews(
        app_ids: Union[int, List[int]],
        pos_limit: int = 100,
        neg_limit: int = 100,
        idioma: str = "english"
    ) -> Dataset:
    """
    Descarga reviews desde la API de Steam, solamente en el idioma indicado.
    """

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

# Cache automático: guarda y carga steam_reviews.json
def obtener_reviews_cache(
        app_ids: Union[int, List[int]],
        pos_limit: int = 100,
        neg_limit: int = 100,
        idioma: str = "spanish",
        archivo: str = "steam_reviews.json"
    ) -> Dataset:
    """
    Si el archivo existe, lo carga.
    Si no existe, descarga el dataset y lo guarda.
    """

    if os.path.exists(archivo):
        print(f"Cargando dataset desde {archivo}...")
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    print("No existe el dataset, descargando desde Steam...")
    dataset = obtener_reviews(app_ids, pos_limit, neg_limit, idioma)

    print(f"Guardando dataset en {archivo}...")
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    return dataset

# Ejecución directa para probar
if __name__ == "__main__":
    # Cuphead (268910) + The Witcher 3 (292030)
    dataset = obtener_reviews_cache([268910, 292030])
    print("Cantidad final:", len(dataset))
