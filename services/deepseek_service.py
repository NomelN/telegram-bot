from datetime import datetime

from openai import OpenAI
from config import Config
from services.news_service import NewsService

class DeepSeekService:
    """Service pour interagir avec l'API DeepSeek"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
    
    def generate_response(self, messages: list, temperature: float = None, max_tokens: int = None) -> str:
        """Génère une réponse via DeepSeek"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature or Config.DEFAULT_TEMPERATURE,
                max_tokens=max_tokens or Config.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erreur DeepSeek: {str(e)}")
    
    def generate_news(self, theme: str) -> str:
        """Génère un résumé d'actualités basé sur de VRAIS articles de 2026."""

        # 1. Essayer de récupérer de vraies actualités
        live_articles = []
        news_service = NewsService()
        try:
            live_articles = news_service.get_live_news(theme)
        except Exception as e:
            print(f"Impossible d'utiliser NewsAPI: {e}")

        # 2. Créer le message pour DeepSeek
        if live_articles:
            # Si on a de vrais articles, on les donne comme contexte à l'IA
            context = news_service.format_articles_for_ai(live_articles)
            prompt = f"""Tu es un journaliste qui doit faire un résumé de ces actualités.
            Voici les dernières nouvelles du {datetime.now().strftime('%d/%m/%Y')} pour le thème '{theme}' :
            
            {context}
            
            Résume ces informations en 3 à 5 points avec des émojis et un format Markdown clair.
            """
        else:
            # Message de secours si l'API ne répond pas
            prompt = f"""Donne les tendances ou événements majeurs de 2025 sur le thème '{theme}'.
            Mentionne que les infos sont basées sur ta connaissance et peuvent être datées.
            """

        messages = [{"role": "user", "content": prompt}]
        return self.generate_response(messages, temperature=0.5, max_tokens=800)
    
    def generate_route(self, departure: str, arrival: str) -> str:
        """Génère un itinéraire entre deux villes"""
        prompt = f"""Tu es un expert en voyages. Donne-moi un itinéraire détaillé 
        de {departure} à {arrival}.
        
        Format :
        🚗 *Transport principal* : Moyen recommandé
        ⏱️ *Durée estimée* : Temps approximatif
        📍 *Distance* : Distance approximative
        
        🛣️ *Itinéraire* :
        1. Étapes détaillées
        
        💡 *Conseils* : Meilleur moment, points d'intérêt, alternatives
        
        Format Markdown avec emojis. Pratique et utile."""
        
        messages = [{"role": "user", "content": prompt}]
        return self.generate_response(messages, temperature=0.5, max_tokens=600)