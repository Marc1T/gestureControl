import time

class GestureAnalyzer:
    def __init__(self, click_threshold=0.05, scroll_threshold=0.1, zoom_threshold=0.05, gesture_delay=0.3):
        """Initialise l'analyseur de gestes avec des seuils."""
        self.click_threshold = click_threshold
        self.scroll_threshold = scroll_threshold
        self.zoom_threshold = zoom_threshold
        self.gesture_delay = gesture_delay
        self.prev_nose_y = None
        self.prev_index_distance = None
        self.last_pinch_time = None
        self.pinch_count = 0
        self.gesture_start_time = {}
        self.current_gesture = None
        
    def analyze(self, features, control_mode="hand"):
        """Analyse les caractéristiques pour détecter des gestes."""
        if not features:
            return []
            
        gestures = []
        current_time = time.time()
        self.control_mode = control_mode
        
        if self.control_mode == "hand":
            # Vérifier temporisation pour chaque geste
            def check_gesture(gesture_name, condition):
                if condition:
                    if gesture_name not in self.gesture_start_time:
                        self.gesture_start_time[gesture_name] = current_time
                    elif current_time - self.gesture_start_time[gesture_name] > self.gesture_delay:
                        return True
                else:
                    self.gesture_start_time.pop(gesture_name, None)
                return False
                
            # Déplacement : main ouverte
            if check_gesture('MOVE', features['open_hand']):
                gestures.append('MOVE')
                
            # Glisser-déposer : poing fermé
            if check_gesture('DRAG', features['fist']):
                gestures.append('DRAG')
                
            # Clic gauche : pincer pouce-index
            if check_gesture('LEFT_CLICK', features['thumb_index_dist'] < self.click_threshold):
                gestures.append('LEFT_CLICK')
                # Vérifier double-clic
                if self.last_pinch_time is not None and current_time - self.last_pinch_time < 0.7:
                    self.pinch_count += 1
                    if self.pinch_count >= 2:
                        gestures.append('DOUBLE_CLICK')
                        self.pinch_count = 0
                self.last_pinch_time = current_time
            else:
                self.pinch_count = 0
                
            # Clic droit : pincer pouce-majeur
            if check_gesture('RIGHT_CLICK', features['thumb_middle_dist'] < self.click_threshold):
                gestures.append('RIGHT_CLICK')
                
            # Défilement : deux doigts levés
            if check_gesture('SCROLL', features['two_fingers']) and 'palm_pos' in features and self.prev_palm_y is not None:
                delta_y = features['palm_pos'][1] - self.prev_palm_y
                if delta_y < -self.scroll_threshold:
                    gestures.append('SCROLL_UP')
                elif delta_y > self.scroll_threshold:
                    gestures.append('SCROLL_DOWN')
            self.prev_palm_y = features['palm_pos'][1] if 'palm_pos' in features else None
            
            # Zoom : deux mains
            if features['index_distance'] is not None and self.prev_index_distance is not None:
                delta_dist = features['index_distance'] - self.prev_index_distance
                if delta_dist > self.zoom_threshold:
                    gestures.append('ZOOM_OUT')
                elif delta_dist < -self.zoom_threshold:
                    gestures.append('ZOOM_IN')
            self.prev_index_distance = features['index_distance']
            
        elif self.control_mode == "nose":
            # Clic gauche : clignement d'œil
            if features['eye_dist'] < 0.01:  # Seuil pour clignement
                gestures.append('LEFT_CLICK')
                
            # Défilement : hochement de tête
            if self.prev_nose_y is not None:
                delta_y = features['nose_y'] - self.prev_nose_y
                if delta_y < -self.scroll_threshold:
                    gestures.append('SCROLL_UP')
                elif delta_y > self.scroll_threshold:
                    gestures.append('SCROLL_DOWN')
            self.prev_nose_y = features['nose_y']
        
        return gestures if gestures else ['NONE']