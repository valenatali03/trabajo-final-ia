from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QPushButton, QSpinBox, QFormLayout
from PySide6.QtCore import Qt
from dataset import obtener_reviews_cache, MAX_FETCH_LIMIT

class DatasetTab(QWidget):
    def __init__(self):
        super().__init__()

        self.line_edit_appid = QLineEdit()

        self.line_edit_appid.setPlaceholderText("Ej: 32330")

        self.spinbox_pos_limit = QSpinBox()
        self.spinbox_pos_limit.setMaximum(MAX_FETCH_LIMIT)

        self.spinbox_neg_limit = QSpinBox()
        self.spinbox_neg_limit.setMaximum(MAX_FETCH_LIMIT)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setSpacing(15)

        form_layout.addRow("Introduce la id de un juego de steam:", self.line_edit_appid)
        form_layout.addRow("Introduce el límite de reviews positivas:", self.spinbox_pos_limit)
        form_layout.addRow("Introduce el límite de reviews negativas:", self.spinbox_neg_limit)

        self.button = QPushButton("Crear dataset")
        self.button.clicked.connect(self.crear_dataset)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button)
        layout.addStretch()

        self.setLayout(layout)

    def crear_dataset(self):
        texto = self.line_edit_appid.text()
        
        pos_limit = self.spinbox_pos_limit.value()

        neg_limit = self.spinbox_neg_limit.value()

        obtener_reviews_cache(int(texto), pos_limit=pos_limit, neg_limit=neg_limit)



        