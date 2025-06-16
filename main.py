# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from utils.config_manager import ConfigManager
from utils.logger import Logger
from chatbot.faq_bot import FAQBot
from interface.main_window import MainWindow
from interface.video_thread import VideoThread
import logging
import os

import os
import ctypes

# Augmenter la limite de récursion
sys.setrecursionlimit(10000)

# Solution pour sqlite3
try:
    # Essayer d'importer normalement
    from sqlite3 import dbapi2 as sqlite
except ImportError:
    # Solution de secours
    dll_path = os.path.join(os.path.dirname(__file__), 'dlls', 'sqlite3.dll')
    if os.path.exists(dll_path):
        ctypes.WinDLL(dll_path)
        from sqlite3 import dbapi2 as sqlite

def resource_path(relative_path):
    """ Convertit un chemin relatif en chemin absolu pour PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger(__name__)
    logger.critical("Exception non capturée", 
                    exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(
        None,
        "Erreur Critique",
        f"Une erreur inattendue est survenue:\n{str(exc_value)}\n\nVoir les logs pour plus de détails."
    )
    sys.exit(1)

def main():
    try:
        sys.excepthook = handle_uncaught_exception
        
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        config = ConfigManager(
            resource_path("config/settings.ini"),
            resource_path("config/gestures.json"),
            resource_path("config/faq.json")
        )
        logger = Logger(config_manager=config)
        logger.info("Démarrage de l'application GestureMouseApp")
        
        cameras = config.get_available_cameras()
        if not cameras:
            logger.error("Aucune caméra détectée")
            QMessageBox.critical(
                None,
                "Erreur Matériel",
                "Aucune caméra n'a été détectée. Veuillez connecter une caméra et redémarrer l'application."
            )
            sys.exit(1)
            
        logger.info(f"Caméras détectées: {cameras}")
        
        configured_cam = int(config.get_setting("DEFAULT", "camera_index", 0))
        if configured_cam not in cameras:
            logger.warning(f"Caméra configurée {configured_cam} non disponible. Utilisation de la caméra 0")
            config.set_setting("DEFAULT", "camera_index", cameras[0])
        
        faq_bot = FAQBot(config_manager=config, logger=logger)
        video_thread = VideoThread(config, logger)
        window = MainWindow(config, logger, faq_bot, video_thread)
        
        window.show()
        logger.info("Interface principale initialisée avec succès")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {str(e)}", exc_info=True) # type: ignore
        QMessageBox.critical(
            None,
            "Erreur d'Initialisation",
            f"Impossible de démarrer l'application:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()