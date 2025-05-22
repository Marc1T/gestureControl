class GestureClassifier:
    def __init__(self):
        """Initialise le classificateur de gestes."""
        self.gesture_priority = ['DOUBLE_CLICK', 'LEFT_CLICK', 'RIGHT_CLICK', 'DRAG', 
                                'SCROLL_UP', 'SCROLL_DOWN', 'ZOOM_IN', 'ZOOM_OUT', 'MOVE']
        
    def classify(self, gestures):
        """Confirme et priorise les gestes détectés."""
        if not gestures or gestures == ['NONE']:
            return None
        # Retourne le geste avec la plus haute priorité
        for gesture in self.gesture_priority:
            if gesture in gestures:
                return gesture
        return None