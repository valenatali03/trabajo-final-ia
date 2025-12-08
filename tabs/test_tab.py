from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QFormLayout, QLabel
from predict import load_model, predict
from const import MODEL_DEFAULT_DIR_PATH

class TestTab(QWidget):
    """
    Pestaña para probar el modelo entrenado realizando predicciones individuales.
    Permite cargar diferentes versiones del modelo y clasificar reseñas ingresadas manualmente.
    """

    def __init__(self):
        """
        Inicializa la pestaña, carga el modelo por defecto y configura la interfaz de prueba.
        """
        super().__init__()
        self.tokenizer, self.model = load_model()
        self.model_dir = MODEL_DEFAULT_DIR_PATH
        self.model_state = QLabel()
        self.update_model(self.model_dir)
        layout = QFormLayout()

        self.input = QLineEdit()
        self.model_input = QLineEdit()
        self.button = QPushButton("Enviar")
        self.model_import_button = QPushButton("Importar")
        self.button.clicked.connect(self.on_predict_start)
        self.model_import_button.clicked.connect(lambda: self.update_model(new_output=self.model_input.text()))
        self.result = QLabel()

        layout.addRow(self.model_state)
        layout.addRow("(Opcional) Introduzca la ruta a la carpeta del modelo (relativa a app.py)", self.model_input)
        layout.addRow(self.model_import_button)
        layout.addRow("Introduzca su reseña", self.input)
        layout.addRow(self.button)
        layout.addRow("Resultado:", self.result)


        self.setLayout(layout)
    
    def on_predict_start(self):
        """
        Ejecuta la predicción sobre el texto ingresado en el campo de entrada
        y muestra el resultado (sentimiento y precisión) en la etiqueta de resultado.
        """
        self.result.setText("Enviando predicción...")
        result, accuracy = predict(self.input.text(), self.tokenizer, self.model)
        if (result is not None and accuracy is not None):
            self.result.setText("La reseña ingresada es " + result + " con una precisión de " + f"{accuracy*100:.2f}" + "%")
        else: 
            self.result.setText("Se produjo un error.")

    def update_model(self, new_output):
        """
        Carga un nuevo modelo desde la ruta especificada.

        Args:
            new_output (str): Ruta al directorio del modelo guardado.
        """
        self.model_state.setText(f"Cargando nuevo modelo desde: {new_output}...")
        self.model_state.repaint()
        
        try:
            self.tokenizer, self.model = load_model(new_output)
            self.model_dir = new_output
            self.model_state.setText(f"Modelo importado desde: {new_output}")

        except Exception as e:
            self.model_state.setText(f"Error cargando modelo: {str(e)}")