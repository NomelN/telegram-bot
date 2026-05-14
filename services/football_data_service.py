"""Service football-data.org v4 (plan gratuit, 10 req/min, saison actuelle)."""

import requests
from datetime import datetime, timedelta
from typing import Optional

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class FootballDataService:
    """Wrapper football-data.org. Cache 5 min pour rester sous la limite 10 req/min."""

    def __init__(self):
        self.api_key = Config.FOOTBALL_DATA_API_KEY
        self.base_url = Config.FOOTBALL_DATA_BASE_URL
        self.cache: dict = {}
        self.cache_duration = timedelta(minutes=5)
        if not self.api_key:
            logger.warning("FOOTBALL_DATA_API_KEY non définie — service indisponible")
        else:
            logger.info("Service football-data.org initialisé")

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        if not self.api_key:
            return None
        params = params or {}
        cache_key = f"{endpoint}?{sorted(params.items())}"
        now = datetime.now()
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if (now - cached_time) < self.cache_duration:
                logger.debug("Cache hit: %s", cache_key)
                return cached_data

        url = f"{self.base_url}/{endpoint}"
        headers = {"X-Auth-Token": self.api_key}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 429:
                logger.error("football-data : rate limit dépassé (10 req/min)")
                return None
            if response.status_code == 403:
                logger.error("football-data : compétition non incluse dans ton plan (%s)", endpoint)
                return None
            response.raise_for_status()
            data = response.json()
            self.cache[cache_key] = (now, data)
            return data
        except requests.RequestException as e:
            logger.exception("Erreur réseau football-data : %s", e)
            return None

    def get_today_matches(self) -> list[dict]:
        """Matchs du jour sur toutes les compétitions du plan."""
        data = self._get("matches")
        return data.get("matches", []) if data else []

    def get_standings(self, competition_code: str) -> list[dict]:
        """Classement de la saison en cours."""
        data = self._get(f"competitions/{competition_code}/standings")
        if not data:
            return []
        standings = data.get("standings", [])
        for s in standings:
            if s.get("type") == "TOTAL":
                return s.get("table", [])
        return standings[0].get("table", []) if standings else []

    def get_top_scorers(self, competition_code: str, limit: int = 15) -> list[dict]:
        """Top buteurs de la saison en cours."""
        data = self._get(f"competitions/{competition_code}/scorers", {"limit": limit})
        return data.get("scorers", []) if data else []

    def get_current_matchday(self, competition_code: str) -> list[dict]:
        """Matchs de la journée en cours d'une compétition."""
        comp = self._get(f"competitions/{competition_code}")
        if not comp:
            return []
        matchday = comp.get("currentSeason", {}).get("currentMatchday")
        if not matchday:
            return []
        data = self._get(f"competitions/{competition_code}/matches", {"matchday": matchday})
        matches = data.get("matches", []) if data else []
        return matches
