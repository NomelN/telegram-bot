# pyrefly: ignore [missing-import]
from datetime import datetime
from telebot import TeleBot

from config import Config
from handlers.menu import show_main_menu
from services import football_service
from services.football_service import AVAILABLE_SEASONS, current_season
from utils.constants import (
    BACK_TO_MENU,
    FOOTBALL_RESULTS,
    FOOTBALL_STANDINGS,
    FOOTBALL_TOP_SCORERS,
    FOOTBALL_TOP_ASSISTS,
    FOOTBALL_CHANGE_SEASON,
)
from utils.keyboards import Keyboards
from utils.logger import get_logger
from utils.session_manager import session_manager, SessionMode

logger = get_logger(__name__)

SEPARATOR = "━━━━━━━━━━━━━━━━━━━"

ACTIONS_NEEDING_LEAGUE = {
    FOOTBALL_RESULTS,
    FOOTBALL_STANDINGS,
    FOOTBALL_TOP_SCORERS,
    FOOTBALL_TOP_ASSISTS,
}


def _get_season(msg) -> int:
    session = session_manager.get_session(msg.chat.id)
    return session.data.get("football_season") or current_season()


def _format_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m %H:%M")
    except (ValueError, AttributeError):
        return iso or "?"


def _format_fixture_result(fx: dict) -> str:
    home = fx["teams"]["home"]["name"]
    away = fx["teams"]["away"]["name"]
    goals = fx.get("goals", {})
    score = f"{goals.get('home', '-')} - {goals.get('away', '-')}"
    date = _format_date(fx["fixture"]["date"])
    return f"`{date}`  *{home}* {score} *{away}*"


def _format_standings(rows: list) -> str:
    if not rows:
        return "_Classement indisponible._"
    lines = ["`#   Équipe              J   Pts`"]
    for row in rows[:20]:
        rank = row.get("rank", "?")
        team = row.get("team", {}).get("name", "?")[:18]
        played = row.get("all", {}).get("played", "?")
        pts = row.get("points", "?")
        lines.append(f"`{rank:>2}  {team:<18} {played:>3}  {pts:>3}`")
    return "\n".join(lines)


def _format_top_scorers(rows: list) -> str:
    if not rows:
        return "_Données indisponibles._"
    lines = ["`#   Joueur              Équipe          Buts`"]
    for i, row in enumerate(rows[:15], 1):
        player = row.get("player", {}).get("name", "?")[:18]
        stats = (row.get("statistics") or [{}])[0]
        team = stats.get("team", {}).get("name", "?")[:14]
        goals = (stats.get("goals") or {}).get("total") or 0
        lines.append(f"`{i:>2}  {player:<18} {team:<14} {goals:>4}`")
    return "\n".join(lines)


def _format_top_assists(rows: list) -> str:
    if not rows:
        return "_Données indisponibles._"
    lines = ["`#   Joueur              Équipe          Pass`"]
    for i, row in enumerate(rows[:15], 1):
        player = row.get("player", {}).get("name", "?")[:18]
        stats = (row.get("statistics") or [{}])[0]
        team = stats.get("team", {}).get("name", "?")[:14]
        assists = (stats.get("goals") or {}).get("assists") or 0
        lines.append(f"`{i:>2}  {player:<18} {team:<14} {assists:>4}`")
    return "\n".join(lines)


def ask_football_action(bot: TeleBot, msg):
    """Affiche le sous-menu Football avec la saison sélectionnée."""
    session_manager.set_mode(msg.chat.id, SessionMode.WAITING_FOOTBALL_ACTION)
    season = _get_season(msg)
    bot.send_message(
        msg.chat.id,
        f"⚽ *Football* — saison *{season}-{season + 1}*\n"
        f"{SEPARATOR}\n"
        "Que voulez-vous consulter ?",
        parse_mode="Markdown",
        reply_markup=Keyboards.football_menu(),
    )


def register_football_handlers(bot: TeleBot):
    """Handlers pour la rubrique Football."""

    @bot.message_handler(func=lambda m: m.text == "⚽ Football")
    def _entry(msg):
        ask_football_action(bot, msg)

    @bot.message_handler(
        func=lambda m: m.text == FOOTBALL_CHANGE_SEASON
        and session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_ACTION
    )
    def change_season(msg):
        session_manager.set_mode(msg.chat.id, SessionMode.WAITING_FOOTBALL_SEASON)
        bot.send_message(
            msg.chat.id,
            "🗓️ *Choix de la saison*\n"
            f"{SEPARATOR}\n"
            "_Plan gratuit : 2022, 2023, 2024 uniquement._",
            parse_mode="Markdown",
            reply_markup=Keyboards.football_seasons(),
        )

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_SEASON
    )
    def pick_season(msg):
        if msg.text == BACK_TO_MENU:
            show_main_menu(bot, msg)
            return
        try:
            year = int(msg.text)
        except ValueError:
            bot.send_message(msg.chat.id, "❌ Saison invalide.")
            return
        if year not in AVAILABLE_SEASONS:
            bot.send_message(msg.chat.id, "❌ Saison hors plan gratuit (2022-2024).")
            return
        session_manager.set_mode(
            msg.chat.id,
            SessionMode.WAITING_FOOTBALL_ACTION,
            {"football_season": year},
        )
        bot.send_message(msg.chat.id, f"✅  Saison *{year}-{year + 1}* sélectionnée.", parse_mode="Markdown")
        ask_football_action(bot, msg)

    @bot.message_handler(
        func=lambda m: m.text in ACTIONS_NEEDING_LEAGUE
        and session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_ACTION
    )
    def choose_league(msg):
        session_manager.set_mode(
            msg.chat.id,
            SessionMode.WAITING_FOOTBALL_LEAGUE,
            {"football_action": msg.text},
        )
        bot.send_message(
            msg.chat.id,
            f"*{msg.text}*\n"
            f"{SEPARATOR}\n"
            "Choisissez une compétition :",
            parse_mode="Markdown",
            reply_markup=Keyboards.football_leagues(),
        )

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_LEAGUE
    )
    def render_league(msg):
        if msg.text == BACK_TO_MENU:
            show_main_menu(bot, msg)
            return

        league_id = Config.FOOTBALL_LEAGUES.get(msg.text)
        if not league_id:
            bot.send_message(msg.chat.id, "❌ Compétition non reconnue.")
            return

        session = session_manager.get_session(msg.chat.id)
        action = session.data.get("football_action")
        season = _get_season(msg)
        loading = bot.send_message(msg.chat.id, "🔍 Récupération des données…")

        try:
            if action == FOOTBALL_RESULTS:
                rows = football_service.get_recent_results(league_id, season=season)
                body = "\n".join(_format_fixture_result(fx) for fx in rows) if rows else "_Aucun résultat._"
                text = f"📊 *Résultats — {msg.text}*\n_Saison {season}-{season + 1}_\n{SEPARATOR}\n{body}"

            elif action == FOOTBALL_STANDINGS:
                rows = football_service.get_standings(league_id, season=season)
                text = f"🏆 *Classement — {msg.text}*\n_Saison {season}-{season + 1}_\n{SEPARATOR}\n{_format_standings(rows)}"

            elif action == FOOTBALL_TOP_SCORERS:
                rows = football_service.get_top_scorers(league_id, season=season)
                text = f"⚽ *Top buteurs — {msg.text}*\n_Saison {season}-{season + 1}_\n{SEPARATOR}\n{_format_top_scorers(rows)}"

            elif action == FOOTBALL_TOP_ASSISTS:
                rows = football_service.get_top_assists(league_id, season=season)
                text = f"🎯 *Top passeurs — {msg.text}*\n_Saison {season}-{season + 1}_\n{SEPARATOR}\n{_format_top_assists(rows)}"

            else:
                text = "_Action inconnue._"

            bot.edit_message_text(
                text,
                msg.chat.id,
                loading.message_id,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.exception("Erreur Football: %s", e)
            bot.edit_message_text(
                f"❌ Erreur : {e}",
                msg.chat.id,
                loading.message_id,
            )

        ask_football_action(bot, msg)
