from typing import Dict, Any, Optional
from enum import Enum

class SessionMode(Enum):
    """Modes de session utilisateur"""
    IDLE = "idle"
    WAITING_CITY = "waiting_city"
    WAITING_THEME = "waiting_theme"
    WAITING_DEPARTURE = "waiting_departure"
    WAITING_ARRIVAL = "waiting_arrival"
    CHAT_FREE = "chat_free"
    WAITING_ACTION = "waiting_action"

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
        
        # Limiter la taille de l'historique
        max_length = 20  # À remplacer par Config.MAX_HISTORY_LENGTH
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