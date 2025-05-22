import cv2
import numpy as np

class Calibrator:
    def __init__(self):
        """Initialise la calibration pour les modes main et nez."""
        self.calibration_data = {"hand": [], "nose": []}
        
    def set_calibration_points(self, mode, points):
        """Définit les points de calibration."""
        print(f"Calibration points for {mode}: {points}")  # Log pour débogage
        self.calibration_data[mode] = points
        
    def calibrate(self, mode, x, y):
        """Applique la calibration aux coordonnées avec transformation homographique."""
        if len(self.calibration_data[mode]) != 4:
            return x, y
            
        # Points source (capturés par la caméra)
        src_pts = np.float32(self.calibration_data[mode])
        # Points destination (coins normalisés de l'écran : 0 à 1)
        dst_pts = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
        
        # Calculer la matrice de transformation homographique
        try:
            matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
            # Appliquer la transformation à la coordonnée (x, y)
            point = cv2.perspectiveTransform(np.float32([[[x, y]]]), matrix)
            norm_x, norm_y = point[0][0][0], point[0][0][1]
            # Limiter les valeurs entre 0 et 1
            return max(0, min(1, norm_x)), max(0, min(1, norm_y))
        except cv2.error:
            print("Erreur dans la transformation homographique, retour aux coordonnées brutes")
            return x, y
