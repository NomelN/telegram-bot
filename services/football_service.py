"""Service API-Football (v3, point d'accès direct api-sports.io).

Notes plan gratuit :
- Seasons 2022-2024 uniquement
- ?last / ?next interdits → on récupère + on filtre côté client
- ?search ne tolère ni 'league' ni 'season', ni caractères spéciaux
"""

import re
import requests
import unicodedata
from datetime import datetime, timedelta
from typing import Optional

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

AVAILABLE_SEASONS = [2022, 2023, 2024]


def current_season() -> int:
    """Saison européenne la plus récente accessible (plafonnée par config)."""
    now = datetime.now()
    natural = now.year if now.month >= 7 else now.year - 1
    return min(natural, Config.FOOTBALL_MAX_SEASON)


def _sanitize_search(name: str) -> str:
    """Retire accents et caractères non alphanumériques (contrainte API)."""
    if not name:
        return ""
    nfkd = unicodedata.normalize("NFKD", name)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9 ]", " ", no_accents).strip()


def _fixture_date(fx: dict) -> str:
    return fx.get("fixture", {}).get("date", "")


class FootballService:
    """Wrapper API-Football. Cache mémoire 1h pour économiser le quota gratuit."""

    def __init__(self):
        self.api_key = Config.FOOTBALL_API_KEY
        self.base_url = Config.FOOTBALL_BASE_URL
        self.cache: dict = {}
        self.cache_duration = timedelta(hours=1)
        if not self.api_key:
            logger.warning("FOOTBALL_API_KEY non définie — service indisponible")
        else:
            logger.info("Service Football initialisé")

    def _get(self, endpoint: str, params: dict) -> Optional[dict]:
        if not self.api_key:
            return None

        cache_key = f"{endpoint}?{sorted(params.items())}"
        now = datetime.now()
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if (now - cached_time) < self.cache_duration:
                logger.debug("Cache hit: %s", cache_key)
                return cached_data

        url = f"{self.base_url}/{endpoint}"
        headers = {"x-apisports-key": self.api_key}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("errors"):
                logger.error("API-Football erreurs: %s", data["errors"])
                return None
            self.cache[cache_key] = (now, data)
            return data
        except requests.RequestException as e:
            logger.exception("Erreur réseau API-Football: %s", e)
            return None

    def get_standings(self, league_id: int, season: Optional[int] = None) -> list[dict]:
        data = self._get("standings", {
            "league": league_id,
            "season": season or current_season(),
        })
        if not data or not data.get("response"):
            return []
        response = data["response"][0]
        standings = response.get("league", {}).get("standings", [])
        return standings[0] if standings else []

    def get_top_scorers(self, league_id: int, season: Optional[int] = None) -> list[dict]:
        data = self._get("players/topscorers", {
            "league": league_id,
            "season": season or current_season(),
        })
        return data.get("response", []) if data else []

    def get_top_assists(self, league_id: int, season: Optional[int] = None) -> list[dict]:
        data = self._get("players/topassists", {
            "league": league_id,
            "season": season or current_season(),
        })
        return data.get("response", []) if data else []

    def search_teams(self, name: str, limit: int = 5) -> list[dict]:
        """Recherche d'équipes par nom (top N). Le plan gratuit n'accepte ni
        league ni season en combinaison avec search."""
        cleaned = _sanitize_search(name)
        if len(cleaned) < 3:
            return []
        data = self._get("teams", {"search": cleaned})
        if not data or not data.get("response"):
            return []
        return [r["team"] for r in data["response"][:limit] if r.get("team")]

    def get_team_statistics(self, team_id: int, league_id: int, season: Optional[int] = None) -> Optional[dict]:
        data = self._get("teams/statistics", {
            "team": team_id,
            "league": league_id,
            "season": season or current_season(),
        })
        if not data:
            return None
        return data.get("response") or None

    def get_h2h(self, team_id_1: int, team_id_2: int, limit: int = 10) -> list[dict]:
        """Confrontations directes (tri côté client car ?last interdit)."""
        data = self._get("fixtures/headtohead", {
            "h2h": f"{team_id_1}-{team_id_2}",
        })
        fixtures = data.get("response", []) if data else []
        fixtures.sort(key=_fixture_date, reverse=True)
        return fixtures[:limit]

