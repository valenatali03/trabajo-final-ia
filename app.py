import os
import sys
from const import *
from train import entrenar
from PySide6.QtWidgets import QApplication, QStackedWidget
from views.main_window import MainWindow
from views.steam_apps_window import SteamAppsWindow
from dataset_manager import DatasetManager

class MainApplication(QApplication):
    """
    Clase principal de la aplicación PySide6.
    Gestiona la navegación entre la ventana de configuración inicial (API Key)
    y la ventana principal de la aplicación mediante un QStackedWidget.
    """

    def __init__(self):
        """
        Inicializa la aplicación, configura el QStackedWidget y determina
        la vista inicial basándose en la existencia del caché de apps de Steam.
        """
        super().__init__()

        self.stack = QStackedWidget()
        self.steam_apps_window = SteamAppsWindow(DatasetManager(STEAM_APPS_CACHE))

        self.stack.addWidget(self.steam_apps_window)
        self.steam_apps_window.entrar_main_window.connect(self.ingresar_main)

        # Si ya existe el caché de apps, saltamos directamente a la ventana principal
        if os.path.exists(STEAM_APPS_CACHE):
            self.ingresar_main()
        else:
            self.stack.setCurrentWidget(self.steam_apps_window)

        self.stack.show()

    def ingresar_main(self) -> None:
        """
        Cambia la vista actual a la ventana principal (MainWindow),
        instanciándola y agregándola a la pila de widgets.
        """
        self.main_window = MainWindow()
        self.stack.addWidget(self.main_window)
        self.stack.setCurrentWidget(self.main_window)

if __name__ == "__main__":
    """
    Punto de entrada del script.
    1. Verifica si existe un modelo pre-entrenado en el directorio.
    2. Si no existe, inicia el proceso de entrenamiento automáticamente.
    3. Inicia el bucle de eventos de la interfaz gráfica.
    """
    model_found = False
    current_dir = os.scandir()
    for d in current_dir:
        model_found = (d.is_dir and d.name.startswith(MODEL_DEFAULT_DIR_NAME))
        if model_found:
            current_dir.close()
            break

    if (not model_found):
        print("No se encontro la carpeta del modelo. Entrenando...")
        entrenar(file=DATASET_NAME, test_size=0.2, epochs=3, learning_rate=3e-5)

    app = MainApplication()
    sys.exit(app.exec())