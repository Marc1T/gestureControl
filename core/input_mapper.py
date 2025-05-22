import pyautogui
import json
import os

class InputMapper:
    def __init__(self, config_path="config/gesture_action_map.json", user_config_path="config/user_gesture_map.json"):
        """Initialise le mappage des gestes aux actions système."""
        self.gesture_map = self.load_gesture_map(config_path, user_config_path)
        self.dragging = False
        
    def load_gesture_map(self, config_path, user_config_path):
        """Charge le mappage des gestes depuis les fichiers JSON."""
        # Charger le mappage par défaut
        if not os.path.exists(config_path):
            default_map = {
                "MOVE": {"action": "move", "params": {}},
                "DRAG": {"action": "drag", "params": {}},
                "RIGHT_CLICK": {"action": "click", "params": {"button": "right"}},
                "LEFT_CLICK": {"action": "click", "params": {"button": "left"}},
                "DOUBLE_CLICK": {"action": "double_click", "params": {}},
                "SCROLL_UP": {"action": "scroll", "params": {"value": 100}},
                "SCROLL_DOWN": {"action": "scroll", "params": {"value": -100}},
                "ZOOM_IN": {"action": "hotkey", "params": {"keys": ["ctrl", "+"]}},
                "ZOOM_OUT": {"action": "hotkey", "params": {"keys": ["ctrl", "-"]}}
            }
            with open(config_path, 'w') as f:
                json.dump(default_map, f, indent=4)
        else:
            with open(config_path, 'r') as f:
                default_map = json.load(f)
                
        # Charger le mappage utilisateur (surcharge)
        if os.path.exists(user_config_path):
            with open(user_config_path, 'r') as f:
                user_map = json.load(f)
            default_map.update(user_map)
            
        return default_map
            
    def execute(self, gesture, last_click):
        """Exécute l'action associée au geste."""
        if gesture not in self.gesture_map:
            return
            
        action = self.gesture_map[gesture]["action"]
        params = self.gesture_map[gesture]["params"]
        
        if action == "move":
            pass  # Le mouvement est géré dans cursor_controller
        elif action == "drag":
            if not self.dragging:
                pyautogui.mouseDown()
                self.dragging = True
        elif action == "click":
            pyautogui.click(button=params["button"])
            if self.dragging:
                pyautogui.mouseUp()
                self.dragging = False
        elif action == "double_click":
            pyautogui.doubleClick()
            if self.dragging:
                pyautogui.mouseUp()
                self.dragging = False
        elif action == "scroll":
            pyautogui.scroll(params["value"])
        elif action == "hotkey":
            pyautogui.hotkey(*params["keys"])