from PySide6.QtWidgets import (QMainWindow, QLineEdit, QPushButton, QFormLayout, 
                               QVBoxLayout, QLabel, QWidget, QMessageBox)
from PySide6.QtCore import Signal, Qt
from steam_apps import obtener_apps
import os

class SteamAppsWindow(QMainWindow):
    entrar_main_window = Signal()

    def __init__(self):
        super().__init__()

        container = QWidget()
        self.setCentralWidget(container)

        self.setWindowTitle("Inicialización")

        self.desc = QLabel("Esto solo se hace la primera vez para crear el cache de las apps de steam")

        self.line_edit_apikey = QLineEdit()

        self.button = QPushButton("Ingresar")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(15)

        form_layout.addRow("Introduzca su api_key:", self.line_edit_apikey)

        link_label = QLabel('<a href="https://steamcommunity.com/dev/apikey">Obtener API Key aquí</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(container)
        layout.addWidget(self.desc)
        layout.addLayout(form_layout)
        layout.addWidget(link_label)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.crear_cache)

    def crear_cache(self):
        api_key = self.line_edit_apikey.text().strip() # .strip() quita espacios accidentales

        if not api_key:
            QMessageBox.warning(self, "Campo Vacío", "Por favor, escribe una API Key antes de continuar.")
            return

        try:
            self.button.setText("Verificando y Descargando...")
            self.button.setEnabled(False)
            self.repaint()

            obtener_apps(api_key)

            QMessageBox.information(self, "Éxito", "Base de datos actualizada correctamente.")
            self.entrar_main_window.emit()

        except ValueError as e:
            QMessageBox.critical(self, "Error de Autenticación", str(e))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado:\n{e}")

        finally:
            self.button.setText("Ingresar")
            self.button.setEnabled(True)
