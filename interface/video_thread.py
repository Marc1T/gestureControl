import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

class VideoThread(QThread):
    frame_updated = pyqtSignal(np.ndarray)
    gesture_detected = pyqtSignal(str)
    calibration_step_updated = pyqtSignal(int)
    
    def __init__(self, hand_tracker, face_tracker, feature_extractor, gesture_analyzer, gesture_classifier, cursor_controller):
        super().__init__()
        self.hand_tracker = hand_tracker
        self.face_tracker = face_tracker
        self.feature_extractor = feature_extractor
        self.gesture_analyzer = gesture_analyzer
        self.gesture_classifier = gesture_classifier
        self.cursor_controller = cursor_controller
        self.running = False
        self.control_mode = "hand"
        self.calibrating = False
        self.calibration_mode = None
        self.calibration_points = []
        self.cap = cv2.VideoCapture(0)
        
    def set_running(self, running):
        """Active ou désactive le traitement."""
        self.running = running
        
    def set_control_mode(self, mode):
        """Change le mode de contrôle."""
        self.control_mode = mode
        
    def start_calibration(self, mode):
        """Démarre la calibration."""
        self.calibrating = True
        self.calibration_mode = mode
        self.calibration_points = []
        self.calibration_step_updated.emit(0)  # Première étape
        
    def run(self):
        """Boucle principale du thread vidéo."""
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            if self.calibrating:
                frame_rgb = self.handle_calibration(frame_rgb)
            elif self.running:
                self.process_frame(frame)
                
            self.frame_updated.emit(frame_rgb)
            self.msleep(15)  # ~60 FPS
            
    def handle_calibration(self, frame):
        """Gère le processus de calibration avec feedback visuel."""
        if self.calibration_mode == "hand":
            landmarks, _ = self.hand_tracker.process(frame)
            if landmarks:
                features = self.feature_extractor.extract_hand_features(landmarks[0].landmark)
                if features:
                    x, y = features['index_pos']
                    # Dessiner un cercle pour le feedback visuel
                    cv2.circle(frame, (int(x * frame.shape[1]), int(y * frame.shape[0])), 10, (0, 255, 0), -1)
                    self.calibration_points.append(features['index_pos'])
                    self.calibration_step_updated.emit(len(self.calibration_points))
        elif self.calibration_mode == "nose":
            face_landmarks = self.face_tracker.process(frame)
            if face_landmarks:
                features = self.feature_extractor.extract_face_features(face_landmarks[0].landmark)
                if features:
                    x, y = features['nose_pos']
                    # Dessiner un cercle pour le feedback visuel
                    cv2.circle(frame, (int(x * frame.shape[1]), int(y * frame.shape[0])), 10, (0, 255, 0), -1)
                    self.calibration_points.append(features['nose_pos'])
                    self.calibration_step_updated.emit(len(self.calibration_points))
                    
        if len(self.calibration_points) >= 4:
            self.cursor_controller.calibrator.set_calibration_points(self.calibration_mode, self.calibration_points)
            self.calibrating = False
            
        return frame
                                               
    def process_frame(self, frame):
        """Traite une image pour le contrôle."""
        if self.control_mode == "hand":
            landmarks, handedness = self.hand_tracker.process(frame)
            if landmarks:
                for i, hand_landmarks in enumerate(landmarks):
                    if not handedness or handedness[i].classification[0].label == "Right":
                        features = self.feature_extractor.extract_hand_features(hand_landmarks.landmark)
                        if features:
                            gestures = self.gesture_analyzer.analyze(features)
                            gesture = self.gesture_classifier.classify(gestures)
                            self.cursor_controller.update(features['index_pos'][0], 
                                                       features['index_pos'][1], 
                                                       gesture)
                            self.gesture_detected.emit(gesture if gesture else "NONE")
                        break
        elif self.control_mode == "nose":
            face_landmarks = self.face_tracker.process(frame)
            if face_landmarks:
                features = self.feature_extractor.extract_face_features(face_landmarks[0].landmark)
                if features:
                    self.cursor_controller.update(features['nose_pos'][0], 
                                               features['nose_pos'][1], 
                                               None)
                    self.gesture_detected.emit("NONE")
                                               
    def stop(self):
        """Arrête le thread et libère la caméra."""
        self.running = False
        self.cap.release()
        self.quit()
        self.wait()