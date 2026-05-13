# pyrefly: ignore [missing-import]
from telebot import TeleBot
from config import Config
from keyboards import Keyboards
from services import deepseek_service
from handlers.menu import show_main_menu
from utils.session_manager import session_manager, SessionMode


def register_chat_handlers(bot: TeleBot):
    """Enregistre les handlers pour le chat libre"""

    @bot.message_handler(func=lambda msg: msg.text == "💬 Chat Libre")
    def activate_chat(msg):
        session_manager.set_mode(msg.chat.id, SessionMode.CHAT_FREE)

        bot.send_message(
            msg.chat.id,
            "💬 *Mode Chat Libre activé !*\n\n"
            "Je suis votre assistant IA basé sur DeepSeek.\n"
            "Posez-moi toutes vos questions, je ferai de mon mieux pour y répondre !\n\n"
            "*Commandes disponibles :*\n"
            "• Tapez 'Retour menu' pour revenir au menu principal\n"
            "• Tapez 'Effacer' pour réinitialiser la conversation\n"
            "• Tapez 'Historique' pour voir les derniers échanges\n\n"
            "Que voulez-vous savoir ? 😊",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_menu()
        )

    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.CHAT_FREE)
    def chat_response(msg):
        if msg.text == "🔙 Retour menu":
            show_main_menu(bot, msg)
            return

        if msg.text.lower() == "effacer":
            session = session_manager.get_session(msg.chat.id)
            session.history = []
            bot.send_message(
                msg.chat.id,
                "✅ Conversation réinitialisée !\nPosez une nouvelle question.",
                reply_markup=Keyboards.back_to_menu()
            )
            return

        if msg.text.lower() == "historique":
            session = session_manager.get_session(msg.chat.id)
            if not session.history:
                bot.send_message(msg.chat.id, "📝 Aucun historique pour le moment.")
                return

            history_text = "*📝 Derniers échanges :*\n\n"
            for i, entry in enumerate(session.history[-10:], 1):
                role_emoji = "👤" if entry["role"] == "user" else "🤖"
                preview = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
                history_text += f"{role_emoji} *{i}.* {preview}\n\n"

            bot.send_message(msg.chat.id, history_text, parse_mode="Markdown")
            return

        session = session_manager.get_session(msg.chat.id)
        session.add_to_history(msg.text, "user")

        bot.send_chat_action(msg.chat.id, 'typing')

        try:
            response = deepseek_service.generate_response(
                messages=session.history,
                temperature=Config.DEFAULT_TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )

            session.add_to_history(response, "assistant")

            if len(response) > 4000:
                parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for part in parts:
                    bot.send_message(msg.chat.id, part, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, response, parse_mode="Markdown")

            print(f"💬 Chat - Utilisateur {msg.chat.id} - Message traité")

        except Exception as e:
            bot.send_message(
                msg.chat.id,
                f"❌ Désolé, une erreur est survenue : {str(e)}\n"
                "Veuillez réessayer ou taper 'Effacer' pour réinitialiser."
            )
