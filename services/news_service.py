import requests
from typing import Optional, List, Dict
from config import Config

class NewsService:
    """Service pour récupérer les actualités (optionnel, avec NewsAPI)"""
    
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = Config.NEWS_API_URL
    
    def get_news_by_category(self, category: str, country: str = "fr", limit: int = 5) -> Optional[List[Dict]]:
        """
        Récupère les actualités par catégorie depuis NewsAPI
        
        Catégories disponibles :
        - business, entertainment, general, health, science, sports, technology
        """
        if not self.api_key:
            return None
        
        category_map = {
            "monde": "general",
            "france": "general",
            "technologie": "technology",
            "sport": "sports",
            "culture": "entertainment",
            "économie": "business",
            "science": "science",
            "santé": "health"
        }
        
        api_category = category_map.get(category.lower(), "general")
        
        params = {
            'apiKey': self.api_key,
            'category': api_category,
            'country': country,
            'pageSize': limit,
            'language': 'fr'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            return None
            
        except requests.RequestException as e:
            print(f"Erreur NewsAPI : {e}")
            return None
    
    def format_articles(self, articles: List[Dict], theme: str) -> str:
        """Formate les articles en message Telegram"""
        if not articles:
            return f"❌ Aucune actualité trouvée pour le thème '{theme}'."
        
        formatted = f"📰 *Actualités - {theme}*\n\n"
        
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', 'Sans titre')
            description = article.get('description', 'Pas de description')
            url = article.get('url', '')
            source = article.get('source', {}).get('name', 'Inconnue')
            
            # Tronquer les descriptions trop longues
            if len(description) > 200:
                description = description[:197] + "..."
            
            formatted += f"{i}️⃣ *{title}*\n"
            formatted += f"📝 _{description}_\n"
            formatted += f"📰 Source : {source}\n"
            if url:
                formatted += f"🔗 [Lire plus]({url})\n"
            formatted += "\n"
        
        formatted += "⚠️ *Note* : Actualités fournies par NewsAPI.org"
        
        return formatted
    
    def search_news(self, query: str, limit: int = 5) -> Optional[List[Dict]]:
        """Recherche des actualités par mot-clé"""
        if not self.api_key:
            return None
        
        params = {
            'apiKey': self.api_key,
            'q': query,
            'pageSize': limit,
            'language': 'fr',
            'sortBy': 'publishedAt'
        }
        
        try:
            response = requests.get("https://newsapi.org/v2/everything", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            return None
            
        except requests.RequestException as e:
            print(f"Erreur recherche NewsAPI : {e}")
            return None

# Instance du service
news_service = NewsService()