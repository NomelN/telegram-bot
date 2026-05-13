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
        
        return f"""
            🌍 *Météo pour {city}*

            🌡️ Température : {main['temp']}°C
            🤒 Ressenti : {main['feels_like']}°C
            💧 Humidité : {main['humidity']}%
            🌬️ Vent : {wind['speed']} km/h
            🌥️ Conditions : {weather['description'].capitalize()}

            📊 Pression : {main['pressure']} hPa
            👁️ Visibilité : {data.get('visibility', 'N/A')} mètres
        """