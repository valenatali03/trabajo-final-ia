from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QLabel, QPushButton, QSpinBox

class DatasetTab(QWidget):
    def __init__(self):
        super().__init__()

        self.label_appid = QLabel("Introduce la id de un juego de steam:")

        self.line_edit_appid = QLineEdit()

        self.label_pos_limit = QLabel("Introduce el límite de reviews positivas:")

        self.spinbox_pos_limit = QSpinBox()

        self.label_neg_limit = QLabel("Introduce el límite de reviews negativas:")

        self.spinbox_neg_limit = QSpinBox()

        self.button = QPushButton("Crear dataset")

        layout = QVBoxLayout()
        layout.addWidget(self.label_appid)
        layout.addWidget(self.line_edit_appid)
        layout.addWidget(self.label_pos_limit)
        layout.addWidget(self.spinbox_pos_limit)
        layout.addWidget(self.label_neg_limit)
        layout.addWidget(self.spinbox_neg_limit)
        layout.addWidget(self.button)
        layout.addStretch()

        self.setLayout(layout)



        