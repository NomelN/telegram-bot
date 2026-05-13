#!/usr/bin/env python3
"""
Bot Telegram thématique avec DeepSeek
Auteur : Votre Nom
Version : 1.0.0
"""

import telebot
from config import Config
from handlers.menu import register_menu_handlers
from handlers.meteo import register_meteo_handlers
from handlers.actualites import register_news_handlers
from handlers.itineraire import register_route_handlers
from handlers.chat import register_chat_handlers

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
        register_chat_handlers(self.bot)
        
        # Handler pour les messages non reconnus
        @self.bot.message_handler(func=lambda msg: True)
        def default_handler(msg):
            from handlers.menu import show_main_menu
            show_main_menu(self.bot, msg)
    
    def run(self):
        """Démarre le bot"""
        print("🚀 Bot thématique démarré !")
        print("Appuyez sur Ctrl+C pour arrêter")
        
        try:
            self.bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("\n👋 Bot arrêté")

def main():
    """Point d'entrée principal"""
    bot_app = BotThematique()
    bot_app.run()

if __name__ == "__main__":
    main()