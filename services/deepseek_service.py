from openai import OpenAI
from config import Config

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
        """Génère un résumé d'actualités sur un thème"""
        prompt = f"""Tu es un journaliste. Donne-moi les 5 dernières actualités importantes 
        sur le thème : {theme}. 
        
        Pour chaque actualité :
        - Un titre en gras avec emoji
        - Un résumé de 2-3 phrases
        - La date approximative
        
        Format Markdown. Sois concis mais informatif.
        Précise que ce sont des informations simulées basées sur ta connaissance jusqu'en mai 2025."""
        
        messages = [{"role": "user", "content": prompt}]
        return self.generate_response(messages, temperature=0.7, max_tokens=800)
    
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