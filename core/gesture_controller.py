# core/gesture_controller.py
"""
Contrôle des actions système basées sur les gestes pour GestureMouseApp.
"""
import math
import pyautogui
from typing import Any, Optional, Tuple, Callable
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbcontrol
from .hand_recognition import Gest, HLabel

pyautogui.FAILSAFE = False

class GestureController:
    def __init__(self, config: Any, logger: Any) -> None:
        self.config = config
        self.logger = logger
        self.tx_old = 0
        self.ty_old = 0
        self.flag = False
        self.drabflag = False
        self.pinchmajorflag = False
        self.pinchminorflag = False
        self.pinchstartxcoord = None
        self.pinchstartycoord = None
        self.pinchdirectionflag = None
        self.prevpinchlv = 0
        self.pinchlv = 0
        self.framecount = 0
        self.prev_hand = None
        self.logger.info("GestureController initialisé")

    def get_pinch_y_lv(self, hand_result: Any) -> float:
        if self.pinchstartycoord is None:
            return 0.0
        return round((self.pinchstartycoord - hand_result.landmark[8].y) * 10, 1)

    def get_pinch_x_lv(self, hand_result: Any) -> float:
        if self.pinchstartxcoord is None:
            return 0.0
        return round((hand_result.landmark[8].x - self.pinchstartxcoord) * 10, 1)

    def change_system_volume(self) -> None:
        try:
            devices = AudioUtilities.GetSpeakers()
            if not devices:
                self.logger.error("Aucun périphérique audio détecté")
                return

            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            if volume is None:
                self.logger.error("Impossible d'accéder au contrôle du volume")
                return

            # Récupérer le volume actuel
            current_volume = volume.GetMasterVolumeLevelScalar() # type: ignore
            if not isinstance(current_volume, float):  # Vérification du type
                self.logger.error(f"Valeur de volume inattendue : {current_volume}")
                return

            # Ajustement du volume
            pinch_value = float(self.pinchlv) if hasattr(self, "pinchlv") else 0.0
            new_volume = max(0.0, min(1.0, current_volume + pinch_value / 50.0))

            volume.SetMasterVolumeLevelScalar(new_volume, None) # type: ignore
            self.logger.info(f"Volume ajusté à {new_volume * 100:.2f}%")

        except Exception as e:
            self.logger.error(f"Erreur ajustement volume : {str(e)}", exc_info=True)

    def change_system_brightness(self) -> None:
        try:
            current_brightness = sbcontrol.get_brightness()
            # Gestion du cas où get_brightness() retourne une liste
            if isinstance(current_brightness, list):
                current_brightness = current_brightness[0]
                
            current_brightness = float(current_brightness) / 100.0
            current_brightness += self.pinchlv / 50.0
            current_brightness = max(0.0, min(1.0, current_brightness))
            sbcontrol.set_brightness(int(100 * current_brightness))
        except Exception as e:
            self.logger.error(f"Erreur ajustement luminosité : {str(e)}")

    def scroll_vertical(self) -> None:
        pyautogui.scroll(120 if self.pinchlv > 0.0 else -120)

    def scroll_horizontal(self) -> None:
        pyautogui.keyDown('shift')
        pyautogui.keyDown('ctrl')
        pyautogui.scroll(-120 if self.pinchlv > 0.0 else 120)
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')

    def get_position(self, hand_result: Any) -> Tuple[float, float]:
        point = 9
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)
        
        if self.prev_hand is None:
            self.prev_hand = x, y
        
        delta_x = x - self.prev_hand[0]
        delta_y = y - self.prev_hand[1]
        
        distsq = delta_x**2 + delta_y**2
        ratio = 1
        self.prev_hand = [x, y]

        if distsq <= 25:
            ratio = 0
        elif distsq <= 900:
            ratio = 0.07 * math.sqrt(distsq)
        else:
            ratio = 2.1
        
        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio
        
        return (x, y)

    def pinch_control_init(self, hand_result: Any) -> None:
        self.pinchstartxcoord = hand_result.landmark[8].x
        self.pinchstartycoord = hand_result.landmark[8].y
        self.pinchlv = 0
        self.prevpinchlv = 0
        self.framecount = 0

    def pinch_control(self, hand_result: Any, controlHorizontal: Callable[[], None], controlVertical: Callable[[], None]) -> None:
        if self.framecount == 5:
            self.framecount = 0
            self.pinchlv = self.prevpinchlv
            if self.pinchdirectionflag:
                controlHorizontal()
            else:
                controlVertical()

        lvx = self.get_pinch_x_lv(hand_result)
        lvy = self.get_pinch_y_lv(hand_result)
        pinch_threshold = self.config.get_setting("DEFAULT", "pinch_threshold", 0.3)

        if abs(lvy) > abs(lvx) and abs(lvy) > pinch_threshold:
            self.pinchdirectionflag = False
            if abs(self.prevpinchlv - lvy) < pinch_threshold:
                self.framecount += 1
            else:
                self.prevpinchlv = lvy
                self.framecount = 0

        elif abs(lvx) > pinch_threshold:
            self.pinchdirectionflag = True
            if abs(self.prevpinchlv - lvx) < pinch_threshold:
                self.framecount += 1
            else:
                self.prevpinchlv = lvx
                self.framecount = 0

    def handle_gesture(self, gesture: Any, hand_result: Any, hand_label: HLabel) -> None:
        x, y = None, None
        
        if gesture != Gest.PALM:
            x, y = self.get_position(hand_result)
        
        # Reset flags
        if gesture != Gest.FIST and self.drabflag:
            self.drabflag = False
            pyautogui.mouseUp(button="left")
            
        if gesture != Gest.PINCH_MAJOR and self.pinchmajorflag:
            self.pinchmajorflag = False
            
        if gesture != Gest.PINCH_MINOR and self.pinchminorflag:
            self.pinchminorflag = False

        # Handle gestures
        if gesture == Gest.V_GEST:
            self.flag = True
            if x and y:
                pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Gest.FIST:
            if not self.drabflag: 
                self.drabflag = True
                pyautogui.mouseDown(button="left")
            if x and y:
                pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Gest.MID and self.flag:
            pyautogui.click()
            self.flag = False

        elif gesture == Gest.INDEX and self.flag:
            pyautogui.click(button='right')
            self.flag = False

        elif gesture == Gest.TWO_FINGER_CLOSED and self.flag:
            pyautogui.doubleClick()
            self.flag = False

        elif gesture == Gest.PINCH_MINOR:
            if not self.pinchminorflag:
                self.pinch_control_init(hand_result)
                self.pinchminorflag = True
            self.pinch_control(hand_result, self.scroll_horizontal, self.scroll_vertical)
        
        elif gesture == Gest.PINCH_MAJOR:
            if not self.pinchmajorflag:
                self.pinch_control_init(hand_result)
                self.pinchmajorflag = True
            self.pinch_control(hand_result, self.change_system_brightness, self.change_system_volume)