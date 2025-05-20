import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import configparser
from core.hand_tracker import HandTracker
from core.face_tracker import FaceTracker
from core.feature_extractor import FeatureExtractor
from core.gesture_analyzer import GestureAnalyzer
from core.gesture_classifier import GestureClassifier
from core.cursor_controller import CursorController
from interface.video_thread import VideoThread
from interface.calibrator_dialog import CalibratorDialog
from chatbot.faq_engine import FAQEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contrôle Gestuel")
        self.setGeometry(100, 100, 800, 600)
        
        # Chargement de la configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/settings.ini')
        
        # Initialisation des composants
        self.tracker = HandTracker(max_num_hands=2)
        self.face_tracker = FaceTracker()
        self.extractor = FeatureExtractor()
        self.analyzer = GestureAnalyzer(
            click_threshold=self.config.getfloat('controls', 'click_threshold', fallback=0.05),
            scroll_threshold=self.config.getfloat('controls', 'scroll_threshold', fallback=0.1),
            zoom_threshold=self.config.getfloat('controls', 'zoom_threshold', fallback=0.05)
        )
        self.classifier = GestureClassifier()
        self.controller = CursorController(
            smooth_factor=self.config.getfloat('controls', 'smooth_factor', fallback=0.3),
            control_mode="hand"
        )
        self.faq_engine = FAQEngine()
        self.control_mode = "hand"
        self.running = False
        
        # Interface graphique
        self.setup_ui()
        
        # Thread vidéo
        self.video_thread = VideoThread(self.tracker, self.face_tracker, self.extractor, 
                                      self.analyzer, self.classifier, self.controller)
        self.video_thread.frame_updated.connect(self.update_frame)
        self.video_thread.gesture_detected.connect(self.update_gesture_status)
        self.video_thread.calibration_step_updated.connect(self.update_calibration_step)
        self.video_thread.start()
        
    def setup_ui(self):
        """Configure l'interface graphique."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Widget vidéo
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        layout.addWidget(self.video_label)
        
        # Boutons
        self.start_button = QPushButton("Démarrer")
        self.start_button.clicked.connect(self.toggle)
        layout.addWidget(self.start_button)
        
        self.calibrate_button = QPushButton("Calibrer")
        self.calibrate_button.clicked.connect(self.start_calibration)
        layout.addWidget(self.calibrate_button)
        
        self.mode_button = QPushButton("Passer au mode Nez")
        self.mode_button.clicked.connect(self.toggle_mode)
        layout.addWidget(self.mode_button)
        
        # Curseurs
        self.click_slider = QSlider(Qt.Horizontal)
        self.click_slider.setRange(1, 10)
        self.click_slider.setValue(int(self.analyzer.click_threshold * 100))
        self.click_slider.valueChanged.connect(self.update_click_threshold)
        layout.addWidget(QLabel("Seuil de clic:"))
        layout.addWidget(self.click_slider)
        
        self.smooth_slider = QSlider(Qt.Horizontal)
        self.smooth_slider.setRange(10, 100)
        self.smooth_slider.setValue(int(self.controller.smooth_factor * 100))
        self.smooth_slider.valueChanged.connect(self.update_smooth_factor)
        layout.addWidget(QLabel("Lissage:"))
        layout.addWidget(self.smooth_slider)
        
        # Chatbot
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Posez une question...")
        self.chat_input.returnPressed.connect(self.process_chat_query)
        layout.addWidget(self.chat_input)
        
        self.chat_output = QLabel("Posez une question sur l'utilisation (ex. 'Comment défiler ?')")
        layout.addWidget(self.chat_output)
        
        # Statut
        self.status_label = QLabel("Statut: Prêt")
        layout.addWidget(self.status_label)
        
    def toggle(self):
        """Active ou désactive le contrôle."""
        self.running = not self.running
        self.video_thread.set_running(self.running)
        self.start_button.setText("Arrêter" if self.running else "Démarrer")
        self.status_label.setText(f"Statut: {'Actif' if self.running else 'Prêt'} (Mode: {self.control_mode})")
        
    def toggle_mode(self):
        """Bascule entre mode main et nez."""
        self.control_mode = "nose" if self.control_mode == "hand" else "hand"
        self.controller.set_control_mode(self.control_mode)
        self.video_thread.set_control_mode(self.control_mode)
        self.mode_button.setText("Passer au mode Nez" if self.control_mode == "hand" else "Passer au mode Main")
        self.status_label.setText(f"Statut: {'Actif' if self.running else 'Prêt'} (Mode: {self.control_mode})")
        
    def start_calibration(self):
        """Démarre la calibration."""
        self.calibrator_dialog = CalibratorDialog(self)
        self.calibrator_dialog.show()
        self.video_thread.start_calibration(self.control_mode)
        self.status_label.setText(f"Calibration ({self.control_mode}): Suivez les instructions")
        
    def update_click_threshold(self, value):
        """Met à jour le seuil de clic."""
        self.analyzer.click_threshold = value / 100.0
        self.config.set('controls', 'click_threshold', str(self.analyzer.click_threshold))
        with open('config/settings.ini', 'w') as configfile:
            self.config.write(configfile)
            
    def update_smooth_factor(self, value):
        """Met à jour le facteur de lissage."""
        self.controller.smooth_factor = value / 100.0
        self.config.set('controls', 'smooth_factor', str(self.controller.smooth_factor))
        with open('config/settings.ini', 'w') as configfile:
            self.config.write(configfile)
            
    def update_frame(self, frame):
        """Met à jour l'image affichée."""
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_image))
        
    def update_gesture_status(self, gesture):
        """Met à jour le statut avec le geste détecté."""
        self.status_label.setText(f"Statut: {'Actif' if self.running else 'Prêt'} (Mode: {self.control_mode}, Geste: {gesture})")
        
    def update_calibration_step(self, step):
        """Met à jour l'étape de calibration dans la fenêtre de dialogue."""
        if hasattr(self, 'calibrator_dialog'):
            self.calibrator_dialog.update_instruction(step)
        
    def process_chat_query(self):
        """Traite une requête du chatbot."""
        query = self.chat_input.text()
        response = self.faq_engine.process_query(query)
        self.chat_output.setText(response)
        
    def closeEvent(self, event):
        """Ferme proprement le thread vidéo."""
        self.video_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())