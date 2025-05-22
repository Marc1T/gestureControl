import numpy as np

class KalmanFilter:
    def __init__(self, process_noise=0.01, measurement_noise=0.1):
        """Initialise le filtre de Kalman pour lisser les coordonnées."""
        # Matrice d'état : [x, y, vx, vy] (position et vitesse)
        self.state = np.zeros((4, 1), dtype=np.float32)
        # Matrice de transition d'état
        self.transition_matrix = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        # Matrice d'observation : observe seulement x, y
        self.measurement_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)
        # Bruit de processus
        self.process_noise_cov = process_noise * np.eye(4, dtype=np.float32)
        # Bruit de mesure
        self.measurement_noise_cov = measurement_noise * np.eye(2, dtype=np.float32)
        # Matrice de covariance
        self.error_cov = np.eye(4, dtype=np.float32)
        
    def filter(self, x, y):
        """Applique le filtre de Kalman aux coordonnées x, y."""
        # Mesure
        measurement = np.array([[x], [y]], dtype=np.float32)
        
        # Prédiction
        self.state = np.dot(self.transition_matrix, self.state)
        self.error_cov = np.dot(np.dot(self.transition_matrix, self.error_cov), 
                               self.transition_matrix.T) + self.process_noise_cov
                               
        # Mise à jour
        kalman_gain = np.dot(np.dot(self.error_cov, self.measurement_matrix.T), 
                            np.linalg.inv(
                                np.dot(np.dot(self.measurement_matrix, self.error_cov), 
                                      self.measurement_matrix.T) + self.measurement_noise_cov
                            ))
        self.state = self.state + np.dot(kalman_gain, 
                                        measurement - np.dot(self.measurement_matrix, self.state))
        self.error_cov = self.error_cov - np.dot(np.dot(kalman_gain, self.measurement_matrix), 
                                                self.error_cov)
                                                
        # Retourner les coordonnées lissées
        return self.state[0, 0], self.state[1, 0]
