import os
import json
import requests
from typing import TypedDict, List, Union, Set

class Review(TypedDict):
    review_id: str
    review: str
    voted_up: bool


Dataset = List[Review]

def obtener_reviews_por_tipo(app_id: int, review_type: str, limit: int, idioma: str) -> Dataset:
    """Busca las reviews dependiendo del tipo de valoración de la review"""
    resultado: Dataset = []
    seen_ids: Set[str] = set()
    cursor = "*"

    url = f"https://store.steampowered.com/appreviews/{app_id}"
    
    print(f"Buscando {limit} reviews de tipo: '{review_type}'")

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
            response = requests.get(url, params=params, timeout=10).json()
        except Exception as e:
            print(f"Error de conexión: {e}")
            break

        reviews = response.get("reviews", [])
        nuevo_cursor = response.get("cursor")

        if not reviews:
            print("La API no devolvió más reviews.")
            break
        
        if nuevo_cursor == cursor:
            print("El cursor no cambió (fin de la paginación).")
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

    print(f"Reviews encontradas: {len(resultado)}")
    return resultado

def obtener_reviews(
        app_ids: Union[int, List[int]], 
        pos_limit: int = 100, 
        neg_limit: int = 100,
        idioma: str = "spanish"
    ) -> Dataset:

    if isinstance(app_ids, int):
        app_ids = [app_ids]

    dataset: Dataset = []
    seen_ids: Set[str] = set()

    for app_id in app_ids:
        print(f"Procesando Juego ID: {app_id}")
        
        positivas = obtener_reviews_por_tipo(app_id, "positive", pos_limit, idioma)
        
        negativas = obtener_reviews_por_tipo(app_id, "negative", neg_limit, idioma)

        total_juego = positivas + negativas
        
        dataset.extend(total_juego)
        
        print(f"Total agregado para este juego: {len(dataset)} (Pos: {len(positivas)}, Neg: {len(negativas)})")

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
