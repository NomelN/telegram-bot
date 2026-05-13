import requests
from config import Config

class MeteoService:
    """Service pour récupérer les données météo"""
    
    @staticmethod
    def get_weather(city: str) -> dict:
        """Récupère la météo d'une ville"""
        params = {
            'q': city,
            'appid': Config.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'fr'
        }
        
        try:
            response = requests.get(Config.OPENWEATHER_URL, params=params)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def format_weather(data: dict, city: str) -> str:
        """Formate les données météo en message lisible"""
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        visibility = data.get('visibility')
        visibility_str = f"{visibility / 1000:.1f} km" if isinstance(visibility, (int, float)) else "N/A"

        return (
            f"🌍 *Météo — {city.title()}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"_{weather['description'].capitalize()}_\n\n"
            f"🌡️  *Température* : {main['temp']:.1f} °C\n"
            f"🤒  *Ressenti* : {main['feels_like']:.1f} °C\n"
            f"💧  *Humidité* : {main['humidity']} %\n"
            f"🌬️  *Vent* : {wind['speed']} m/s\n\n"
            f"📊  *Pression* : {main['pressure']} hPa\n"
            f"👁️  *Visibilité* : {visibility_str}"
        )