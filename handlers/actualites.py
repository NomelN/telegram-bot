# pyrefly: ignore [missing-import]
from telebot import TeleBot
from config import Config
from keyboards import Keyboards
from services.deepseek_service import DeepSeekService
from utils.session_manager import session_manager, SessionMode

# Initialiser le service DeepSeek
deepseek_service = DeepSeekService()

def ask_theme(bot, msg):
    """Demande le thème des actualités (fonction exportable)"""
    session_manager.set_mode(msg.chat.id, SessionMode.WAITING_THEME)
    
    bot.send_message(
        msg.chat.id,
        "📰 *Quel thème d'actualité vous intéresse ?*\n\n"
        "Choisissez un thème ou tapez votre propre sujet.",
        parse_mode="Markdown",
        reply_markup=Keyboards.themes_actualites()
    )

def register_news_handlers(bot: TeleBot):
    """Enregistre les handlers pour les actualités"""
    
    @bot.message_handler(func=lambda msg: msg.text == "📰 Actualités")
    def _ask_theme_handler(msg):
        ask_theme(bot, msg)
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_THEME)
    def show_news(msg):
        """Affiche les actualités pour le thème choisi"""
        if msg.text == "🔙 Retour menu":
            from handlers.menu import show_main_menu
            show_main_menu(bot, msg)
            return
        
        theme = msg.text.replace("🌍 ", "").replace("🇫🇷 ", "").replace("💻 ", "").replace("🏅 ", "").replace("🎨 ", "").replace("💰 ", "")
        
        # Message de chargement
        loading_msg = bot.send_message(
            msg.chat.id, 
            f"🔍 Recherche des actualités sur *{theme}*...",
            parse_mode="Markdown"
        )
        
        try:
            # Générer les actualités avec DeepSeek
            news = deepseek_service.generate_news(theme)
            
            # Diviser le message si trop long (Telegram limite à 4096 caractères)
            if len(news) > 4000:
                # Envoyer en plusieurs messages
                parts = [news[i:i+4000] for i in range(0, len(news), 4000)]
                bot.edit_message_text(
                    f"📰 *Actualités - {theme}*\n\n{parts[0]}",
                    msg.chat.id,
                    loading_msg.message_id,
                    parse_mode="Markdown"
                )
                for part in parts[1:]:
                    bot.send_message(msg.chat.id, part, parse_mode="Markdown")
            else:
                bot.edit_message_text(
                    f"📰 *Actualités - {theme}*\n\n{news}",
                    msg.chat.id,
                    loading_msg.message_id,
                    parse_mode="Markdown"
                )
            
            # Sauvegarder le thème pour la discussion
            session_manager.set_mode(
                msg.chat.id, 
                SessionMode.WAITING_ACTION,
                {"dernier_theme": theme}
            )
            
            # Proposer des actions
            bot.send_message(
                msg.chat.id,
                "Que voulez-vous faire ?",
                reply_markup=Keyboards.after_news_actions()
            )
            
        except Exception as e:
            bot.edit_message_text(
                f"❌ Erreur lors de la récupération des actualités : {str(e)}",
                msg.chat.id,
                loading_msg.message_id
            )
    
    @bot.message_handler(func=lambda msg: msg.text == "💬 En discuter" and session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_ACTION)
    def discuss_news(msg):
        """Lance une discussion sur le dernier thème d'actualité"""
        session_data = session_manager.get_session(msg.chat.id)
        theme = session_data.data.get("dernier_theme", "actualités")
        
        # Passer en mode chat avec contexte
        session_manager.set_mode(msg.chat.id, SessionMode.CHAT_FREE)
        session = session_manager.get_session(msg.chat.id)
        
        # Initialiser l'historique avec le contexte
        session.add_to_history(f"Parlons des actualités sur : {theme}", "user")
        session.add_to_history(f"Bien sûr ! Que voulez-vous savoir sur {theme} ? Je viens de vous donner les dernières actualités à ce sujet.", "assistant")
        
        bot.send_message(
            msg.chat.id,
            f"💬 *Discussion sur : {theme}*\n\n"
            "Posez-moi vos questions sur ce sujet !\n"
            "Tapez 'Retour menu' pour revenir au menu principal.",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_menu()
        )