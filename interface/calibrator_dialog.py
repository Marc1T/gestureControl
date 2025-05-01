from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class CalibratorDialog(QDialog):
    def __init__(self, parent=None):
        """Initialise la fenêtre de calibration (placeholder)."""
        super().__init__(parent)
        self.setWindowTitle("Calibration")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Placeholder: Fenêtre de calibration dédiée."))
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        self.setLayout(layout)