# pyrefly: ignore [missing-import]
from telebot import TeleBot
from handlers.meteo import ask_city
from handlers.actualites import ask_theme
from utils.constants import (
    WEATHER_OTHER_CITY,
    WEATHER_FAVORITE,
    NEWS_OTHER_THEME,
)
from utils.session_manager import session_manager, SessionMode

WEATHER_FOLLOW_UPS = {WEATHER_OTHER_CITY, WEATHER_FAVORITE}
NEWS_FOLLOW_UPS = {NEWS_OTHER_THEME}


def register_action_handlers(bot: TeleBot):
    """Handlers transverses : actions de suivi après météo / actualités."""

    @bot.message_handler(
        func=lambda msg: msg.text in WEATHER_FOLLOW_UPS
        and session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_WEATHER_ACTION
    )
    def handle_weather_follow_up(msg):
        if msg.text == WEATHER_OTHER_CITY:
            ask_city(bot, msg)
        elif msg.text == WEATHER_FAVORITE:
            bot.send_message(msg.chat.id, "⭐ Fonctionnalité 'favoris' bientôt disponible !")

    @bot.message_handler(
        func=lambda msg: msg.text in NEWS_FOLLOW_UPS
        and session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_NEWS_ACTION
    )
    def handle_news_follow_up(msg):
        if msg.text == NEWS_OTHER_THEME:
            ask_theme(bot, msg)
