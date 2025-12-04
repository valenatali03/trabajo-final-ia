from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QPushButton, QSpinBox, QFormLayout, QCompleter
from PySide6.QtCore import Qt, QStringListModel
from dataset import obtener_reviews_cache, MAX_FETCH_LIMIT
from dataset_manager import DatasetManager

class DatasetTab(QWidget):
    def __init__(self, dataset_manager: DatasetManager):
        super().__init__()

        self.dataset_manager = dataset_manager
        
        self.todos_los_juegos = [] 
        self.cargar_datos()

        self.line_edit_appid = QLineEdit()
        self.line_edit_appid.setPlaceholderText("Ej: 32330")
        
        self.line_edit_appid.textEdited.connect(self.actualizar_sugerencias)

        self.spinbox_pos_limit = QSpinBox()
        self.spinbox_pos_limit.setMaximum(MAX_FETCH_LIMIT)
        self.spinbox_neg_limit = QSpinBox()
        self.spinbox_neg_limit.setMaximum(MAX_FETCH_LIMIT)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(15)

        form_layout.addRow("Busca el juego:", self.line_edit_appid)
        form_layout.addRow("Límite positivas:", self.spinbox_pos_limit)
        form_layout.addRow("Límite negativas:", self.spinbox_neg_limit)

        self.button = QPushButton("Crear dataset")
        self.button.clicked.connect(self.crear_dataset)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button)
        layout.addStretch()

        self.setLayout(layout)

        self.modelo_completer = QStringListModel()
        
        self.completer = QCompleter(self.modelo_completer, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        
        self.line_edit_appid.setCompleter(self.completer)

    def cargar_datos(self):
        steamapps = self.dataset_manager.obtener_apps_json()
        self.todos_los_juegos = [f"{app['appid']} ({app['name']})" for app in steamapps]

    def actualizar_sugerencias(self, texto_usuario):
        if not texto_usuario:
            return

        texto_usuario = texto_usuario.lower()
        coincidencias = []
        contador = 0
        LIMITE = 30

        for juego in self.todos_los_juegos:
            if texto_usuario in juego.lower():
                coincidencias.append(juego)
                contador += 1
                
                if contador >= LIMITE:
                    break
        
        self.modelo_completer.setStringList(coincidencias)

        self.completer.complete()

    def crear_dataset(self) -> None:
        texto = self.line_edit_appid.text()
        try:
            app_id = int(texto.split(" ")[0])
            pos_limit = self.spinbox_pos_limit.value()
            neg_limit = self.spinbox_neg_limit.value()
            obtener_reviews_cache(app_id, pos_limit=pos_limit, neg_limit=neg_limit)
        except (ValueError, IndexError):
            pass