#!/usr/bin/env python3
"""
Bot Telegram thématique avec DeepSeek
Auteur : Votre Nom
Version : 1.0.0
"""

import telebot
from config import Config
from utils.logger import setup_logging, get_logger
from handlers.menu import register_menu_handlers, show_main_menu
from handlers.meteo import register_meteo_handlers
from handlers.actualites import register_news_handlers
from handlers.itineraire import register_route_handlers
from handlers.chat import register_chat_handlers
from handlers.currency import register_currency_handlers
from handlers.football import register_football_handlers
from handlers.actions import register_action_handlers

logger = get_logger(__name__)


class BotThematique:
    """Classe principale du bot"""
    
    def __init__(self):
        # Vérifier la configuration
        Config.validate()
        
        # Initialiser le bot
        self.bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)
        
        # Enregistrer tous les handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Enregistre tous les gestionnaires de messages"""
        register_menu_handlers(self.bot)
        register_meteo_handlers(self.bot)
        register_news_handlers(self.bot)
        register_route_handlers(self.bot)
        register_currency_handlers(self.bot)
        register_football_handlers(self.bot)
        register_chat_handlers(self.bot)
        register_action_handlers(self.bot)

        @self.bot.message_handler(func=lambda msg: True)
        def default_handler(msg):
            show_main_menu(self.bot, msg)
    
    def run(self):
        """Démarre le bot"""
        logger.info("🚀 Bot thématique démarré ! (Ctrl+C pour arrêter)")

        try:
            self.bot.polling(none_stop=True)
        except KeyboardInterrupt:
            logger.info("👋 Bot arrêté")

def main():
    """Point d'entrée principal"""
    setup_logging()
    bot_app = BotThematique()
    bot_app.run()

if __name__ == "__main__":
    main()