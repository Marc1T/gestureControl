from chatbot.response_generator import ResponseGenerator

class FAQEngine:
    def __init__(self):
        """Initialise le moteur de FAQ."""
        self.faqs = {
            "comment démarrer": "Cliquez sur 'Démarrer' pour activer le contrôle gestuel.",
            "comment calibrer": "Cliquez sur 'Calibrer' et pointez vers les quatre coins de l'écran.",
            "mode nez": "Utilisez le bouton 'Passer au mode Nez' pour contrôler avec le nez.",
            "gestes": "Les gestes incluent : déplacement (index levé), glisser-déposer (poing fermé), clic droit (geste OK), clic gauche (majeur levé), double-clic (OK rapide x2), défilement (auriculaire levé et déplacer), zoom avant (pincer pouce-index), zoom arrière (écarter pouce-index).",
            "comment défiler": "Levez l'auriculaire, repliez les autres doigts, et déplacez la main vers le haut ou le bas."
        }
        self.response_generator = ResponseGenerator()
        
    def process_query(self, query):
        """Traite une requête utilisateur."""
        query = query.lower()
        for key, answer in self.faqs.items():
            if key in query:
                return self.response_generator.generate(answer)
        return self.response_generator.generate("Désolé, je n'ai pas compris. Essayez 'comment démarrer', 'comment défiler', ou 'gestes'.")