import requests
from datetime import datetime, timedelta
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsService:
    """Service pour récupérer et formater les actualités via NewsAPI"""

    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        if not self.api_key:
            logger.warning("NEWS_API_KEY non définie — service indisponible")
        self.base_url = Config.NEWS_API_URL

    def get_live_news(self, theme: str, limit: int = 5) -> list[dict]:
        """
        Récupère les dernières actualités pour un thème donné.
        """
        if not self.api_key:
            return []

        # Définir la période de recherche (aujourd'hui et hier)
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        params = {
            'apiKey': self.api_key,
            'q': theme,
            'from': yesterday,
            'to': today,
            'language': 'fr',
            'sortBy': 'publishedAt',
            'pageSize': limit
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                logger.error("NewsAPI: %s", data.get('message'))
                return []
        except requests.RequestException as e:
            logger.exception("Erreur réseau NewsAPI: %s", e)
            return []

    def format_articles_for_ai(self, articles: list[dict]) -> str:
        """Formate les articles pour les donner comme contexte à l'IA."""
        if not articles:
            return "Aucune actualité trouvée pour le moment."

        formatted = "Voici les dernières actualités :\n"
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Sans titre')
            description = article.get('description', 'Pas de description')
            formatted += f"{i}. {title}\n   {description}\n\n"
        return formatted