from telebot import types

from config import Config
from utils.constants import (
    BACK_TO_MENU,
    MENU_METEO,
    MENU_NEWS,
    MENU_ROUTE,
    MENU_CHAT,
    MENU_CURRENCY,
    MENU_FOOTBALL,
    MENU_HELP,
    WEATHER_OTHER_CITY,
    WEATHER_FAVORITE,
    NEWS_OTHER_THEME,
    NEWS_DISCUSS,
    ROUTE_NEW,
    ROUTE_ALTERNATIVES,
    FOOTBALL_STANDINGS,
    FOOTBALL_TOP_SCORERS,
    FOOTBALL_TOP_ASSISTS,
    FOOTBALL_TEAM_STATS,
    FOOTBALL_H2H,
    FOOTBALL_CHANGE_SEASON,
    FOOTBALL_LIVE_ENTRY,
    FOOTBALL_LIVE_MATCHES,
    FOOTBALL_LIVE_STANDINGS,
    FOOTBALL_LIVE_SCORERS,
    FOOTBALL_LIVE_MATCHDAY,
)


class Keyboards:
    """Gestion des claviers du bot"""

    @staticmethod
    def main_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            types.KeyboardButton(MENU_METEO),
            types.KeyboardButton(MENU_NEWS),
            types.KeyboardButton(MENU_ROUTE),
            types.KeyboardButton(MENU_CHAT),
            types.KeyboardButton(MENU_CURRENCY),
            types.KeyboardButton(MENU_FOOTBALL),
            types.KeyboardButton(MENU_HELP),
        ]
        markup.add(*buttons)
        return markup

    @staticmethod
    def football_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            FOOTBALL_STANDINGS, FOOTBALL_TEAM_STATS,
            FOOTBALL_TOP_SCORERS, FOOTBALL_TOP_ASSISTS,
            FOOTBALL_H2H,
        )
        markup.add(FOOTBALL_LIVE_ENTRY)
        markup.add(FOOTBALL_CHANGE_SEASON)
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def football_live_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            FOOTBALL_LIVE_MATCHES, FOOTBALL_LIVE_STANDINGS,
            FOOTBALL_LIVE_SCORERS, FOOTBALL_LIVE_MATCHDAY,
        )
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def football_live_competitions():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*list(Config.FOOTBALL_DATA_COMPETITIONS.keys()))
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def football_leagues():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        labels = list(Config.FOOTBALL_LEAGUES.keys())
        markup.add(*labels)
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def football_seasons():
        from services.football_service import AVAILABLE_SEASONS
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(*[str(s) for s in AVAILABLE_SEASONS])
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def cities_suggestions():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🏠 Paris", "🏠 Lyon", "🏠 Marseille", "🏠 Bordeaux")
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def themes_actualites():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            "🌍 Monde", "🇫🇷 France",
            "💻 Technologie", "🏅 Sport",
            "🎨 Culture", "💰 Économie",
        )
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def back_to_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(BACK_TO_MENU)
        return markup

    @staticmethod
    def after_meteo_actions():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(WEATHER_OTHER_CITY, WEATHER_FAVORITE, BACK_TO_MENU)
        return markup

    @staticmethod
    def after_news_actions():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(NEWS_OTHER_THEME, NEWS_DISCUSS, BACK_TO_MENU)
        return markup

    @staticmethod
    def after_route_actions():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(ROUTE_NEW, ROUTE_ALTERNATIVES, BACK_TO_MENU)
        return markup
