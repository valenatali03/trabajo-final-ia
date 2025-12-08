import os
import json
from typing import List, Union, Any
from structs import SteamApps, Dataset

class DatasetManager:
    """
    Clase utilitaria para gestionar la persistencia de datos en archivos JSON.
    Se utiliza tanto para almacenar el caché de aplicaciones de Steam como para guardar
    los datasets de reseñas generados.
    """
    def __init__(self, archivo_json: str):
        """
        Inicializa el gestor con la ruta del archivo destino.

        Args:
            archivo_json (str): Ruta o nombre del archivo JSON a gestionar.
        """
        self.archivo_json = archivo_json

    def guardar_datos(self, datos: Union[SteamApps, Dataset, List[Any]]) -> None:
        """
        Serializa y guarda los datos proporcionados en el archivo JSON configurado.
        Sobrescribe el archivo si ya existe.

        Args:
            datos (Union[SteamApps, Dataset, List[Any]]): La estructura de datos a guardar (lista de apps o lista de reviews).
        """
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)

    def obtener_apps_json(self) -> SteamApps:
        """
        Lee el archivo JSON y recupera la lista de aplicaciones de Steam.
        
        Returns:
            SteamApps: Lista de diccionarios con la información de las apps. 
                       Devuelve una lista vacía si el archivo no existe.
        """
        if not os.path.exists(self.archivo_json):
            print(f"Error: El archivo {self.archivo_json} no existe.")
            return []

        with open(self.archivo_json, 'r', encoding='utf-8') as archivo:
            datos: SteamApps = json.load(archivo)
        
        return datos