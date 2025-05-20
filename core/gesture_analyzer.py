import time

class GestureAnalyzer:
    def __init__(self, click_threshold=0.05, scroll_threshold=0.1, zoom_threshold=0.05):
        """Initialise l'analyseur de gestes avec des seuils."""
        self.click_threshold = click_threshold
        self.scroll_threshold = scroll_threshold
        self.zoom_threshold = zoom_threshold
        self.prev_pinky_y = None
        self.prev_thumb_index_dist = None
        self.last_ok_time = None
        self.ok_count = 0
        
    def analyze(self, features):
        """Analyse les caractéristiques pour détecter des gestes."""
        if not features:
            return []
            
        gestures = []
        current_time = time.time()
        
        # Déplacement du curseur : index levé, autres doigts repliés
        if features['index_raised'] and features['other_fingers_folded']:
            gestures.append('MOVE')
            
        # Glisser-déposer : poing fermé
        # if features['fist']:
        #     gestures.append('DRAG')
        
        # Clic gauche : majeur levé, autres doigts repliés
        if features['ok_gesture']:
            gestures.append('LEFT_CLICK')
            # Vérifier double-clic
            if self.last_ok_time is not None and current_time - self.last_ok_time < 0.5:
                self.ok_count += 1
                if self.ok_count >= 2:
                    gestures.append('DOUBLE_CLICK')
                    self.ok_count = 0
            self.last_ok_time = current_time
        else:
            self.ok_count = 0
            
        # Clic droit : geste OK
        if features['middle_raised'] and features['other_fingers_folded']:
            gestures.append('RIGHT_CLICK')
            
        # Défilement : auriculaire levé, mouvement vertical
        # if features['pinky_raised'] and features['other_fingers_folded'] and self.prev_pinky_y is not None:
        #     delta_y = features['pinky_y'] - self.prev_pinky_y
        #     if delta_y < -self.scroll_threshold:
        #         gestures.append('SCROLL_UP')
        #     elif delta_y > self.scroll_threshold:
        #         gestures.append('SCROLL_DOWN')
        # self.prev_pinky_y = features['pinky_y']
        
        # Zoom : changement distance pouce-index
        # if self.prev_thumb_index_dist is not None:
        #     delta_dist = features['thumb_index_dist'] - self.prev_thumb_index_dist
        #     if delta_dist > self.zoom_threshold and not features['ok_gesture']:
        #         gestures.append('ZOOM_OUT')
        #     elif delta_dist < -self.zoom_threshold and not features['ok_gesture']:
        #         gestures.append('ZOOM_IN')
        # self.prev_thumb_index_dist = features['thumb_index_dist']
        
        return gestures if gestures else ['NONE']