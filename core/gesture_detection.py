# core/gesture_detection.py
"""
Détection des mains et capture vidéo pour GestureMouseApp.
"""

import cv2
import mediapipe as mp
from typing import Any, Optional, Tuple
from google.protobuf.json_format import MessageToDict
from utils.helpers import opencv_to_qimage
from PyQt5.QtGui import QImage
import threading
import numpy as np

mp_hands = mp.solutions.hands             # type: ignore
mp_drawing = mp.solutions.drawing_utils   # type: ignore

class GestureDetector:
    def __init__(self, config: Any, logger: Any) -> None:
        self.config = config
        self.logger = logger
        self.cap: Optional[cv2.VideoCapture] = None
        threshold = float(self.config.get_setting("DEFAULT", "threshold", 50))/100
        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=threshold,
            min_tracking_confidence=threshold
        )
        self.camera_index = int(self.config.get_setting("DEFAULT", "camera_index", 0))
        self.show_landmarks = bool(self.config.get_setting("DEFAULT", "show_landmarks", True))
        self.major_hand = None
        self.minor_hand = None
        self.logger.info("GestureDetector initialisé")
        self._lock = threading.Lock()

    def start(self) -> bool:
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                self.logger.error(f"Impossible d'ouvrir la caméra {self.camera_index}")
                return False
            self.logger.info(f"Capture vidéo démarrée (caméra {self.camera_index})")
            return True
        except Exception as e:
            self.logger.error(f"Erreur démarrage capture vidéo : {e}")
            return False

    def stop(self) -> None:
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.logger.info("Capture vidéo arrêtée")

    def update_camera(self, camera_index: int) -> bool:
        with self._lock:  # Bloque pendant la modification
            try:
                self.stop()
                self.camera_index = camera_index
                return self.start()
            except Exception as e:
                self.logger.error(f"Erreur mise à jour caméra : {e}")
                return False

    def process_frame(self) -> Tuple[Optional[np.ndarray], Optional[Any]]:
        try:
            if not self.cap or not self.cap.isOpened():
                self.logger.warning("Caméra non ouverte")
                return None, None

            ret, image = self.cap.read()
            if not ret:
                self.logger.warning("Échec lecture frame")
                return None, None

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            self._classify_hands(results)

            if results.multi_hand_landmarks and self.show_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # q_image = opencv_to_qimage(image)
            return image, results

        except Exception as e:
            self.logger.error(f"Erreur traitement frame : {e}")
            return None, None

    def _classify_hands(self, results: Any) -> None:
        self.major_hand = None
        self.minor_hand = None
        if not results.multi_hand_landmarks:
            return

        dominant_hand = self.config.get_setting("DEFAULT", "dominant_hand", "Droite").lower() == "droite"

        left, right = None, None
        try:
            for i, handedness in enumerate(results.multi_handedness):
                handedness_dict = MessageToDict(handedness)
                label = handedness_dict['classification'][0]['label']
                if label == 'Right':
                    right = results.multi_hand_landmarks[i]
                elif label == 'Left':
                    left = results.multi_hand_landmarks[i]
        except Exception as e:
            self.logger.error(f"Erreur classification mains : {e}")

        if dominant_hand:
            self.major_hand = right
            self.minor_hand = left
        else:
            self.major_hand = left
            self.minor_hand = right