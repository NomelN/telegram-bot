from services.deepseek_service import DeepSeekService
from services.currency_service import currency_service
from services.news_service import NewsService
from services.meteo_service import MeteoService

deepseek_service = DeepSeekService()
news_service = NewsService()

__all__ = [
    "deepseek_service",
    "currency_service",
    "news_service",
    "MeteoService",
]
