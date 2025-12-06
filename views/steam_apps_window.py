from PySide6.QtWidgets import (QMainWindow, QLineEdit, QPushButton, QFormLayout, 
                               QVBoxLayout, QLabel, QWidget, QMessageBox, QProgressBar)
from PySide6.QtCore import Signal, Qt, QThread
from workers import SteamWorker
from dataset_manager import DatasetManager
from structs import SteamApps
from typing import Optional

class SteamAppsWindow(QMainWindow):
    entrar_main_window = Signal()

    def __init__(self, dataset_manager: DatasetManager):
        super().__init__()

        self.dataset_manager = dataset_manager
        
        # Tipado explícito
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[SteamWorker] = None

        container = QWidget()
        self.setCentralWidget(container)

        self.setWindowTitle("Inicialización")

        self.desc = QLabel("Esto solo se hace la primera vez para crear el cache de las apps de steam")
        self.line_edit_apikey = QLineEdit()
        self.button = QPushButton("Ingresar")
        self.progress_bar = QProgressBar()
        
        self.status_bar = self.statusBar()
        self.status_bar.addWidget(self.progress_bar)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()

        form_layout = QFormLayout()

        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setSpacing(15)

        form_layout.addRow("Introduzca su api_key:", self.line_edit_apikey)

        link_label = QLabel('<a href="https://steamcommunity.com/dev/apikey">Obtener API Key aquí</a>')
        link_label.setOpenExternalLinks(True)

        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(container)
        layout.addWidget(self.desc)
        layout.addLayout(form_layout)
        layout.addWidget(link_label)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.crear_cache)

    def crear_cache(self) -> None:
        api_key = self.line_edit_apikey.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Campo Vacío", "Por favor, escribe una API Key.")
            return

        self.button.setText("Verificando y Descargando...")
        self.button.setEnabled(False)
        self.line_edit_apikey.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.show()

        self.worker_thread = QThread()
        self.worker = SteamWorker(api_key)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        
        self.worker.signals.error.connect(self.mostrar_error)
        self.worker.signals.data_ready.connect(self.procesar_datos_exitosos)
        self.worker.signals.progress.connect(self.actualizar_barra_progreso)
        self.worker.signals.finished.connect(self.limpiar_thread)
        self.worker.signals.finished.connect(self.restaurar_ui)

        self.worker_thread.start()

    def mostrar_error(self, mensaje_error: str) -> None:
        QMessageBox.critical(self, "Error", mensaje_error)

    def procesar_datos_exitosos(self, datos: SteamApps) -> None:
        self.dataset_manager.guardar_datos(datos)
        QMessageBox.information(self, "Éxito", "Juegos de steam descargados")
        self.entrar_main_window.emit()

    def restaurar_ui(self) -> None:
        self.button.setText("Ingresar")
        self.button.setEnabled(True)
        self.line_edit_apikey.setEnabled(True)

    def limpiar_thread(self) -> None:
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread.deleteLater()
            self.worker_thread = None
            
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None
    
    def actualizar_barra_progreso(self, valor: int) -> None:
        self.progress_bar.setValue(valor)