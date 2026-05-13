from telebot import types

class Keyboards:
    """Gestion des claviers du bot"""
    
    @staticmethod
    def main_menu():
        """Clavier du menu principal"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        buttons = [
            types.KeyboardButton("🌤️ Météo"),
            types.KeyboardButton("📰 Actualités"),
            types.KeyboardButton("🗺️ Itinéraire"),
            types.KeyboardButton("💬 Chat Libre"),
            types.KeyboardButton("💱 Convertisseur"),
            types.KeyboardButton("❓ Aide")
        ]
        
        markup.add(*buttons)
        return markup
    
    @staticmethod
    def cities_suggestions():
        """Suggestions de villes pour la météo"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🏠 Paris", "🏠 Lyon", "🏠 Marseille", "🏠 Bordeaux")
        markup.add("🔙 Retour menu")
        return markup
    
    @staticmethod
    def themes_actualites():
        """Thèmes pour les actualités"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            "🌍 Monde", "🇫🇷 France", 
            "💻 Technologie", "🏅 Sport",
            "🎨 Culture", "💰 Économie"
        )
        markup.add("🔙 Retour menu")
        return markup
    
    @staticmethod
    def back_to_menu():
        """Clavier simple avec retour au menu"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔙 Retour menu")
        return markup
    
    @staticmethod
    def after_meteo_actions():
        """Actions après avoir consulté la météo"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🌤️ Autre ville", "📍 Météo favorite", "🔙 Retour menu")
        return markup
    
    @staticmethod
    def after_news_actions():
        """Actions après avoir consulté les actualités"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📰 Autre thème", "💬 En discuter", "🔙 Retour menu")
        return markup
    
    @staticmethod
    def after_route_actions():
        """Actions après avoir consulté un itinéraire"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🗺️ Nouvel itinéraire", "🚗 Alternatives", "🔙 Retour menu")
        return markup