from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class CalibratorDialog(QDialog):
    def __init__(self, parent=None):
        """Initialise la fenêtre de calibration."""
        super().__init__(parent)
        self.setWindowTitle("Calibration")
        self.setFixedSize(400, 200)
        self.step = 0
        self.instructions = [
            "Pointez vers le coin supérieur gauche de l'écran",
            "Pointez vers le coin supérieur droit de l'écran",
            "Pointez vers le coin inférieur droit de l'écran",
            "Pointez vers le coin inférieur gauche de l'écran"
        ]
        
        # Mise en page
        layout = QVBoxLayout()
        
        # Instruction
        self.instruction_label = QLabel(self.instructions[0])
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)
        
        # Bouton pour confirmer manuellement (optionnel)
        self.confirm_button = QPushButton("Confirmer ce point")
        self.confirm_button.clicked.connect(self.next_step)
        layout.addWidget(self.confirm_button)
        
        self.setLayout(layout)
        
    def update_instruction(self, step):
        """Met à jour l'instruction pour l'étape actuelle."""
        self.step = step
        if self.step < len(self.instructions):
            self.instruction_label.setText(self.instructions[self.step])
        else:
            self.accept()  # Ferme la fenêtre après le dernier point
            
    def next_step(self):
        """Passe à l'étape suivante manuellement."""
        self.update_instruction(self.step + 1)
