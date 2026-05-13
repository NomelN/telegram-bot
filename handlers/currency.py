import re
from telebot import TeleBot, types
from config import Config
from utils.keyboards import Keyboards
from services.currency_service import currency_service
from handlers.menu import show_main_menu
from utils.session_manager import session_manager, SessionMode


def register_currency_handlers(bot: TeleBot):
    """Enregistre les handlers pour le convertisseur de devises"""
    
    @bot.message_handler(commands=['convert', 'conversion', 'devise', 'devises'])
    @bot.message_handler(func=lambda msg: msg.text == "💱 Convertisseur")
    def start_conversion(msg):
        """Démarre le processus de conversion guidé"""
        show_currency_from_selection(bot, msg)
    
    def show_currency_from_selection(bot, msg):
        """Étape 1 : Choisir la devise de départ"""
        session_manager.set_mode(msg.chat.id, SessionMode.WAITING_CURRENCY_FROM)
        
        currencies = get_main_currencies_list()
        
        # Créer un clavier avec les devises les plus populaires
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        
        # Première rangée : devises les plus utilisées
        row1 = ["EUR (€)", "USD ($)", "GBP (£)"]
        markup.add(*[types.KeyboardButton(btn) for btn in row1])
        
        # Deuxième rangée
        row2 = ["CHF (Fr)", "JPY (¥)", "CAD (C$)"]
        markup.add(*[types.KeyboardButton(btn) for btn in row2])
        
        # Troisième rangée : devises africaines populaires
        row3 = ["XOF (CFA)", "MAD (DH)", "DZD (DA)"]
        markup.add(*[types.KeyboardButton(btn) for btn in row3])
        
        # Quatrième rangée
        row4 = ["CNY (¥)", "AUD (A$)", "TND (DT)"]
        markup.add(*[types.KeyboardButton(btn) for btn in row4])
        
        # Boutons d'action
        markup.add(
            types.KeyboardButton("📋 Voir toutes les devises"),
            types.KeyboardButton("🔙 Retour menu")
        )
        
        bot.send_message(
            msg.chat.id,
            "💱 *Convertisseur de devises - Étape 1/3*\n\n"
            "*Choisissez la devise de départ :*\n\n"
            "Vous pouvez :\n"
            "• Cliquer sur un bouton ci-dessous\n"
            "• Ou taper le code devise (ex: EUR, USD, GBP)\n"
            "• Ou écrire le nom (ex: euro, dollar, livre)",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_CURRENCY_FROM)
    def handle_currency_from(msg):
        """Traite la devise de départ choisie"""
        if msg.text == "🔙 Retour menu":
            show_main_menu(bot, msg)
            return
        
        if msg.text == "📋 Voir toutes les devises":
            show_all_currencies(bot, msg)
            return
        
        # Extraire le code devise
        from_currency = extract_currency_code(msg.text)
        
        if not from_currency:
            bot.send_message(
                msg.chat.id,
                "❌ Devise non reconnue.\n\n"
                "Veuillez choisir une devise dans la liste ou taper un code valide (ex: EUR, USD, GBP).",
                reply_markup=get_currency_from_keyboard()
            )
            return
        
        # Sauvegarder la devise de départ
        session_manager.set_mode(
            msg.chat.id,
            SessionMode.WAITING_CURRENCY_AMOUNT,
            {"from_currency": from_currency}
        )
        
        common = currency_service.get_common_currencies()
        from_name = common.get(from_currency, from_currency)
        
        # Simplifier le clavier pour l'étape du montant
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton("10"),
            types.KeyboardButton("50"),
            types.KeyboardButton("100"),
            types.KeyboardButton("500"),
            types.KeyboardButton("1000"),
            types.KeyboardButton("5000")
        )
        markup.add(types.KeyboardButton("🔙 Retour menu"))
        
        bot.send_message(
            msg.chat.id,
            f"✅ Devise de départ : *{from_currency}* ({from_name})\n\n"
            "💱 *Étape 2/3 : Quel montant voulez-vous convertir ?*\n\n"
            "Tapez un nombre (ex: 100, 50.50) ou choisissez un montant rapide :",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_CURRENCY_AMOUNT)
    def handle_amount(msg):
        """Traite le montant à convertir"""
        if msg.text == "🔙 Retour menu":
            show_main_menu(bot, msg)
            return
        
        # Extraire le montant
        amount = extract_amount(msg.text)
        
        if amount is None or amount <= 0:
            bot.send_message(
                msg.chat.id,
                "❌ Montant invalide. Veuillez taper un nombre valide (ex: 100, 50.50)."
            )
            return
        
        # Récupérer la devise de départ
        session = session_manager.get_session(msg.chat.id)
        from_currency = session.data.get("from_currency")
        
        # Sauvegarder le montant
        session_manager.set_mode(
            msg.chat.id,
            SessionMode.WAITING_CURRENCY_TO,
            {
                "from_currency": from_currency,
                "amount": amount
            }
        )
        
        # Afficher la sélection de la devise d'arrivée
        common = currency_service.get_common_currencies()
        from_name = common.get(from_currency, from_currency)
        
        # Créer un clavier avec les devises de destination
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        
        # Exclure la devise de départ de la liste
        main_currencies = ["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "XOF", "MAD", "DZD", "CNY", "AUD", "TND"]
        available = [c for c in main_currencies if c != from_currency][:9]
        
        # Créer les boutons
        buttons = []
        for curr in available:
            name = common.get(curr, curr)
            symbol = get_currency_symbol(curr)
            buttons.append(types.KeyboardButton(f"{curr} {symbol}"))
        
        markup.add(*buttons)
        markup.add(
            types.KeyboardButton("📋 Voir toutes les devises"),
            types.KeyboardButton("🔙 Retour menu")
        )
        
        bot.send_message(
            msg.chat.id,
            f"✅ Départ : *{amount} {from_currency}* ({from_name})\n\n"
            "💱 *Étape 3/3 : Choisissez la devise d'arrivée :*\n\n"
            "Cliquez sur un bouton ou tapez un code devise (ex: USD, EUR, GBP)",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    @bot.message_handler(func=lambda msg: session_manager.get_mode(msg.chat.id) == SessionMode.WAITING_CURRENCY_TO)
    def handle_currency_to(msg):
        """Traite la devise d'arrivée et affiche le résultat"""
        if msg.text == "🔙 Retour menu":
            show_main_menu(bot, msg)
            return
        
        if msg.text == "📋 Voir toutes les devises":
            show_all_currencies(bot, msg)
            return
        
        # Extraire le code devise
        to_currency = extract_currency_code(msg.text)
        
        if not to_currency:
            bot.send_message(
                msg.chat.id,
                "❌ Devise non reconnue. Veuillez choisir une devise valide."
            )
            return
        
        # Récupérer les données de la session
        session = session_manager.get_session(msg.chat.id)
        from_currency = session.data.get("from_currency")
        amount = session.data.get("amount")
        
        if to_currency == from_currency:
            bot.send_message(
                msg.chat.id,
                "❌ La devise d'arrivée doit être différente de la devise de départ."
            )
            return
        
        # Effectuer la conversion
        loading_msg = bot.send_message(
            msg.chat.id,
            f"💱 Conversion de {amount} {from_currency} en {to_currency}..."
        )
        
        result = currency_service.convert(amount, from_currency, to_currency)
        
        if result["success"]:
            common = currency_service.get_common_currencies()
            from_name = common.get(result["from"], result["from"])
            to_name = common.get(result["to"], result["to"])
            from_symbol = get_currency_symbol(result["from"])
            to_symbol = get_currency_symbol(result["to"])
            
            message = f"""
💱 *Conversion réussie !*

┌─────────────────────────┐
│ *Départ*   │ {result['amount']} {from_symbol} {result['from']}
│ *{from_name}*
│
│ Taux : 1 {result['from']} = {result['rate']} {result['to']}
│
│ *Résultat* │ *{result['result']} {to_symbol} {result['to']}*
│ *{to_name}*
└─────────────────────────┘

📅 Taux du : {result['date']}
🔄 Mis à jour quotidiennement

*Que voulez-vous faire ?*
            """
            
            bot.edit_message_text(
                message,
                msg.chat.id,
                loading_msg.message_id,
                parse_mode="Markdown"
            )
            
            # Proposer des actions
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(
                types.KeyboardButton("💱 Nouvelle conversion"),
                types.KeyboardButton("🔄 Inverser"),
                types.KeyboardButton("💱 Taux du jour"),
                types.KeyboardButton("🔙 Retour menu")
            )
            
            bot.send_message(
                msg.chat.id,
                "Que voulez-vous faire ?",
                reply_markup=markup
            )
            
            # Réinitialiser le mode
            session_manager.set_mode(msg.chat.id, SessionMode.IDLE)
            
        else:
            bot.edit_message_text(
                f"❌ Erreur : {result['error']}",
                msg.chat.id,
                loading_msg.message_id
            )
    
    @bot.message_handler(func=lambda msg: msg.text == "💱 Nouvelle conversion" or msg.text == "🔄 Inverser")
    def handle_new_conversion(msg):
        """Démarre une nouvelle conversion ou inverse"""
        if msg.text == "🔄 Inverser":
            # Récupérer la dernière conversion
            session = session_manager.get_session(msg.chat.id)
            from_currency = session.data.get("from_currency")
            amount = session.data.get("amount")
            
            if from_currency and amount:
                # Dans l'inversion, on garde le même montant mais on échange les devises
                show_currency_from_selection(bot, msg)
            else:
                show_currency_from_selection(bot, msg)
        else:
            show_currency_from_selection(bot, msg)
    
    @bot.message_handler(func=lambda msg: msg.text == "💱 Taux du jour")
    def show_todays_rates(msg):
        """Affiche les taux du jour"""
        loading_msg = bot.send_message(msg.chat.id, "📊 Récupération des taux du jour...")
        
        rates_data = currency_service.get_rates("EUR")
        if not rates_data:
            bot.edit_message_text("❌ Impossible de récupérer les taux", msg.chat.id, loading_msg.message_id)
            return
        
        rates = rates_data.get("rates", {})
        date = rates_data.get("date", "N/A")
        
        main_currencies = ["USD", "GBP", "CHF", "JPY", "CAD", "XOF", "MAD", "DZD", "CNY", "AUD", "TND"]
        
        message = f"📊 *Taux de change du {date}*\n"
        message += "*Base : 1 EUR (€)*\n\n"
        
        common = currency_service.get_common_currencies()
        for currency in main_currencies:
            if currency in rates:
                name = common.get(currency, currency)
                symbol = get_currency_symbol(currency)
                message += f"• {symbol} {currency} : *{rates[currency]}*\n"
        
        message += "\n_💡 Pour convertir, tapez '💱 Nouvelle conversion'_"
        
        bot.edit_message_text(
            message,
            msg.chat.id,
            loading_msg.message_id,
            parse_mode="Markdown"
        )

def get_currency_from_keyboard():
    """Clavier pour la sélection de devise de départ"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        types.KeyboardButton("EUR (€)"),
        types.KeyboardButton("USD ($)"),
        types.KeyboardButton("GBP (£)"),
        types.KeyboardButton("CHF (Fr)"),
        types.KeyboardButton("JPY (¥)"),
        types.KeyboardButton("CAD (C$)"),
        types.KeyboardButton("XOF (CFA)"),
        types.KeyboardButton("MAD (DH)"),
        types.KeyboardButton("DZD (DA)")
    )
    markup.add(
        types.KeyboardButton("📋 Voir toutes les devises"),
        types.KeyboardButton("🔙 Retour menu")
    )
    return markup

def show_all_currencies(bot, msg):
    """Affiche toutes les devises disponibles"""
    common = currency_service.get_common_currencies()
    
    message = "📋 *Toutes les devises disponibles*\n\n"
    
    # Organiser par catégories
    categories = {
        "🌍 Europe": ["EUR", "GBP", "CHF"],
        "🌎 Amériques": ["USD", "CAD", "BRL"],
        "🌏 Asie/Océanie": ["JPY", "CNY", "KRW", "INR", "AUD"],
        "🌍 Afrique": ["XOF", "XAF", "MAD", "DZD", "TND", "NGN", "ZAR"],
        "🌍 Autres": ["RUB", "TRY", "SAR", "AED"]
    }
    
    for category, currencies in categories.items():
        message += f"*{category}*\n"
        for code in currencies:
            if code in common:
                name = common[code]
                symbol = get_currency_symbol(code)
                message += f"  • {symbol} *{code}* - {name}\n"
        message += "\n"
    
    message += "_💡 Vous pouvez taper le code (EUR, USD...) ou le nom de la devise_"
    
    bot.send_message(msg.chat.id, message, parse_mode="Markdown")

def extract_currency_code(text: str) -> str:
    """Extrait le code devise d'un texte"""
    text_upper = text.upper().strip()
    
    # Si c'est un code ISO direct (3 lettres)
    if re.match(r'^[A-Z]{3}$', text_upper):
        if text_upper in currency_service.get_common_currencies():
            return text_upper
    
    # Si c'est un bouton avec symbole (ex: "EUR (€)")
    match = re.match(r'([A-Z]{3})\s*[\(\[].*[\)\]]', text_upper)
    if match:
        code = match.group(1)
        if code in currency_service.get_common_currencies():
            return code
    
    # Correspondance noms -> codes
    name_to_code = {
        "EURO": "EUR", "EUROS": "EUR", "€": "EUR",
        "DOLLAR": "USD", "DOLLARS": "USD", "$": "USD",
        "LIVRE": "GBP", "LIVRES": "GBP", "STERLING": "GBP", "£": "GBP",
        "FRANC SUISSE": "CHF", "FRANCS SUISSES": "CHF",
        "YEN": "JPY", "YENS": "JPY", "¥": "JPY",
        "DOLLAR CANADIEN": "CAD",
        "DOLLAR AUSTRALIEN": "AUD",
        "YUAN": "CNY", "YUANS": "CNY",
        "FRANC CFA": "XOF", "CFA": "XOF",
        "DIRHAM": "MAD", "DIRHAMS": "MAD",
        "DINAR ALGÉRIEN": "DZD", "DINAR": "DZD",
        "DINAR TUNISIEN": "TND",
        "REAL": "BRL", "REALS": "BRL",
        "ROUPIE": "INR", "ROUPIES": "INR",
        "ROUBLE": "RUB", "ROUBLES": "RUB",
        "WON": "KRW", "WONS": "KRW",
        "NAIRA": "NGN", "NAIRAS": "NGN",
        "RAND": "ZAR", "RANDS": "ZAR"
    }
    
    # Chercher dans le texte
    for name, code in name_to_code.items():
        if name in text_upper:
            return code
    
    return None

def extract_amount(text: str) -> float:
    """Extrait un montant numérique du texte"""
    # Nettoyer le texte
    text = text.replace(',', '.').replace(' ', '')
    
    # Chercher un nombre
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    
    return None

def get_currency_symbol(currency_code: str) -> str:
    """Retourne le symbole d'une devise"""
    symbols = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£",
        "CHF": "Fr",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "CNY": "¥",
        "XOF": "CFA",
        "XAF": "CFA",
        "MAD": "DH",
        "DZD": "DA",
        "TND": "DT",
        "BRL": "R$",
        "INR": "₹",
        "RUB": "₽",
        "KRW": "₩",
        "NGN": "₦",
        "ZAR": "R"
    }
    return symbols.get(currency_code, "")

def get_main_currencies_list() -> list:
    """Retourne la liste des devises principales avec leurs symboles"""
    common = currency_service.get_common_currencies()
    main = ["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD", "CNY", "XOF", "MAD", "DZD", "TND"]
    
    result = []
    for code in main:
        if code in common:
            symbol = get_currency_symbol(code)
            name = common[code]
            result.append(f"{symbol} {code} - {name}")
    
    return result