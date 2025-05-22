import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_num_hands=2):
        """Initialise le suivi des mains avec MediaPipe."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.5
        )
        self.image_width = None
        self.image_height = None
        
    def process(self, frame):
        """Traite une image et retourne les points de repère des mains."""
        if frame is None or frame.size == 0:
            return None, None
            
        # Stocker les dimensions de l'image
        self.image_width, self.image_height = frame.shape[1], frame.shape[0]
        
        # Ajuster la frame pour une ROI carrée
        size = min(self.image_width, self.image_height)
        x_offset = (self.image_width - size) // 2
        y_offset = (self.image_height - size) // 2
        square_frame = frame[y_offset:y_offset + size, x_offset:x_offset + size]
        
        # Convertir en RGB
        rgb = cv2.cvtColor(square_frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False  # Nécessaire pour MediaPipe
        
        # Traiter avec MediaPipe
        results = self.hands.process(rgb)
        
        # Ajuster les coordonnées des landmarks pour la frame originale
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    # Décaler et redimensionner les coordonnées normalisées
                    landmark.x = (landmark.x * size + x_offset) / self.image_width
                    landmark.y = (landmark.y * size + y_offset) / self.image_height
                    
        return results.multi_hand_landmarks, results.multi_handedness
    
    def draw_landmarks(self, frame, landmarks):
        """Dessine les points de repère sur l'image."""
        if landmarks:
            for hand_landmarks in landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return frame