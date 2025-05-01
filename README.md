Gesture-Control
Un système de contrôle gestuel pour manipuler le curseur d'un ordinateur à l'aide de gestes de la main ou du nez, conçu pour améliorer l'accessibilité.
Fonctionnalités

Mode Main : Contrôle du curseur avec des gestes comme déplacement (index levé), glisser-déposer (poing fermé), clics (OK, majeur levé), double-clic (OK x2), défilement (auriculaire levé), zoom (pincer/écarter pouce-index).
Mode Nez : Contrôle du curseur en suivant la pointe du nez (sans gestes pour l'instant).
Calibration : Mappage précis des mouvements à l'écran.
Lissage : Filtre de Kalman pour des mouvements fluides.
Interface PyQt5 : Interface graphique avec vidéo en temps réel, boutons, curseurs, et chatbot.
Chatbot : Répond aux questions fréquentes sur l'utilisation.

Prérequis

Python 3.7-3.11
Webcam
Dépendances listées dans requirements.txt

Installation

Clonez le dépôt :git clone <url-du-dépôt>
cd Gesture-Control


Créez un environnement virtuel :python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows


Installez les dépendances :pip install -r requirements.txt


Lancez l'application :python main.py



Utilisation

Cliquez sur "Démarrer" pour activer le contrôle.
Utilisez "Calibrer" pour mapper les mouvements aux coins de l'écran.
Basculez entre mode main et nez avec "Passer au mode Nez".
Ajustez les seuils de clic et le lissage via les curseurs.
Posez des questions au chatbot (ex. "Comment défiler ?").

Gestes (Mode Main)

Déplacement : Levez l'index, repliez les autres doigts, déplacez la main.
Glisser-déposer : Fermez la main en poing, déplacez.
Clic droit : Faites le geste "OK" (pouce touche index).
Clic gauche : Levez le majeur, repliez les autres doigts.
Double-clic : Faites "OK" deux fois rapidement.
Défilement : Levez l'auriculaire, repliez les autres doigts, déplacez verticalement.
Zoom avant : Pincez pouce et index.
Zoom arrière : Écartez pouce et index.

Structure du projet

core/ : Logique principale (suivi, analyse des gestes, contrôle).
interface/ : Interface PyQt5.
utils/ : Calibration et lissage.
config/ : Paramètres et mappage des gestes.
chatbot/ : Assistance utilisateur via FAQ.

Contribution
Les contributions sont bienvenues ! Ouvrez une issue ou une pull request pour proposer des améliorations.
Licence
MIT
