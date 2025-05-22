import numpy as np

class FeatureExtractor:
    def __init__(self):
        """Initialise l'extracteur de caractéristiques."""
        pass
        
    def extract_hand_features(self, landmarks, multi_landmarks=None, multi_handedness=None):
        """Extrait les caractéristiques des landmarks de la main."""
        if not landmarks and not multi_landmarks:
            return None
            
        features = {}
        if multi_landmarks and len(multi_landmarks) >= 2 and multi_handedness:  # Deux mains pour zoom
            # Identifier main gauche et droite via handedness
            left_hand = None
            right_hand = None
            for i, hand_landmarks in enumerate(multi_landmarks):
                if i < len(multi_handedness) and multi_handedness[i].classification[0].label == "Left":
                    left_hand = hand_landmarks.landmark
                elif i < len(multi_handedness) and multi_handedness[i].classification[0].label == "Right":
                    right_hand = hand_landmarks.landmark
                    
            if left_hand and right_hand:
                left_index = left_hand[8]
                right_index = right_hand[8]
                features['index_distance'] = ((left_index.x - right_index.x) ** 2 + 
                                            (left_index.y - right_index.y) ** 2) ** 0.5
            else:
                features['index_distance'] = None
        else:
            features['index_distance'] = None
            
        # Points clés pour une main (droite par défaut)
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        
        # Distances pour pincements
        features['thumb_index_dist'] = ((thumb_tip.x - index_tip.x) ** 2 + 
                                      (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        features['thumb_middle_dist'] = ((thumb_tip.x - middle_tip.x) ** 2 + 
                                       (thumb_tip.y - middle_tip.y) ** 2) ** 0.5
                                       
        # État des doigts
        features['open_hand'] = (index_tip.y < index_mcp.y and 
                                middle_tip.y < middle_mcp.y and 
                                ring_tip.y < landmarks[13].y and 
                                pinky_tip.y < landmarks[17].y)
        features['fist'] = (features['thumb_index_dist'] < 0.1 and 
                           ring_tip.y > landmarks[13].y and 
                           pinky_tip.y > landmarks[17].y and 
                           index_tip.y > landmarks[6].y and 
                           middle_tip.y > landmarks[10].y)
        features['two_fingers'] = (index_tip.y < index_mcp.y and 
                                  middle_tip.y < middle_mcp.y and 
                                  ring_tip.y > landmarks[13].y and 
                                  pinky_tip.y > landmarks[17].y)
                                  
        # Position de la paume pour déplacement
        features['palm_pos'] = ((wrist.x + index_tip.x) / 2, (wrist.y + index_tip.y) / 2)
        
        return features
        
    def extract_face_features(self, landmarks):
        """Extrait les caractéristiques des landmarks du visage."""
        if not landmarks:
            return None
            
        features = {}
        nose_tip = landmarks[1]
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        features['nose_pos'] = (nose_tip.x, nose_tip.y)
        features['eye_dist'] = (left_eye_top.y - left_eye_bottom.y)
        features['nose_y'] = nose_tip.y
        
        return features