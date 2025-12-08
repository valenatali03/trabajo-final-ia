from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QSpinBox, QFormLayout, QDoubleSpinBox, QLabel, QApplication
from PySide6.QtCore import Signal
from const import LEARNING_RATE, TEST_SIZE, EPOCHS, DATASET_NAME, MODEL_DEFAULT_DIR_NAME
from datetime import datetime
import train

class TrainTab(QWidget):
    """
    Pestaña de configuración y ejecución del entrenamiento del modelo.
    Permite ajustar hiperparámetros como epochs, learning rate y test size.
    
    Attributes:
        train_finished (Signal): Se emite con la ruta del modelo generado al finalizar el entrenamiento.
    """
    train_finished = Signal(str)

    def __init__(self):
        """
        Inicializa los campos de entrada con valores por defecto definidos en `const.py`
        y configura el layout del formulario.
        """
        super().__init__()

        layout = QFormLayout()

        self.line_edit_dataset_file = QLineEdit(placeholderText="steam_reviews.json")
        self.line_edit_dataset_file.setText(DATASET_NAME)
        self.test_size = QDoubleSpinBox(minimum=0.0, maximum=1.0, singleStep=0.1)
        self.test_size.setValue(TEST_SIZE)
        self.epochs = QSpinBox(minimum=1)
        self.epochs.setValue(EPOCHS)
        self.learning_rate = QDoubleSpinBox(minimum=0.0, maximum=1.0, singleStep=0.00001, decimals=5)
        self.learning_rate.setValue(LEARNING_RATE)
        self.button = QPushButton("Comenzar entrenamiento")
        self.progress = QLabel("Esperando para iniciar.")
    
        self.button.clicked.connect(self.iniciar_entrenamiento)

        layout.addRow("Introduzca el nombre del archivo del dataset", self.line_edit_dataset_file)
        layout.addRow("Introduzca el tamaño del conjunto de validación", self.test_size)
        layout.addRow("Introduzca el número de épocas", self.epochs)
        layout.addRow("Introduzca la tasa de aprendizaje", self.learning_rate)
        layout.addRow(self.button)
        layout.addRow(self.progress)

        self.setLayout(layout)

    def iniciar_entrenamiento(self):
        """
        Recopila los parámetros configurados, crea un directorio con timestamp para el modelo,
        y ejecuta el proceso de entrenamiento.
        Nota: Utiliza processEvents para actualizar la UI, aunque el entrenamiento es bloqueante en este hilo.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"./{MODEL_DEFAULT_DIR_NAME}_{timestamp}"
        dataset = self.line_edit_dataset_file.text()
        test_size = self.test_size.value()
        epochs = self.epochs.value()
        lr = self.learning_rate.value()

        self.progress.setText("Entrenamiento en curso...")
        self.progress.setStyleSheet("color: orange;")
            
        self.progress.repaint()  
        QApplication.processEvents() 

        try:
            train.entrenar(dataset, test_size, epochs, lr, output_dir)
            self.train_finished.emit(output_dir)
            
            self.progress.setText("Entrenamiento completado.")
            self.progress.setStyleSheet("color: green; font-weight: bold;")
                
        except Exception as e:
            self.progress.setText("Error en el entrenamiento.")
            print(f"Error: {e}")