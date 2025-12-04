import os
import json
from structs import SteamApps

class DatasetManager():
    def __init__(self, archivo_json):
        self.archivo_json = archivo_json

    def obtener_apps_json(self) -> SteamApps:
        if not os.path.exists(self.archivo_json):
            print(f"Error: El archivo {self.archivo_json} no existe.")
            return []

        with open(self.archivo_json, 'r', encoding='utf-8') as archivo:
            datos:SteamApps = json.load(archivo)
        
        return datos