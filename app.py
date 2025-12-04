import os
import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
from views.main_window import MainWindow
from views.steam_apps_window import SteamAppsWindow

class MainApplication(QApplication):

    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()

        self.steam_apps_window = SteamAppsWindow()

        self.stack.addWidget(self.steam_apps_window)
        
        self.steam_apps_window.entrar_main_window.connect(self.ingresar_main)

        if os.path.exists('steam_apps_cache.json'):
            self.ingresar_main()
        else:
            self.stack.setCurrentWidget(self.steam_apps_window)

        self.stack.show()

    def ingresar_main(self):
        self.main_window = MainWindow()

        self.stack.addWidget(self.main_window)

        self.stack.setCurrentWidget(self.main_window)

if __name__ == "__main__":
    app = MainApplication()
    sys.exit(app.exec())