from telebot import types

from utils.constants import (
    BACK_TO_MENU,
    MENU_METEO,
    MENU_NEWS,
    MENU_ROUTE,
    MENU_CHAT,
    MENU_CURRENCY,
    MENU_HELP,
    WEATHER_OTHER_CITY,
    WEATHER_FAVORITE,
    NEWS_OTHER_THEME,
    NEWS_DISCUSS,
    ROUTE_NEW,
    ROUTE_ALTERNATIVES,
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
            types.KeyboardButton(MENU_HELP),
        ]
        markup.add(*buttons)
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
