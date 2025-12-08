from typing import TypedDict, List, Union, Set

class Review(TypedDict):
    """
    Estructura de datos que representa una reseña individual de Steam.
    
    Attributes:
        review_id (str): Identificador único de la reseña.
        review (str): El contenido textual de la reseña.
        voted_up (bool): True si la reseña es positiva, False si es negativa.
    """
    review_id: str
    review: str
    voted_up: bool

# Alias para una lista de reseñas
Dataset = List[Review]

class SteamApp(TypedDict):
    """
    Estructura de datos que representa una aplicación/juego de Steam simplificado.
    
    Attributes:
        appid (int): ID numérico de la aplicación en Steam.
        name (str): Nombre de la aplicación.
    """
    appid: int
    name: str

# Alias para una lista de aplicaciones de Steam
SteamApps = List[SteamApp]