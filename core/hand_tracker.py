import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_num_hands=2):
        """Initialise le suivi des mains avec MediaPipe."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=0.9,
            min_tracking_confidence=0.7
        )
        
    def process(self, frame):
        """Traite une image et retourne les points de repère des mains."""
        if frame is None or frame.size == 0:
            return None, None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        return results.multi_hand_landmarks, results.multi_handedness
    
    def draw_landmarks(self, frame, landmarks):
        """Dessine les points de repère sur l'image."""
        if landmarks:
            for hand_landmarks in landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return frame