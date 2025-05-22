# Gesture-Control

Un système de contrôle gestuel utilisant MediaPipe, OpenCV, et PyQt5 pour contrôler le curseur de l'ordinateur via des gestes de la main ou des mouvements du nez. Idéal pour améliorer l'accessibilité et offrir une alternative intuitive à la souris.

## Fonctionnalités
- **Mode main** : Contrôle via gestes de la main (déplacement, clics, défilement, zoom).
- **Mode nez** : Contrôle via mouvements de la tête (suivi de la pointe du nez).
- **Calibration** : Alignement précis des mouvements avec l'écran.
- **Interface graphique** : Fenêtre PyQt5 avec flux vidéo en temps réel et commandes.
- **Chatbot intégré** : Répond aux questions sur l'utilisation (ex. "Comment défiler ?").
- **Personnalisation** : Gestes modifiables via `config/user_gesture_map.json`.

## Prérequis
- Python 3.8+
- Une webcam
- Système d'exploitation : Windows, macOS, ou Linux

## Installation
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/gesture-control.git
   cd gesture-control


2. Créez un environnement virtuel :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    .\venv\Scripts\Activate.ps1  # Windows


3. Installez les dépendances :
    ```bash
    pip install -r requirements.txt


4. Lancez l'application :
    ```bash
    python main.py



## Utilisation

1. Démarrer : Cliquez sur "Démarrer" pour activer le contrôle.
2. Calibrer : Cliquez sur "Calibrer" et pointez vers les quatre coins de l'écran.
3. Mode : Basculez entre mode main et mode nez avec "Passer au mode Nez".
4. Gestes :
* Main ouverte : Déplacer le curseur.
* Pincer pouce-index : Clic gauche.
* Pincer pouce-majeur : Clic droit.
* Pincer pouce-index x2 : Double-clic.
* Poing fermé : Glisser-déposer.
* Deux doigts levés : Défilement.
* Deux mains, écarter/rapprocher index : Zoom avant/arrière.
* Mode nez : Clignement d'œil (clic), hochement de tête (défilement).


5. Chatbot : Posez des questions comme "Comment défiler ?".

### Structure du projet

core/ : Logique de suivi, analyse et contrôle.
interface/ : Interface graphique PyQt5.
utils/ : Outils comme le calibrage et le filtre de Kalman.
config/ : Fichiers de configuration (seuils, mappage des gestes).
chatbot/ : Système de FAQ pour l'assistance utilisateur.

## Contribution

1. Forkez le dépôt.
2. Créez une branche : git checkout -b ma-fonctionnalité.
3. Committez vos changements : git commit -m "Ajout de ma fonctionnalité".
4. Poussez : git push origin ma-fonctionnalité.
5. Ouvrez une Pull Request.

## Licence
MIT License
