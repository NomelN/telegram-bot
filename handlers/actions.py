# pyrefly: ignore [missing-import]
from telebot import TeleBot
from handlers.meteo import ask_city
from handlers.actualites import ask_theme
from utils.session_manager import session_manager, SessionMode

FOLLOW_UP_TEXTS = ["🌤️ Autre ville", "📰 Autre thème", "📍 Météo favorite"]


def register_action_handlers(bot: TeleBot):
    """Handlers transverses : actions de suivi après météo / actualités."""

    @bot.message_handler(
        func=lambda msg: msg.text in FOLLOW_UP_TEXTS
        and session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_ACTION
    )
    def handle_follow_up_actions(msg):
        if msg.text == "🌤️ Autre ville":
            ask_city(bot, msg)
        elif msg.text == "📰 Autre thème":
            ask_theme(bot, msg)
        elif msg.text == "📍 Météo favorite":
            bot.send_message(msg.chat.id, "⭐ Fonctionnalité 'favoris' bientôt disponible !")
