import os
import json
from typing import List, Union, Any
from structs import SteamApps, Dataset

class DatasetManager:
    def __init__(self, archivo_json: str):
        self.archivo_json = archivo_json

    def guardar_datos(self, datos: Union[SteamApps, Dataset, List[Any]]) -> None:
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)

    def obtener_apps_json(self) -> SteamApps:
        if not os.path.exists(self.archivo_json):
            print(f"Error: El archivo {self.archivo_json} no existe.")
            return []

        with open(self.archivo_json, 'r', encoding='utf-8') as archivo:
            datos: SteamApps = json.load(archivo)
        
        return datos