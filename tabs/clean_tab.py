from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QSpinBox, QFormLayout
import clean
from const import MAX_WORDS, MIN_WORDS
class CleanTab(QWidget):

    def __init__(self):
        super().__init__()

        layout = QFormLayout()

        self.line_edit_dataset_file = QLineEdit(placeholderText="steam_review.json")
        self.spinbox_min_words = QSpinBox()
        self.spinbox_min_words.setMinimum(MIN_WORDS)
        self.spinbox_min_words.valueChanged.connect(lambda: self.spinbox_max_words.setMinimum(self.spinbox_min_words.value()))
        self.spinbox_max_words = QSpinBox()
        self.spinbox_max_words.setMinimum(self.spinbox_min_words.value())
        self.spinbox_max_words.setValue(MAX_WORDS)
        self.button = QPushButton("Limpiar dataset")
        self.button.clicked.connect(lambda: clean.ejecutar_limpieza(self.spinbox_min_words.value(), self.spinbox_max_words.value()))

        layout.addRow("Introduzca el nombre del archivo del dataset", self.line_edit_dataset_file)
        layout.addRow("Introduzca la cantidad mínima de palabras en cada review", self.spinbox_min_words)
        layout.addRow("Introduzca la cantidad máxima de palabras en cada review", self.spinbox_max_words)
        layout.addRow(self.button)

        self.setLayout(layout)