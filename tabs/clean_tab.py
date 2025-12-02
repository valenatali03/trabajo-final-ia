from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QLabel, QPushButton, QSpinBox

class CleanTab(QWidget):

    def __init__(self):
        super().__init__()

        self.label_dataset_file = QLabel("Introduzca el nombre del archivo del dataset \
                                          (steam_review.json por defecto):")
        
        self.line_edit_dataset_file = QLineEdit()

        self.label_min_words = QLabel("Introduzca la cantidad mínima de palabras en cada review:")
        
        self.spinbox_min_words = QSpinBox()

        self.label_max_words = QLabel("Introduzca la cantidad máxima de palabras en cada review:")

        self.spinbox_max_words = QSpinBox()

        self.button = QPushButton("Limpiar dataset")

        layout = QVBoxLayout()
        layout.addWidget(self.label_dataset_file)
        layout.addWidget(self.line_edit_dataset_file)
        layout.addWidget(self.label_min_words)
        layout.addWidget(self.spinbox_min_words)
        layout.addWidget(self.label_max_words)
        layout.addWidget(self.spinbox_max_words)
        layout.addWidget(self.button)
        layout.addStretch()

        self.setLayout(layout)