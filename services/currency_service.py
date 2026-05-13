import requests
from datetime import datetime, timedelta
from config import Config

class CurrencyService:
    """Service de conversion de devises utilisant ExchangeRate-API V6"""

    def __init__(self):
        self.api_key = Config.EXCHANGE_RATE_API_KEY
        if not self.api_key:
            print("⚠️ ATTENTION: Clé API ExchangeRate non définie dans .env")
            print("Le service de conversion ne fonctionnera pas correctement.")
            self.base_url = None
        else:
            self.base_url = f"{Config.EXCHANGE_RATE_BASE_URL}/{self.api_key}/latest/"
            print("✅ Service de conversion initialisé avec la clé API")
        
        # Cache pour éviter trop de requêtes (valable 1 heure)
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
    
    def get_rates(self, base_currency: str = "EUR") -> dict:
        """Récupère les taux de change pour une devise de base."""
        if not self.base_url:
            return None
            
        now = datetime.now()
        # Vérifie si les taux pour cette devise sont déjà en cache et encore valides
        if base_currency in self.cache:
            cached_time = self.cache[base_currency].get("_timestamp")
            if cached_time and (now - cached_time) < self.cache_duration:
                print(f"📦 Utilisation du cache pour {base_currency}")
                return self.cache[base_currency]["data"]
        
        try:
            url = f"{self.base_url}{base_currency}"
            print(f"🌐 Requête API: {url}")
            response = requests.get(url)
            
            # Vérifie si la requête a réussi
            if response.status_code != 200:
                print(f"❌ Erreur API: Status {response.status_code}")
                return None
                
            data = response.json()
            
            # Vérifie le résultat de l'API
            if data.get("result") == "success":
                # Met en cache avec un timestamp
                self.cache[base_currency] = {
                    "data": data,
                    "_timestamp": now
                }
                print(f"✅ Taux récupérés pour {base_currency}")
                return data
            else:
                print(f"❌ Erreur API: {data.get('error-type', 'inconnue')}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return None
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> dict:
        """Convertit un montant d'une devise à une autre."""
        # Normalise les codes devises
        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()
        
        # Récupère les taux
        rates_data = self.get_rates(from_currency)
        if not rates_data:
            return {"success": False, "error": "Impossible de récupérer les taux de change"}
        
        rates = rates_data.get("conversion_rates", {})
        if to_currency not in rates:
            return {"success": False, "error": f"Devise '{to_currency}' non trouvée"}
        
        # Calcul de la conversion
        rate = rates[to_currency]
        converted_amount = amount * rate
        
        return {
            "success": True,
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "rate": rate,
            "result": round(converted_amount, 2),
            "date": rates_data.get("time_last_update_utc", "N/A")[:10]
        }
    
    def get_common_currencies(self) -> dict:
        """Retourne les devises les plus courantes avec leurs noms."""
        return {
            "EUR": "Euro",
            "USD": "Dollar américain",
            "GBP": "Livre sterling",
            "CHF": "Franc suisse",
            "JPY": "Yen japonais",
            "CAD": "Dollar canadien",
            "AUD": "Dollar australien",
            "CNY": "Yuan chinois",
            "XOF": "Franc CFA (UEMOA)",
            "XAF": "Franc CFA (CEMAC)",
            "MAD": "Dirham marocain",
            "DZD": "Dinar algérien",
            "TND": "Dinar tunisien",
            "BRL": "Real brésilien",
            "INR": "Roupie indienne",
            "RUB": "Rouble russe",
            "KRW": "Won sud-coréen",
            "NGN": "Naira nigérian",
            "ZAR": "Rand sud-africain"
        }

currency_service = CurrencyService()