import requests
import time
from PySide6.QtCore import QObject, Signal
from structs import SteamApps

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)
    data_ready = Signal(list)

class SteamWorker(QObject):
    def __init__(self, api_key: str):
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running : bool = True
        self.url : str = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        self.todas_las_apps : SteamApps = []
        self.last_appid : int = 0
        self.api_key : str = api_key

    def run(self):
        if not self.api_key:
            self.signals.error.emit("Por favor, coloca una API Key válida.")
            self.signals.finished.emit()
            return

        try:
            for i in range(3): 
                if not self.is_running: break

                params = {
                    'key': self.api_key,
                    'max_results': 50000,
                    'last_appid': self.last_appid,
                    'include_games': 'true'
                }

                response = requests.get(self.url, params=params, timeout=10)
                
                if response.status_code == 403:
                    self.signals.error.emit("La API Key es incorrecta o ha sido revocada (Error 403).")
                    return
                
                response.raise_for_status()
                
                data = response.json()

                if 'response' in data and 'apps' in data['response']:
                    apps = data['response']['apps']
                    apps_optimizado = [{'appid': app['appid'], 'name': app['name']} for app in apps]
                    
                    self.todas_las_apps.extend(apps_optimizado)
                    
                    if apps_optimizado:
                        self.last_appid = apps_optimizado[-1]['appid']

                    self.signals.progress.emit((i + 1) * 33)
                    time.sleep(1)
                else:
                    break

            self.signals.data_ready.emit(self.todas_las_apps)

        except requests.exceptions.RequestException as e:
            self.signals.error.emit(f"Error de conexión: {str(e)}")
        except Exception as e:
            self.signals.error.emit(f"Error inesperado: {str(e)}")
        finally:
            self.signals.finished.emit()

