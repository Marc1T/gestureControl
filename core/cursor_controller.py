import pyautogui
import time
from utils.calibrator import Calibrator
from utils.kalman_filter import KalmanFilter
from core.input_mapper import InputMapper

class CursorController:
    def __init__(self, smooth_factor=0.3, control_mode="hand"):
        """Initialise le contrôleur de curseur."""
        self.screen_w, self.screen_h = pyautogui.size()
        self.last_click = 0
        self.smooth_factor = smooth_factor
        self.control_mode = control_mode
        self.calibrator = Calibrator()
        self.kalman = KalmanFilter()
        self.input_mapper = InputMapper()
        
    def set_control_mode(self, mode):
        """Change le mode de contrôle (main ou nez)."""
        self.control_mode = mode
        
    def update(self, x, y, gesture=None):
        """Met à jour la position du curseur et exécute les gestes."""
        # Calibration
        x, y = self.calibrator.calibrate(self.control_mode, x, y)
        
        # Filtrage Kalman pour lisser
        x, y = self.kalman.filter(x, y)
        
        # Lissage supplémentaire
        current_x, current_y = pyautogui.position()
        target_x = int(x * self.screen_w)
        target_y = int(y * self.screen_h)
        smooth_x = current_x + (target_x - current_x) * self.smooth_factor
        smooth_y = current_y + (target_y - current_y) * self.smooth_factor
        pyautogui.moveTo(smooth_x, smooth_y)
        
        # Exécuter le geste
        if gesture:
            self.input_mapper.execute(gesture, self.last_click)
            if gesture in ['LEFT_CLICK', 'RIGHT_CLICK']:
                self.last_click = time.time()