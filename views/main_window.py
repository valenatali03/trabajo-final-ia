from PySide6.QtWidgets import QMainWindow, QTabWidget
from tabs.dataset_tab import DatasetTab
from tabs.clean_tab import CleanTab
from dataset_manager import DatasetManager
from const import *

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.dataset_manager = DatasetManager(STEAM_APPS_CACHE)

        self.setWindowTitle("Steam Reviews")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)

        self.dataset_tab = DatasetTab(self.dataset_manager)
        self.clean_tab = CleanTab()
        
        self.tabs.addTab(self.dataset_tab, "Dataset")
        self.tabs.addTab(self.clean_tab, "Limpieza")
        
        self.setCentralWidget(self.tabs)