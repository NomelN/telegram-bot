from telebot import TeleBot
from config import Config
from utils.keyboards import Keyboards
from utils.session_manager import session_manager, SessionMode

def show_main_menu(bot: TeleBot, msg):
    """Affiche le menu principal"""
    session_manager.reset_session(msg.chat.id)
    
    bot.send_message(
        msg.chat.id,
        Config.WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=Keyboards.main_menu()
    )

def register_menu_handlers(bot: TeleBot):
    """Enregistre les handlers du menu"""
    
    @bot.message_handler(commands=['start'])
    def start(msg):
        show_main_menu(bot, msg)
    
    @bot.message_handler(commands=['help'])
    @bot.message_handler(func=lambda msg: msg.text == "❓ Aide")
    def help(msg):
        help_text = """
            🤖 *Guide d'utilisation*

            *Fonctionnalités :*

            🌤️ *Météo*
            → Météo en temps réel pour n'importe quelle ville

            📰 *Actualités*
            → Résumé des dernières actualités par thème

            🗺️ *Itinéraire*
            → Planification de trajets entre deux villes
            
            💱 *Convertisseur*
            → Conversion de devises en temps réel

            💬 *Chat Libre*
            → Discussion avec l'IA DeepSeek

            *Commandes :*
            /start - Menu principal
            /help - Ce message d'aide

            *Besoin d'aide ?* Contactez l'administrateur
        """
        bot.send_message(msg.chat.id, help_text, parse_mode="Markdown")
    
    @bot.message_handler(func=lambda msg: msg.text == "🔙 Retour menu")
    def back_to_menu(msg):
        show_main_menu(bot, msg)