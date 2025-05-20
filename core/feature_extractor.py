class FeatureExtractor:
    def __init__(self):
        """Initialise l'extracteur de caractéristiques."""
        pass
        
    def extract_hand_features(self, landmarks):
        """Extrait les caractéristiques des landmarks de la main."""
        if not landmarks:
            return None
            
        features = {}
        # Points clés : poignet (0), pouce (4), index (8), majeur (12), auriculaire (20)
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        index_mcp = landmarks[5]  # Articulation de base de l'index
        middle_mcp = landmarks[9]  # Articulation de base du majeur
        pinky_mcp = landmarks[17]  # Articulation de base de l'auriculaire
        
        # Distance pouce-index (pour clic droit, zoom)
        features['thumb_index_dist'] = ((thumb_tip.x - index_tip.x) ** 2 + 
                                      (thumb_tip.y - index_tip.y) ** 2) ** 0.5
                                      
        # Position y de l'auriculaire (pour défilement)
        features['pinky_y'] = pinky_tip.y
        
        # État des doigts (levés ou repliés)
        features['index_raised'] = index_tip.y < index_mcp.y
        features['middle_raised'] = middle_tip.y < middle_mcp.y
        features['pinky_raised'] = pinky_tip.y < pinky_mcp.y
        features['other_fingers_folded'] = (ring_tip.y > landmarks[13].y and 
                                         thumb_tip.y > landmarks[2].y and 
                                         (not features['index_raised'] or not features['middle_raised'] or not features['pinky_raised']))
                                         
        # Poing fermé (pour glisser-déposer)
        features['fist'] = (features['thumb_index_dist'] < 0.1 and 
                           ring_tip.y > landmarks[13].y and 
                           pinky_tip.y > landmarks[17].y and 
                           index_tip.y > landmarks[6].y and 
                           middle_tip.y > landmarks[10].y)
                           
        # Geste OK (pouce-index proches, autres doigts levés)
        features['ok_gesture'] = (features['thumb_index_dist'] < 0.05 and 
                                ring_tip.y < landmarks[13].y and 
                                pinky_tip.y < landmarks[17].y)
                                
        # Coordonnées de l'index pour le curseur
        features['index_pos'] = (index_tip.x, index_tip.y)
        
        return features
        
    def extract_face_features(self, landmarks):
        """Extrait les caractéristiques des landmarks du visage."""
        if not landmarks:
            return None
            
        features = {}
        # Pointe du nez (landmark 1)
        nose_tip = landmarks[1]
        features['nose_pos'] = (nose_tip.x, nose_tip.y)
        
        return features