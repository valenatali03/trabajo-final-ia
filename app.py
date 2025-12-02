import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

class MainApplication(QApplication):

    def __init__(self):
        super().__init__()

        self.main_window = MainWindow()

        self.main_window.show()
        

    
if __name__ == "__main__":
    app = MainApplication()
    sys.exit(app.exec())