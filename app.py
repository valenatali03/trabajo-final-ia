import os
import sys
from const import *
from PySide6.QtWidgets import QApplication, QStackedWidget
from views.main_window import MainWindow
from views.steam_apps_window import SteamAppsWindow
from dataset_manager import DatasetManager

class MainApplication(QApplication):

    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()
        self.steam_apps_window = SteamAppsWindow(DatasetManager(STEAM_APPS_CACHE))

        self.stack.addWidget(self.steam_apps_window)
        self.steam_apps_window.entrar_main_window.connect(self.ingresar_main)

        if os.path.exists(STEAM_APPS_CACHE):
            self.ingresar_main()
        else:
            self.stack.setCurrentWidget(self.steam_apps_window)

        self.stack.show()

    def ingresar_main(self) -> None:
        self.main_window = MainWindow()
        self.stack.addWidget(self.main_window)
        self.stack.setCurrentWidget(self.main_window)

if __name__ == "__main__":
    app = MainApplication()
    sys.exit(app.exec())