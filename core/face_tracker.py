import cv2
import mediapipe as mp

class FaceTracker:
    def __init__(self):
        """Initialise le suivi du visage avec MediaPipe Face Mesh."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.9,
            min_tracking_confidence=0.7
        )
        
    def process(self, frame):
        """Traite une image et retourne les points de repère du visage."""
        if frame is None or frame.size == 0:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        return results.multi_face_landmarks
    
    def draw_landmarks(self, frame, landmarks):
        """Dessine les points de repère du visage (optionnel)."""
        if landmarks:
            for face_landmarks in landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION)
        return frame