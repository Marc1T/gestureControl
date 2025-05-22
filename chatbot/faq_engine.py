from chatbot.response_generator import ResponseGenerator

class FAQEngine:
    def __init__(self):
        """Initialise le moteur de FAQ."""
        self.faqs = {
            "comment démarrer": "Cliquez sur 'Démarrer' pour activer le contrôle gestuel.",
            "comment calibrer": "Cliquez sur 'Calibrer' et pointez vers les quatre coins de l'écran.",
            "mode nez": "Utilisez le bouton 'Passer au mode Nez' pour contrôler avec le nez.",
            "gestes": "Les gestes incluent : déplacement (main ouverte), glisser-déposer (poing fermé), clic gauche (pincer pouce-index), clic droit (pincer pouce-majeur), double-clic (pincer pouce-index x2), défilement (deux doigts levés et déplacer), zoom avant (écarter index des deux mains), zoom arrière (rapprocher index des deux mains). En mode nez : clic (clignement d'œil), défilement (hochement de tête).",
            "comment défiler": "Levez l'index et le majeur, repliez les autres doigts, et déplacez la main vers le haut ou le bas. En mode nez, hochez la tête."
        }
        self.response_generator = ResponseGenerator()
        
    def process_query(self, query):
        """Traite une requête utilisateur."""
        query = query.lower()
        for key, answer in self.faqs.items():
            if key in query:
                return self.response_generator.generate(answer)
        return self.response_generator.generate("Désolé, je n'ai pas compris. Essayez 'comment démarrer', 'comment défiler', ou 'gestes'.")