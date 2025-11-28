import requests
from typing import TypedDict, List, Union

class Review(TypedDict):
    review: str
    voted_up: bool

Dataset = List[Review]

def obtener_reviews(app_ids: Union[int, List[int]],
                    pos_limit: int = 100,
                    neg_limit: int = 100,
                    idioma: str = "spanish") -> Dataset:
    """Crea el dataset del modelo con Web Scraping en base a reviews de videojuegos de steam

    Args:
        app_ids (Union[int, List[int]]): id o ids de los juegos 
        pos_limit (int, optional): Límite de reviews positivas. Defaults to 100.
        neg_limit (int, optional): Límite de reviews negativas. Defaults to 100.
        idioma (str, optional): Idioma de las reviews. Defaults to "spanish".

    Returns:
        Dataset: Lista de diccionarios que solo poseen el contenido de la reseña y su calificación (Positivo, Negativo)
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
            
        for p, n in zip(positivas, negativas):
            dataset.append(p)
            dataset.append(n)

        print("Terminado")

    print(f"Dataset creado. Total: {len(dataset)} elementos")
    return dataset

if __name__ == "__main__":
    #Id de Cuphead y The Witcher 3
    dataset = obtener_reviews([268910, 292030])