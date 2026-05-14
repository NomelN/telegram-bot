from services.deepseek_service import DeepSeekService
from services.currency_service import currency_service
from services.news_service import NewsService
from services.meteo_service import MeteoService
from services.football_service import FootballService
from services.football_data_service import FootballDataService

deepseek_service = DeepSeekService()
news_service = NewsService()
football_service = FootballService()
football_data_service = FootballDataService()

__all__ = [
    "deepseek_service",
    "currency_service",
    "news_service",
    "football_service",
    "football_data_service",
    "MeteoService",
]
