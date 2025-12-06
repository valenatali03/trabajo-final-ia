from PySide6.QtWidgets import QMainWindow, QTabWidget
from tabs.dataset_tab import DatasetTab
from tabs.clean_tab import CleanTab
from dataset_manager import DatasetManager
from const import *
from tabs.test_tab import TestTab
from tabs.train_tab import TrainTab

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
        self.train_tab = TrainTab()
        self.test_tab = TestTab()
        
        self.tabs.addTab(self.dataset_tab, "Dataset")
        self.tabs.addTab(self.clean_tab, "Limpieza")
        self.tabs.addTab(self.train_tab, "Entrenamiento")
        self.tabs.addTab(self.test_tab, "Prueba")

        self.train_tab.train_finished.connect(self.test_tab.update_model)
        
        self.setCentralWidget(self.tabs)