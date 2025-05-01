class Calibrator:
    def __init__(self):
        """Initialise la calibration pour les modes main et nez."""
        self.calibration_data = {"hand": [], "nose": []}
        
    def set_calibration_points(self, mode, points):
        """Définit les points de calibration."""
        self.calibration_data[mode] = points
        
    def calibrate(self, mode, x, y):
        """Applique la calibration aux coordonnées."""
        if len(self.calibration_data[mode]) != 4:
            return x, y
            
        points = self.calibration_data[mode]
        min_x, max_x = min(p[0] for p in points), max(p[0] for p in points)
        min_y, max_y = min(p[1] for p in points), max(p[1] for p in points)
        
        if max_x == min_x or max_y == min_y:
            return x, y
            
        norm_x = (x - min_x) / (max_x - min_x)
        norm_y = (y - min_y) / (max_y - min_y)
        
        return max(0, min(1, norm_x)), max(0, min(1, norm_y))