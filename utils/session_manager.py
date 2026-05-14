from typing import Dict, Any, Optional
from enum import Enum
from config import Config

class SessionMode(Enum):
    """Modes de session utilisateur"""
    IDLE = "idle"
    WAITING_CITY = "waiting_city"
    WAITING_THEME = "waiting_theme"
    WAITING_DEPARTURE = "waiting_departure"
    WAITING_ARRIVAL = "waiting_arrival"
    CHAT_FREE = "chat_free"
    WAITING_WEATHER_ACTION = "waiting_weather_action"
    WAITING_NEWS_ACTION = "waiting_news_action"
    WAITING_ROUTE_ACTION = "waiting_route_action"
    WAITING_CURRENCY_FROM = "waiting_currency_from"
    WAITING_CURRENCY_AMOUNT = "waiting_currency_amount"
    WAITING_CURRENCY_TO = "waiting_currency_to"
    WAITING_FOOTBALL_ACTION = "waiting_football_action"
    WAITING_FOOTBALL_LEAGUE = "waiting_football_league"
    WAITING_FOOTBALL_SEASON = "waiting_football_season"
    WAITING_FOOTBALL_STATS_TEAM = "waiting_football_stats_team"
    WAITING_FOOTBALL_H2H_TEAM1 = "waiting_football_h2h_team1"
    WAITING_FOOTBALL_H2H_TEAM2 = "waiting_football_h2h_team2"
    WAITING_FOOTBALL_TEAM_PICK = "waiting_football_team_pick"

class UserSession:
    """Gère les données de session d'un utilisateur"""
    
    def __init__(self):
        self.mode: SessionMode = SessionMode.IDLE
        self.data: Dict[str, Any] = {}
        self.history: list = []
    
    def reset(self):
        """Réinitialise la session"""
        self.mode = SessionMode.IDLE
        self.data = {}
        self.history = []
    
    def add_to_history(self, message: str, role: str = "user"):
        """Ajoute un message à l'historique"""
        self.history.append({"role": role, "content": message})
        
        max_length = Config.MAX_HISTORY_LENGTH
        if len(self.history) > max_length:
            self.history = self.history[-max_length:]

class SessionManager:
    """Gestionnaire de sessions utilisateur"""
    
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
    
    def get_session(self, user_id: int) -> UserSession:
        """Récupère ou crée une session utilisateur"""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession()
        return self._sessions[user_id]
    
    def reset_session(self, user_id: int):
        """Réinitialise la session d'un utilisateur"""
        if user_id in self._sessions:
            self._sessions[user_id].reset()
    
    def set_mode(self, user_id: int, mode: SessionMode, data: Dict = None):
        """Définit le mode de session"""
        session = self.get_session(user_id)
        session.mode = mode
        if data:
            session.data.update(data)
    
    def get_mode(self, user_id: int) -> SessionMode:
        """Récupère le mode de session"""
        return self.get_session(user_id).mode

# Instance globale du gestionnaire de sessions
session_manager = SessionManager()