from PySide6.QtWidgets import (QVBoxLayout, QWidget, QLineEdit, QPushButton, 
                               QSpinBox, QFormLayout, QCompleter, QHBoxLayout,
                               QScrollArea, QLabel, QFrame)
from PySide6.QtCore import Qt, QStringListModel
from dataset import obtener_reviews_cache, MAX_FETCH_LIMIT
from dataset_manager import DatasetManager

class DatasetTab(QWidget):
    def __init__(self, dataset_manager: DatasetManager):
        super().__init__()

        self.dataset_manager = dataset_manager
        self.todos_los_juegos = [] 
        self.cargar_datos()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame) 
        self.scroll_area.setFixedHeight(150)

        self.container_items = QWidget()
        self.layout_items = QVBoxLayout(self.container_items)
        self.layout_items.setAlignment(Qt.AlignTop)
        self.layout_items.setContentsMargins(0,0,0,0)
        
        self.scroll_area.setWidget(self.container_items)

        self.spinbox_pos_limit = QSpinBox()
        self.spinbox_pos_limit.setMaximum(MAX_FETCH_LIMIT)
        self.spinbox_neg_limit = QSpinBox()
        self.spinbox_neg_limit.setMaximum(MAX_FETCH_LIMIT)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(10)
        form_layout.addRow("Límite positivas:", self.spinbox_pos_limit)
        form_layout.addRow("Límite negativas:", self.spinbox_neg_limit)

        self.button = QPushButton("Crear dataset")
        self.button.clicked.connect(self.crear_dataset)
        
        self.btn_agregar = QPushButton("+ Agregar otro juego")
        self.btn_agregar.setFixedWidth(150)
        self.btn_agregar.clicked.connect(self.agregar_nueva_fila)

        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Lista de Juegos a procesar:"))
        
        layout.addWidget(self.scroll_area)
        
        layout.addWidget(self.btn_agregar)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addLayout(form_layout)
        layout.addSpacing(10)
        layout.addWidget(self.button)
        layout.addStretch()

        self.setLayout(layout)

        self.modelo_completer = QStringListModel()
        
        self.agregar_nueva_fila()

    def agregar_nueva_fila(self):
        fila = FilaJuego(self.modelo_completer, self.todos_los_juegos)
        self.layout_items.addWidget(fila)
        fila.line_edit_appid.setFocus()

    def cargar_datos(self):
        try:
            steamapps = self.dataset_manager.obtener_apps_json()
            self.todos_los_juegos = [f"{app['appid']} ({app['name']})" for app in steamapps]
        except:
            self.todos_los_juegos = []

    def crear_dataset(self) -> None:
        app_ids = []
        try:
            for i in range(self.layout_items.count()):
                fila = self.layout_items.itemAt(i).widget()
                if fila:
                    texto = fila.obtener_texto()
                    if texto:
                        app_id = int(texto.split(" ")[0])
                        app_ids.append(app_id)
            
            if not app_ids:
                print("No hay IDs seleccionados")
                return

            pos_limit = self.spinbox_pos_limit.value()
            neg_limit = self.spinbox_neg_limit.value()

            obtener_reviews_cache(app_ids, pos_limit=pos_limit, neg_limit=neg_limit)
            
        except (ValueError, IndexError) as e:
            print(f"Error al procesar: {e}")


class FilaJuego(QWidget):
    def __init__(self, modelo_juegos : QStringListModel, lista_juegos):
        super().__init__()

        self.modelo_juegos = modelo_juegos
        self.lista_juegos = lista_juegos

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.line_edit_appid = QLineEdit()
        self.line_edit_appid.setPlaceholderText("Ej: 32330")
        self.line_edit_appid.setFixedWidth(250) 

        self.completer = QCompleter(self.modelo_juegos)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.line_edit_appid.setCompleter(self.completer)

        self.btn_eliminar = QPushButton("X")
        self.btn_eliminar.setFixedSize(30, 30)
        self.btn_eliminar.setStyleSheet("color: white; background-color: #d9534f; border: none; border-radius: 4px;")

        layout.addWidget(self.line_edit_appid)
        layout.addWidget(self.btn_eliminar)
        layout.addStretch() 

        self.line_edit_appid.textEdited.connect(self.actualizar_sugerencias)
        self.btn_eliminar.clicked.connect(self.eliminar_fila)

    def actualizar_sugerencias(self, texto_usuario):
        if not texto_usuario:
            return

        texto_usuario = texto_usuario.lower()
        coincidencias = []
        contador = 0
        LIMITE = 30
        for juego in self.lista_juegos:
            if texto_usuario in juego.lower():
                coincidencias.append(juego)
                contador += 1
                if contador >= LIMITE:
                    break
        self.modelo_juegos.setStringList(coincidencias)
        self.completer.complete()

    def eliminar_fila(self):
        self.deleteLater()

    def obtener_texto(self):
        return self.line_edit_appid.text().strip()