# Gesture Control

Une application de contrôle gestuel utilisant MediaPipe et PyQt5 pour contrôler votre PC sans souris ni trackpad.

## Installation

1. Clonez le dépôt :
   ```bash
   git clone <repository_url>
   cd Gesture-Control
   ```

2. Créez un environnement virtuel et installez les dépendances :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Lancez l'application :
   ```bash
   python main.py
   ```

## Fonctionnalités

- Détection des gestes de la main pour contrôler le curseur et exécuter des actions (clic, zoom).
- Interface graphique avec feedback visuel.
- Chatbot FAQ pour répondre aux questions des utilisateurs.

## Dépendances

- Python 3.8+
- mediapipe
- opencv-python
- pyqt5
- numpy

## Structure du projet

- `core/` : Logique de détection et contrôle.
- `interface/` : Interface graphique.
- `utils/` : Outils (journalisation, configuration).
- `chatbot/` : Module chatbot (FAQ).
- `config/` : Fichiers de configuration.