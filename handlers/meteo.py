# pyrefly: ignore [missing-import]
from telebot import TeleBot
from config import Config
from keyboards import Keyboards
from services.meteo_service import MeteoService
from utils.session_manager import session_manager, SessionMode

def ask_city(bot, msg):
    """Demande la ville pour la météo (fonction exportable)"""
    session_manager.set_mode(msg.chat.id, SessionMode.WAITING_CITY)
    
    bot.send_message(
        msg.chat.id,
        "📍 *Pour quelle ville voulez-vous la météo ?*\n\n"
        "Tapez le nom d'une ville (ex: Paris, Lyon, New York...)",
        parse_mode="Markdown",
        reply_markup=Keyboards.cities_suggestions()
    )

def register_meteo_handlers(bot: TeleBot):
    """Enregistre les handlers pour la météo"""
    
    @bot.message_handler(func=lambda msg: msg.text == "🌤️ Météo")
    def _ask_city_handler(msg):
        ask_city(bot, msg)
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_CITY)
    def show_weather(msg):
        """Affiche la météo pour la ville demandée"""
        if msg.text == "🔙 Retour menu":
            return_back_to_menu(bot, msg)
            return
        
        city = msg.text.replace("🏠 ", "")
        
        # Message de chargement
        loading_msg = bot.send_message(msg.chat.id, "🔍 Recherche de la météo...")
        
        # Récupérer la météo
        result = MeteoService.get_weather(city)
        
        if result["success"]:
            formatted = MeteoService.format_weather(result["data"], city)
            bot.edit_message_text(
                formatted,
                msg.chat.id,
                loading_msg.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                f"❌ Ville '{city}' non trouvée. Vérifiez l'orthographe.",
                msg.chat.id,
                loading_msg.message_id
            )
        
        # Proposer des actions
        session_manager.set_mode(msg.chat.id, SessionMode.WAITING_ACTION)
        bot.send_message(
            msg.chat.id,
            "Que voulez-vous faire ?",
            reply_markup=Keyboards.after_meteo_actions()
        )

def return_back_to_menu(bot, msg):
    """Retour au menu principal"""
    from handlers.menu import show_main_menu
    show_main_menu(bot, msg)