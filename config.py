import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

class Config:
    """Classe de configuration pour le bot Telegram."""
    
    # Clés API
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')  
    
    # Urls des API
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
    NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
    
    # Configuration
    MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', 20))  # Par défaut, 20 si non défini dans .env
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
    
    # Messages
    WELCOME_MESSAGE = """
        🤖 *Assistant IA Thématique*

        *Fonctionnalités disponibles :*
        • 🌤️ Météo : Météo en temps réel
        • 📰 Actualités : Dernières news par thème
        • 🗺️ Itinéraire : Planification de trajets
        • 💬 Convertisseur : Conversion de devises
        • 💬 Chat Libre : Discussion avec l'IA
        

        Choisissez une option ci-dessous :
    """
    
    @classmethod
    def validate(cls):
        """Vérifie que toutes les clés nécessaires sont présentes"""
        required_keys = ['TELEGRAM_TOKEN', 'DEEPSEEK_API_KEY', 'OPENWEATHER_API_KEY']
        missing = [key for key in required_keys if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Clés API manquantes : {', '.join(missing)}")