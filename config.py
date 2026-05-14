import logging
import os
from dotenv import load_dotenv

_logger = logging.getLogger(__name__)

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

class Config:
    """Classe de configuration pour le bot Telegram."""

    # Clés API
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
    FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')
    FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')

    # Urls des API
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    EXCHANGE_RATE_BASE_URL = "https://v6.exchangerate-api.com/v6"
    FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
    FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
    # Plan gratuit API-Football : seasons 2022-2024 uniquement.
    # Ajustable via FOOTBALL_MAX_SEASON dans .env si tu changes d'offre.
    FOOTBALL_MAX_SEASON = int(os.getenv('FOOTBALL_MAX_SEASON', 2024))

    # Compétitions football-data.org (codes officiels, plan gratuit)
    FOOTBALL_DATA_COMPETITIONS = {
        "🇫🇷 Ligue 1": "FL1",
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "PL",
        "🇪🇸 La Liga": "PD",
        "🇩🇪 Bundesliga": "BL1",
        "🇮🇹 Serie A": "SA",
        "🏆 Ligue des Champions": "CL",
    }

    # Compétitions exposées (id API-Football, nom affiché, pays/scope)
    FOOTBALL_LEAGUES = {
        "🇫🇷 Ligue 1": 61,
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39,
        "🇪🇸 La Liga": 140,
        "🇩🇪 Bundesliga": 78,
        "🇮🇹 Serie A": 135,
        "🏆 Ligue des Champions": 2,
        "🌍 CAN": 6,
        "🌎 Coupe du Monde": 1,
    }

    # Configuration
    MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', 20))
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))

    # Messages
    WELCOME_MESSAGE = (
        "🤖 *Assistant IA Thématique*\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "*Que puis-je faire pour vous ?*\n\n"
        "🌤️  *Météo* — en temps réel, n'importe quelle ville\n"
        "📰  *Actualités* — dernières news par thème\n"
        "💱  *Convertisseur* — conversion de devises\n"
        "⚽  *Football* — classement, stats, top buteurs, matchs du jour\n"
        "💬  *Chat Libre* — discussion avec l'IA\n\n"
        "_Choisissez une option ci-dessous_ 👇"
    )

    @classmethod
    def validate(cls):
        """Vérifie la présence des clés API. Lève si une clé requise manque,
        avertit pour les clés optionnelles."""
        required_keys = [
            'TELEGRAM_TOKEN',
            'DEEPSEEK_API_KEY',
            'OPENWEATHER_API_KEY',
            'EXCHANGE_RATE_API_KEY',
        ]
        optional_keys = ['NEWS_API_KEY', 'FOOTBALL_API_KEY', 'FOOTBALL_DATA_API_KEY']

        missing = [key for key in required_keys if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Clés API manquantes : {', '.join(missing)}")

        missing_optional = [key for key in optional_keys if not getattr(cls, key)]
        if missing_optional:
            _logger.warning("Clés API optionnelles manquantes : %s", ', '.join(missing_optional))
