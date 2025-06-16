# chatbot/faq_bot.py
"""
Chatbot FAQ pour GestureMouseApp utilisant NLP (TF-IDF, similarité cosinus).
"""

import nltk
from typing import List, Dict, Optional, Any, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from scipy.sparse import spmatrix

class FAQBotError(Exception):
    """Exception personnalisée pour les erreurs du chatbot FAQ."""
    pass

class FAQBot:
    """
    Chatbot FAQ qui répond aux questions en utilisant TF-IDF et similarité cosinus.

    Attributes:
        config (Any): Gestionnaire de configuration.
        logger (Any): Logger pour journalisation.
        faq_data (List[Dict[str, str]]): Données FAQ (question-réponse).
        questions (List[str]): Liste des questions FAQ.
        tfidf_matrix (Union[np.ndarray, spmatrix]): Matrice TF-IDF des questions.
        tfidf_matrix (np.ndarray): Matrice TF-IDF des questions.
        similarity_threshold (float): Seuil de similarité pour les réponses.
        stemmer (SnowballStemmer): Stemmer pour le prétraitement.
        stop_words (set): Mots vides pour le prétraitement.
    """

    def __init__(self, config_manager: Any, logger: Any) -> None:
        """
        Initialise le chatbot FAQ.

        Args:
            config_manager (Any): Instance de ConfigManager.
            logger (Any): Instance de Logger.
        """
        self.config = config_manager
        self.logger = logger
        self.faq_data: List[Dict[str, str]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[Union[np.ndarray, spmatrix]] = None
        self.similarity_threshold: float = 0.5
        self.stemmer = SnowballStemmer("french")
        self.stop_words = set(stopwords.words("french"))
        try:
            nltk.download("punkt", quiet=True)
            nltk.download("stopwords", quiet=True)
            self._load_faq()
            self._initialize_vectorizer()
            self.logger.info("FAQBot initialisé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur initialisation FAQBot : {e}")
            raise FAQBotError(f"Erreur initialisation FAQBot : {e}")

    def _load_faq(self) -> None:
        """Charge les données FAQ depuis config_manager."""
        try:
            self.faq_data = self.config.get_faq_data()
            self.questions = [item["question"] for item in self.faq_data]
            self.similarity_threshold = self.config.get_setting(
                "FAQ", "similarity_threshold", 0.5
            )
            if not self.faq_data:
                raise FAQBotError("Aucune donnée FAQ chargée")
            self.logger.info(f"Chargé {len(self.faq_data)} entrées FAQ")
        except Exception as e:
            self.logger.error(f"Erreur chargement FAQ : {e}")
            raise FAQBotError(f"Erreur chargement FAQ : {e}")

    def _preprocess_text(self, text: str) -> str:
        """
        Prétraitement du texte : tokenisation, suppression des mots vides, stemming.

        Args:
            text (str): Texte à prétraiter.

        Returns:
            str: Texte prétraité.
        """
        try:
            tokens = word_tokenize(text.lower(), language="french")
            tokens = [
                self.stemmer.stem(token)
                for token in tokens
                if token.isalnum() and token not in self.stop_words
            ]
            return " ".join(tokens)
        except Exception as e:
            self.logger.error(f"Erreur prétraitement texte : {e}")
            return text.lower()

    def _initialize_vectorizer(self) -> None:
        """Initialise le vectoriseur TF-IDF avec les questions FAQ."""
        try:
            preprocessed_questions = [self._preprocess_text(q) for q in self.questions]
            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(preprocessed_questions)
            self.logger.info("Vectoriseur TF-IDF initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation vectoriseur : {e}")
            raise FAQBotError(f"Erreur initialisation vectoriseur : {e}")

    def get_response(self, user_question: str) -> Optional[str]:
        """
        Retourne la réponse la plus pertinente pour une question utilisateur.

        Args:
            user_question (str): Question posée par l'utilisateur.

        Returns:
            Optional[str]: Réponse correspondante ou None si aucune réponse pertinente.
        """
        try:
            if not user_question.strip():
                self.logger.warning("Question utilisateur vide")
                return None
            preprocessed_question = self._preprocess_text(user_question)
            if self.vectorizer is None or self.tfidf_matrix is None:
                self.logger.error("Vectoriseur TF-IDF non initialisé")
                return None
            question_vector = self.vectorizer.transform([preprocessed_question])
            similarities = cosine_similarity(question_vector, self.tfidf_matrix)
            max_similarity = np.max(similarities)
            if max_similarity < self.similarity_threshold:
                self.logger.info(
                    f"Aucune réponse pertinente pour '{user_question}' "
                    f"(similarité={max_similarity:.2f} < {self.similarity_threshold})"
                )
                return None
            best_match_idx = np.argmax(similarities)
            response = self.faq_data[best_match_idx]["answer"]
            self.logger.info(
                f"Réponse trouvée pour '{user_question}' "
                f"(similarité={max_similarity:.2f}, question='{self.questions[best_match_idx]}')"
            )
            return response
        except Exception as e:
            self.logger.error(f"Erreur traitement question '{user_question}' : {e}")
            return None

    def reload_faq(self) -> None:
        """Recharge les données FAQ et réinitialise le vectoriseur."""
        try:
            self._load_faq()
            self._initialize_vectorizer()
            self.logger.info("Données FAQ rechargées")
        except Exception as e:
            self.logger.error(f"Erreur rechargement FAQ : {e}")
            raise FAQBotError(f"Erreur rechargement FAQ : {e}")