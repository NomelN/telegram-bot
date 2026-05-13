from telebot import TeleBot
from config import Config
from keyboards import Keyboards
from services import deepseek_service
from handlers.menu import show_main_menu
from utils.session_manager import session_manager, SessionMode

def register_route_handlers(bot: TeleBot):
    """Enregistre les handlers pour les itinéraires"""
    
    @bot.message_handler(func=lambda msg: msg.text == "🗺️ Itinéraire")
    def ask_departure(msg):
        """Demande la ville de départ"""
        session_manager.set_mode(msg.chat.id, SessionMode.WAITING_DEPARTURE)
        
        bot.send_message(
            msg.chat.id,
            "🗺️ *Planifions votre itinéraire !*\n\n"
            "📍 *Étape 1/2* : Quelle est votre *ville de départ* ?\n\n"
            "Exemples : Paris, Lyon, Marseille...",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_menu()
        )
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_DEPARTURE)
    def ask_arrival(msg):
        """Enregistre le départ et demande l'arrivée"""
        if msg.text == "🔙 Retour menu":
            show_main_menu(bot, msg)
            return
        
        departure = msg.text
        
        # Sauvegarder le départ
        session_manager.set_mode(
            msg.chat.id,
            SessionMode.WAITING_ARRIVAL,
            {"depart": departure}
        )
        
        bot.send_message(
            msg.chat.id,
            f"✅ Départ : *{departure}*\n\n"
            "📍 *Étape 2/2* : Quelle est votre *ville d'arrivée* ?",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_menu()
        )
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_ARRIVAL)
    def show_route(msg):
        """Affiche l'itinéraire entre les deux villes"""
        if msg.text == "🔙 Retour menu":
            show_main_menu(bot, msg)
            return
        
        arrival = msg.text
        session = session_manager.get_session(msg.chat.id)
        departure = session.data.get("depart", "inconnue")
        
        # Message de chargement
        loading_msg = bot.send_message(
            msg.chat.id,
            f"🗺️ Calcul de l'itinéraire *{departure} → {arrival}*...\n"
            "Cela peut prendre quelques secondes.",
            parse_mode="Markdown"
        )
        
        try:
            # Générer l'itinéraire avec DeepSeek
            route = deepseek_service.generate_route(departure, arrival)
            
            # Envoyer l'itinéraire
            if len(route) > 4000:
                parts = [route[i:i+4000] for i in range(0, len(route), 4000)]
                bot.edit_message_text(
                    f"🗺️ *Itinéraire : {departure} → {arrival}*\n\n{parts[0]}",
                    msg.chat.id,
                    loading_msg.message_id,
                    parse_mode="Markdown"
                )
                for part in parts[1:]:
                    bot.send_message(msg.chat.id, part, parse_mode="Markdown")
            else:
                bot.edit_message_text(
                    f"🗺️ *Itinéraire : {departure} → {arrival}*\n\n{route}",
                    msg.chat.id,
                    loading_msg.message_id,
                    parse_mode="Markdown"
                )
            
            # Proposer des actions
            session_manager.set_mode(
                msg.chat.id,
                SessionMode.WAITING_ACTION,
                {
                    "dernier_depart": departure,
                    "derniere_arrivee": arrival
                }
            )
            
            bot.send_message(
                msg.chat.id,
                "Que voulez-vous faire ?",
                reply_markup=Keyboards.after_route_actions()
            )
            
        except Exception as e:
            bot.edit_message_text(
                f"❌ Erreur lors du calcul de l'itinéraire : {str(e)}",
                msg.chat.id,
                loading_msg.message_id
            )
    
    @bot.message_handler(func=lambda msg: msg.text in ["🗺️ Nouvel itinéraire", "🚗 Alternatives"] and session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_ACTION)
    def handle_route_action(msg):
        """Gère les actions après un itinéraire"""
        if msg.text == "🗺️ Nouvel itinéraire":
            ask_departure(msg)
        elif msg.text == "🚗 Alternatives":
            session = session_manager.get_session(msg.chat.id)
            departure = session.data.get("dernier_depart")
            arrival = session.data.get("derniere_arrivee")
            
            if departure and arrival:
                bot.send_message(
                    msg.chat.id,
                    f"🔄 Recherche d'alternatives pour *{departure} → {arrival}*...",
                    parse_mode="Markdown"
                )
                
                # Demander à DeepSeek des alternatives
                alternatives = deepseek_service.generate_response(
                    messages=[{
                        "role": "user",
                        "content": f"""Propose 3 alternatives d'itinéraire entre {departure} et {arrival} :
                        1. Le plus rapide
                        2. Le plus économique
                        3. Le plus touristique
                        
                        Format court et pratique avec emojis."""
                    }],
                    temperature=0.8,
                    max_tokens=500
                )
                
                bot.send_message(msg.chat.id, alternatives, parse_mode="Markdown")