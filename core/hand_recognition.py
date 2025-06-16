# core/hand_recognition.py
"""
Reconnaissance des gestes à partir des landmarks MediaPipe pour GestureMouseApp.
"""

from enum import IntEnum
import math
from pickle import NONE
from typing import Any, Optional

class Gest(IntEnum):
    # Encodage binaire : [Pouce][Index][Majeur][Annulaire][Auriculaire]
    # 0 = fermé, 1 = ouvert
    
    FIST = 0                      # 00000 - Tous doigts fermés
    PINKY = 1                     # 00001 - Seul auriculaire ouvert
    RING = 2                      # 00010 - Seul annulaire ouvert
    RING_PINKY = 3                # 00011 - Annulaire + auriculaire
    MID = 4                       # 00100 - Seul majeur ouvert
    MID_PINKY = 5                 # 00101 - Majeur + auriculaire
    MID_RING = 6                  # 00110 - Majeur + annulaire
    LAST3 = 7                     # 00111 - Majeur + annulaire + auriculaire
    INDEX = 8                     # 01000 - Seul index ouvert
    INDEX_PINKY = 9               # 01001 - Index + auriculaire
    INDEX_RING = 10               # 01010 - Index + annulaire
    INDEX_RING_PINKY = 11         # 01011 - Index + annulaire + auriculaire
    FIRST2 = 12                   # 01100 - Index + majeur
    FIRST2_PINKY = 13             # 01101 - Index + majeur + auriculaire
    FIRST3 = 14                   # 01110 - Index + majeur + annulaire
    LAST4 = 15                    # 01111 - Index + majeur + annulaire + auriculaire
    THUMB = 16                    # 10000 - Seul pouce ouvert
    THUMB_PINKY = 17              # 10001 - Pouce + auriculaire
    THUMB_RING = 18               # 10010 - Pouce + annulaire
    THUMB_RING_PINKY = 19         # 10011 - Pouce + annulaire + auriculaire
    THUMB_MID = 20                # 10100 - Pouce + majeur
    THUMB_MID_PINKY = 21          # 10101 - Pouce + majeur + auriculaire
    THUMB_MID_RING = 22           # 10110 - Pouce + majeur + annulaire
    THUMB_LAST3 = 23              # 10111 - Pouce + majeur + annulaire + auriculaire
    THUMB_INDEX = 24              # 11000 - Pouce + index
    THUMB_INDEX_PINKY = 25        # 11001 - Pouce + index + auriculaire
    THUMB_INDEX_RING = 26         # 11010 - Pouce + index + annulaire
    THUMB_INDEX_RING_PINKY = 27   # 11011 - Pouce + index + annulaire + auriculaire
    THUMB_FIRST2 = 28             # 11100 - Pouce + index + majeur
    THUMB_FIRST2_PINKY = 29       # 11101 - Pouce + index + majeur + auriculaire
    THUMB_FIRST3 = 30             # 11110 - Pouce + index + majeur + annulaire
    PALM = 31                     # 11111 - Tous doigts ouverts
    
    # Gestes spéciaux (valeurs hors binary encoding)
    V_GEST = 33                   # Geste "V" (index+majeur écartés)
    TWO_FINGER_CLOSED = 34        # Index+majeur collés
    PINCH_MAJOR = 35              # Pince majeur (pouce+index main dominante)
    PINCH_MINOR = 36              # Pince mineur (pouce+index main non-dominante)
    NONE = -1                     # Aucun geste détecté
    
class HLabel(IntEnum):
    MINOR = 0
    MAJOR = 1

class HandRecognizer:
    def __init__(self, config: Any, logger: Any, hand_label: HLabel) -> None:
        self.config = config
        self.logger = logger
        self.hand_label = hand_label
        self.finger = 0
        self.ori_gesture = Gest.PALM
        self.prev_gesture = Gest.PALM
        self.frame_count = 0
        self.hand_result = None
        self.logger.info(f"HandRecognizer initialisé (label={hand_label})")

    def update_hand_result(self, hand_result: Any) -> None:
        self.hand_result = hand_result

    def get_signed_dist(self, point: list) -> float:
        if not self.hand_result:
            return 0.0
        sign = -1
        if self.hand_result.landmark[point[0]].y < self.hand_result.landmark[point[1]].y:
            sign = 1
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
        dist = math.sqrt(dist)
        return dist * sign

    def get_dist(self, point: list) -> float:
        if not self.hand_result:
            return 0.0
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x)**2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y)**2
        dist = math.sqrt(dist)
        return dist

    def get_dz(self, point: list) -> float:
        if not self.hand_result:
            return 0.0
        return abs(self.hand_result.landmark[point[0]].z - self.hand_result.landmark[point[1]].z)

    def set_finger_state(self) -> None:
        if not self.hand_result:
            return

        points = [[8,5,0],[12,9,0],[16,13,0],[20,17,0]]
        self.finger = 0
        self.finger |= 0  # Thumb
        
        for idx, point in enumerate(points):
            dist1 = self.get_signed_dist(point[:2])
            dist2 = self.get_signed_dist(point[1:])
            
            try:
                ratio = round(dist1/dist2,1)
            except ZeroDivisionError:
                ratio = round(dist1/0.01,1)
            
            self.finger = self.finger << 1
            if ratio > self.config.get_setting("DEFAULT", "finger_ratio_threshold", 0.5):
                self.finger |= 1

    def get_gesture(self) -> Gest:
        if not self.hand_result:
            return Gest.PALM

        current_gesture = Gest.PALM
        pinch_dist_threshold = self.config.get_setting("DEFAULT", "pinch_dist_threshold", 0.05)
        vgest_ratio_threshold = self.config.get_setting("DEFAULT", "vgest_ratio_threshold", 1.7)
        dz_threshold = self.config.get_setting("DEFAULT", "dz_threshold", 0.1)

        # PINCH detection
        if self.finger in [Gest.LAST3, Gest.LAST4] and self.get_dist([8,4]) < pinch_dist_threshold:
            if self.hand_label == HLabel.MINOR:
                current_gesture = Gest.PINCH_MINOR
            else:
                current_gesture = Gest.PINCH_MAJOR

        # V_GEST detection
        elif self.finger == Gest.FIRST2:
            dist1 = self.get_dist([8,12])
            dist2 = self.get_dist([5,9])
            ratio = dist1/dist2 if dist2 != 0 else 0
            if ratio > vgest_ratio_threshold:
                current_gesture = Gest.V_GEST
            else:
                if self.get_dz([8,12]) < dz_threshold:
                    current_gesture = Gest.TWO_FINGER_CLOSED
                else:
                    current_gesture = Gest.MID
        else:
            current_gesture = Gest(self.finger)

        # Stabilization
        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture

        min_frames_confirm = self.config.get_setting("DEFAULT", "min_frames_confirm", 4)
        if self.frame_count > min_frames_confirm:
            self.ori_gesture = current_gesture
            
        return self.ori_gesture