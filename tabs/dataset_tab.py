from PySide6.QtWidgets import (QVBoxLayout, QWidget, QLineEdit, QPushButton, 
                               QSpinBox, QFormLayout, QCompleter, QHBoxLayout,
                               QScrollArea, QLabel, QFrame, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QStringListModel, QThread, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from dataset import MAX_FETCH_LIMIT
from dataset_manager import DatasetManager
from workers import DatasetWorker

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

        self.btn_agregar = QPushButton("+ Agregar otro juego")
        self.btn_agregar.setFixedWidth(150)
        self.btn_agregar.clicked.connect(self.agregar_nueva_fila)

        self.line_edit_filename = QLineEdit("steam_reviews.json")
        self.line_edit_filename.setPlaceholderText("nombre_del_archivo.json")

        regex = QRegularExpression(r"^[\w\-. ]+$")
        validator = QRegularExpressionValidator(regex, self.line_edit_filename)
        self.line_edit_filename.setValidator(validator)

        self.line_edit_filename.editingFinished.connect(self.validar_extension_json)

        self.spinbox_max_diff = QSpinBox()

        self.spinbox_pos_limit = QSpinBox()
        self.spinbox_pos_limit.setMaximum(MAX_FETCH_LIMIT)
        self.spinbox_neg_limit = QSpinBox()
        self.spinbox_neg_limit.setMaximum(MAX_FETCH_LIMIT)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(10)
        form_layout.addRow("Nombre del dataset:", self.line_edit_filename)
        form_layout.addRow("Límite positivas:", self.spinbox_pos_limit)
        form_layout.addRow("Límite negativas:", self.spinbox_neg_limit)
        form_layout.addRow("Máxima diferencia entre reviews:", self.spinbox_max_diff)

        self.button = QPushButton("Crear dataset")
        self.button.clicked.connect(self.crear_dataset)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        self.status_label.setVisible(False)

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
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

        self.setLayout(layout)

        self.modelo_completer = QStringListModel()
        
        self.agregar_nueva_fila()

    def obtener_juegos_seleccionados(self) -> set:
        seleccionados = set()
        for i in range(self.layout_items.count()):
            fila = self.layout_items.itemAt(i).widget()
            if fila:
                texto = fila.obtener_texto()
                if texto:
                    seleccionados.add(texto)
        return seleccionados

    def agregar_nueva_fila(self):
        fila = FilaJuego(self.modelo_completer, self.todos_los_juegos, self.obtener_juegos_seleccionados)
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
                    fila.setEnabled(False)
                    fila.btn_eliminar.setEnabled(False)
                    if texto:
                        app_id = int(texto.split(" ")[0])
                        app_ids.append(app_id)
            
            if not app_ids:
                print("No hay IDs seleccionados")
                return
            
            filename = self.line_edit_filename.text()
            self.line_edit_filename.setEnabled(False)

            pos_limit = self.spinbox_pos_limit.value()
            self.spinbox_pos_limit.setEnabled(False)

            neg_limit = self.spinbox_neg_limit.value()
            self.spinbox_neg_limit.setEnabled(False)

            max_diff = self.spinbox_max_diff.value()
            self.spinbox_max_diff.setEnabled(False)

            self.btn_agregar.setEnabled(False)

            self.button.setText("Creando dataset...")
            self.button.setEnabled(False)

            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.status_label.setText("Iniciando...")
            self.status_label.setVisible(True)

            self.thread = QThread()
            self.worker = DatasetWorker(app_ids, pos_limit, neg_limit, filename, max_diff)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)

            self.worker.signals.error.connect(self.mostrar_error)
            self.worker.signals.data_ready.connect(self.procesar_datos_exitosos)
            self.worker.signals.log.connect(self.status_label.setText)
            self.worker.signals.progress.connect(self.actualizar_barra_progreso)
            self.worker.signals.finished.connect(self.limpiar_thread)
            self.worker.signals.finished.connect(self.restaurar_ui)

            self.thread.start()
            
        except (ValueError, IndexError) as e:
            print(f"Error al procesar: {e}")

    def mostrar_error(self, mensaje_error):
        QMessageBox.critical(self, "Error", mensaje_error)

    def procesar_datos_exitosos(self, datos):
        dataset = DatasetManager(self.line_edit_filename.text())
        dataset.guardar_datos(datos)

        QMessageBox.information(self, "Éxito", "Dataset creado exitosamente")
    
    def actualizar_barra_progreso(self, valor):
        self.progress_bar.setValue(valor)

    def limpiar_thread(self):
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.worker.deleteLater()

    def restaurar_ui(self):
        for i in range(self.layout_items.count()):
                fila = self.layout_items.itemAt(i).widget()
                if fila:
                    fila.setEnabled(True)
                    fila.btn_eliminar.setEnabled(True)

        self.line_edit_filename.setEnabled(True)

        self.spinbox_max_diff.setEnabled(True)

        self.spinbox_pos_limit.setEnabled(True)

        self.spinbox_neg_limit.setEnabled(True)

        self.btn_agregar.setEnabled(True)

        self.button.setText("Crear dataset")

        self.button.setEnabled(True)

        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)

        self.status_label.setVisible(False)

    def validar_extension_json(self):
        texto = self.line_edit_filename.text().strip()
        
        if not texto:
            return
        
        if not texto.lower().endswith(".json"):
            nuevo_texto = f"{texto}.json"
            self.line_edit_filename.setText(nuevo_texto)

class FilaJuego(QWidget):
    def __init__(self, modelo_juegos : QStringListModel, lista_juegos, callback_juegos_usados):
        super().__init__()

        self.modelo_juegos = modelo_juegos
        self.lista_juegos = lista_juegos
        self.callback_juegos_usados = callback_juegos_usados

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

        juegos_usados = self.callback_juegos_usados()

        for juego in self.lista_juegos:
            if texto_usuario in juego.lower() and juego not in juegos_usados:
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