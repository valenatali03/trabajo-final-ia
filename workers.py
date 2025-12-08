import requests
import time
import dataset
from typing import List, Dict, Any, Optional, cast
from PySide6.QtCore import QObject, Signal
from structs import SteamApps, Dataset

class WorkerSignals(QObject):
    """
    Define las señales utilizadas por los workers para comunicarse con el hilo principal de la GUI.

    Attributes:
        finished (Signal): Se emite cuando el proceso ha terminado (con o sin éxito).
        error (Signal): Se emite cuando ocurre un error, enviando un mensaje de texto.
        log (Signal): Se emite para enviar mensajes de registro o estado.
        progress (Signal): Se emite para actualizar barras de progreso (0-100).
        data_ready (Signal): Se emite cuando los datos han sido procesados y están listos para enviarse.
    """
    finished = Signal()
    error = Signal(str)
    log = Signal(str)
    progress = Signal(int)
    data_ready = Signal(list)

class SteamWorker(QObject):
    """
    Worker encargado de interactuar con la API de Steam para obtener la lista de aplicaciones.
    Se ejecuta en un hilo separado para no bloquear la interfaz.
    """
    def __init__(self, api_key: str):
        """
        Inicializa el worker con la API Key necesaria.

        Args:
            api_key (str): La clave de API de Steam proporcionada por el usuario.
        """
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running: bool = True
        self.url: str = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        self.todas_las_apps: SteamApps = []
        self.last_appid: int = 0
        self.api_key: str = api_key

    def run(self) -> None:
        """
        Ejecuta la lógica principal de obtención de datos.
        Realiza peticiones paginadas a la API de Steam, procesa la respuesta JSON
        y emite señales de progreso o error según corresponda.
        """
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
                    
                    apps_optimizado = cast(SteamApps, [
                        {'appid': app['appid'], 'name': app['name']} for app in apps
                    ])
                    
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

class DatasetWorker(QObject):
    """
    Worker encargado de la generación o recuperación del dataset de reseñas.
    Gestiona la obtención de reviews positivas y negativas en segundo plano.
    """
    def __init__(self, app_ids: List[int], pos_limit: int, neg_limit: int, filename: str, max_diff: int):
        """
        Configura los parámetros para la creación del dataset.

        Args:
            app_ids (List[int]): Lista de IDs de aplicaciones de Steam a procesar.
            pos_limit (int): Límite de reseñas positivas a obtener.
            neg_limit (int): Límite de reseñas negativas a obtener.
            filename (str): Nombre del archivo donde se guardará o leerá el caché.
            max_diff (int): Diferencia máxima permitida entre cantidad de reseñas positivas y negativas.
        """
        super().__init__()
        self.signals = WorkerSignals()
        self.app_ids = app_ids
        self.pos_limit = pos_limit
        self.neg_limit = neg_limit
        self.filename = filename
        self.max_diff = max_diff
        self.is_running = True

    def run(self) -> None:
        """
        Ejecuta la lógica de obtención de reviews llamando al módulo 'dataset'.
        Utiliza callbacks para comunicar el progreso y estado a la GUI.
        """
        callbacks = {
            'check_stop': lambda: not self.is_running,
            'progress': self.signals.progress.emit,
            'error': self.signals.error.emit,
            'log': self.signals.log.emit
        }

        try:
            data: Dataset = dataset.obtener_reviews_cache(
                app_ids=self.app_ids,
                pos_limit=self.pos_limit,
                neg_limit=self.neg_limit,
                archivo=self.filename,
                max_diff=self.max_diff,
                callbacks=callbacks
            )

            if self.is_running and data:
                self.signals.data_ready.emit(data)

        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def stop(self) -> None:
        """
        Señaliza al worker para que detenga su ejecución de manera segura.
        """
        self.is_running = False