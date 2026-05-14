# pyrefly: ignore [missing-import]
from telebot import TeleBot, types

from config import Config
from handlers.menu import show_main_menu
from services import football_service
from services.football_service import AVAILABLE_SEASONS, current_season
from utils.constants import (
    BACK_TO_MENU,
    FOOTBALL_STANDINGS,
    FOOTBALL_TOP_SCORERS,
    FOOTBALL_TOP_ASSISTS,
    FOOTBALL_TEAM_STATS,
    FOOTBALL_H2H,
    FOOTBALL_CHANGE_SEASON,
)
from utils.keyboards import Keyboards
from utils.logger import get_logger
from utils.session_manager import session_manager, SessionMode

logger = get_logger(__name__)

SEPARATOR = "━━━━━━━━━━━━"

ACTIONS_LEAGUE_DIRECT = {
    FOOTBALL_STANDINGS,
    FOOTBALL_TOP_SCORERS,
    FOOTBALL_TOP_ASSISTS,
}

PENDING_STATS = "stats"
PENDING_H2H_1 = "h2h_1"
PENDING_H2H_2 = "h2h_2"


# ─────────────── Helpers ───────────────

def _get_season(msg) -> int:
    session = session_manager.get_session(msg.chat.id)
    return session.data.get("football_season") or current_season()


def _team_button_label(team: dict, idx: int) -> str:
    name = team.get("name", "?")
    country = team.get("country") or "?"
    return f"{idx}. {name} ({country})"


# ─────────────── Formatters ───────────────

def _format_fixture_result(fx: dict) -> str:
    home = fx["teams"]["home"]["name"]
    away = fx["teams"]["away"]["name"]
    goals = fx.get("goals", {})
    score = f"{goals.get('home', '-')} - {goals.get('away', '-')}"
    date_iso = fx.get("fixture", {}).get("date", "")
    date = date_iso[:10] if date_iso else "?"
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


def _format_team_stats(stats: dict) -> str:
    team = stats.get("team", {}).get("name", "?")
    league = stats.get("league", {}).get("name", "?")
    form = stats.get("form") or "—"
    fixtures = stats.get("fixtures", {}) or {}
    played = fixtures.get("played", {}).get("total", 0)
    wins = fixtures.get("wins", {}).get("total", 0)
    draws = fixtures.get("draws", {}).get("total", 0)
    loses = fixtures.get("loses", {}).get("total", 0)
    goals = stats.get("goals", {}) or {}
    gf = (goals.get("for") or {}).get("total", {}).get("total", 0)
    ga = (goals.get("against") or {}).get("total", {}).get("total", 0)
    avg_gf = (goals.get("for") or {}).get("average", {}).get("total", "—")
    avg_ga = (goals.get("against") or {}).get("average", {}).get("total", "—")
    cs = (stats.get("clean_sheet") or {}).get("total", 0)
    failed = (stats.get("failed_to_score") or {}).get("total", 0)
    form_recent = form[-10:] if form else "—"

    return (
        f"📈 *{team}*\n"
        f"_{league}_\n"
        f"{SEPARATOR}\n"
        f"🎯  *Forme récente* : `{form_recent}`\n\n"
        f"📋  *Bilan* — {played} matchs\n"
        f"• ✅ Victoires : {wins}\n"
        f"• 🤝 Nuls : {draws}\n"
        f"• ❌ Défaites : {loses}\n\n"
        f"⚽  *Attaque* : {gf} buts ({avg_gf}/match)\n"
        f"🛡️  *Défense* : {ga} buts encaissés ({avg_ga}/match)\n"
        f"🧤  *Clean sheets* : {cs}\n"
        f"🚫  *Matchs sans marquer* : {failed}"
    )


def _format_h2h(team1: dict, team2: dict, fixtures: list) -> str:
    n1, n2 = team1.get("name", "?"), team2.get("name", "?")
    if not fixtures:
        return f"⚔️  *{n1}* vs *{n2}*\n{SEPARATOR}\n_Aucun historique disponible._"

    wins1 = wins2 = draws = 0
    goals1 = goals2 = 0
    id1 = team1.get("id")

    for fx in fixtures:
        gh = fx.get("goals", {}).get("home")
        ga = fx.get("goals", {}).get("away")
        if gh is None or ga is None:
            continue
        home_id = fx["teams"]["home"]["id"]
        if home_id == id1:
            goals1 += gh
            goals2 += ga
            if gh > ga: wins1 += 1
            elif gh < ga: wins2 += 1
            else: draws += 1
        else:
            goals2 += gh
            goals1 += ga
            if gh > ga: wins2 += 1
            elif gh < ga: wins1 += 1
            else: draws += 1

    history = "\n".join(_format_fixture_result(fx) for fx in fixtures[:5])
    return (
        f"⚔️  *{n1}* vs *{n2}*\n"
        f"{SEPARATOR}\n"
        f"📊  *Bilan sur {len(fixtures)} matchs*\n"
        f"• {n1} : {wins1} victoires ({goals1} buts)\n"
        f"• {n2} : {wins2} victoires ({goals2} buts)\n"
        f"• Nuls : {draws}\n\n"
        f"📅  *Derniers matchs*\n{history}"
    )


# ─────────────── UI ───────────────

def ask_football_action(bot: TeleBot, msg):
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


def _ask_text(bot: TeleBot, msg, prompt: str):
    bot.send_message(msg.chat.id, prompt, parse_mode="Markdown", reply_markup=Keyboards.back_to_menu())


def _show_team_picker(bot: TeleBot, msg, candidates: list, pending_action: str):
    session = session_manager.get_session(msg.chat.id)
    session.data["team_candidates"] = candidates
    session.data["pending_team_action"] = pending_action
    session_manager.set_mode(msg.chat.id, SessionMode.WAITING_FOOTBALL_TEAM_PICK)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for i, team in enumerate(candidates, 1):
        markup.add(_team_button_label(team, i))
    markup.add(BACK_TO_MENU)

    bot.send_message(
        msg.chat.id,
        f"🔎 *Plusieurs équipes correspondent*\n{SEPARATOR}\n"
        "Choisissez ci-dessous :",
        parse_mode="Markdown",
        reply_markup=markup,
    )


def _resolve_team_input(bot: TeleBot, msg, pending_action: str):
    if msg.text == BACK_TO_MENU:
        show_main_menu(bot, msg)
        return

    loading = bot.send_message(msg.chat.id, "🔍 Recherche…")
    candidates = football_service.search_teams(msg.text, limit=5)

    if not candidates:
        bot.edit_message_text(
            f"❌ Aucune équipe trouvée pour '*{msg.text}*'.\nRéessayez avec un nom plus complet :",
            msg.chat.id, loading.message_id, parse_mode="Markdown",
        )
        return

    bot.delete_message(msg.chat.id, loading.message_id)

    if len(candidates) == 1:
        _dispatch_team_action(bot, msg, candidates[0], pending_action)
    else:
        _show_team_picker(bot, msg, candidates, pending_action)


def _dispatch_team_action(bot: TeleBot, msg, team: dict, pending_action: str):
    session = session_manager.get_session(msg.chat.id)

    if pending_action == PENDING_STATS:
        _render_team_stats(bot, msg, team)
    elif pending_action == PENDING_H2H_1:
        session.data["h2h_team1"] = team
        session_manager.set_mode(msg.chat.id, SessionMode.WAITING_FOOTBALL_H2H_TEAM2)
        _ask_text(
            bot, msg,
            f"✅  Équipe 1 : *{team.get('name')}* ({team.get('country', '?')})\n\n"
            "Tapez le nom de la *deuxième équipe* :"
        )
    elif pending_action == PENDING_H2H_2:
        team1 = session.data.get("h2h_team1")
        if not team1:
            bot.send_message(msg.chat.id, "❌ Contexte perdu, recommencez.")
            ask_football_action(bot, msg)
            return
        if team["id"] == team1["id"]:
            bot.send_message(msg.chat.id, "❌ Les deux équipes doivent être différentes.")
            ask_football_action(bot, msg)
            return
        _render_h2h(bot, msg, team1, team)


# ─────────────── Rendering ───────────────

def _render_team_stats(bot: TeleBot, msg, team: dict):
    session = session_manager.get_session(msg.chat.id)
    league_id = session.data.get("football_league_id")
    league_label = session.data.get("football_league_label", "")
    season = _get_season(msg)

    loading = bot.send_message(msg.chat.id, "🔍 Récupération des stats…")
    try:
        stats = football_service.get_team_statistics(team["id"], league_id, season=season)
        if not stats:
            bot.edit_message_text(
                f"❌ Pas de stats pour *{team.get('name')}* dans {league_label} ({season}-{season + 1}).\n"
                "_L'équipe n'y a peut-être pas joué cette saison._",
                msg.chat.id, loading.message_id, parse_mode="Markdown",
            )
        else:
            bot.edit_message_text(
                _format_team_stats(stats),
                msg.chat.id, loading.message_id, parse_mode="Markdown",
            )
    except Exception as e:
        logger.exception("Erreur stats équipe: %s", e)
        bot.edit_message_text(f"❌ Erreur : {e}", msg.chat.id, loading.message_id)
    ask_football_action(bot, msg)


def _render_h2h(bot: TeleBot, msg, team1: dict, team2: dict):
    loading = bot.send_message(msg.chat.id, "🔍 Récupération de l'historique…")
    try:
        fixtures = football_service.get_h2h(team1["id"], team2["id"], limit=10)
        bot.edit_message_text(
            _format_h2h(team1, team2, fixtures),
            msg.chat.id, loading.message_id, parse_mode="Markdown",
        )
    except Exception as e:
        logger.exception("Erreur H2H: %s", e)
        bot.edit_message_text(f"❌ Erreur : {e}", msg.chat.id, loading.message_id)
    ask_football_action(bot, msg)


# ─────────────── Handlers ───────────────

def register_football_handlers(bot: TeleBot):

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
        func=lambda m: m.text in (ACTIONS_LEAGUE_DIRECT | {FOOTBALL_TEAM_STATS})
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
            f"*{msg.text}*\n{SEPARATOR}\nChoisissez une compétition :",
            parse_mode="Markdown",
            reply_markup=Keyboards.football_leagues(),
        )

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_LEAGUE
    )
    def after_league(msg):
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
        session.data["football_league_id"] = league_id
        session.data["football_league_label"] = msg.text

        if action == FOOTBALL_TEAM_STATS:
            session_manager.set_mode(msg.chat.id, SessionMode.WAITING_FOOTBALL_STATS_TEAM)
            _ask_text(
                bot, msg,
                f"📈 *Stats d'équipe — {msg.text}*\n{SEPARATOR}\n"
                "Tapez le *nom complet de l'équipe*\n"
                "_(ex: Paris Saint Germain, Real Madrid, Lyon)_"
            )
            return

        loading = bot.send_message(msg.chat.id, "🔍 Récupération des données…")
        try:
            if action == FOOTBALL_STANDINGS:
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
            bot.edit_message_text(text, msg.chat.id, loading.message_id, parse_mode="Markdown")
        except Exception as e:
            logger.exception("Erreur Football: %s", e)
            bot.edit_message_text(f"❌ Erreur : {e}", msg.chat.id, loading.message_id)

        ask_football_action(bot, msg)

    @bot.message_handler(
        func=lambda m: m.text == FOOTBALL_H2H
        and session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_ACTION
    )
    def start_h2h(msg):
        session_manager.set_mode(msg.chat.id, SessionMode.WAITING_FOOTBALL_H2H_TEAM1)
        _ask_text(
            bot, msg,
            f"⚔️ *Confrontations directes*\n{SEPARATOR}\n"
            "Tapez le nom de la *première équipe*\n"
            "_(ex: Paris Saint Germain, Real Madrid)_"
        )

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_STATS_TEAM
    )
    def stats_team_input(msg):
        _resolve_team_input(bot, msg, PENDING_STATS)

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_H2H_TEAM1
    )
    def h2h_team1_input(msg):
        _resolve_team_input(bot, msg, PENDING_H2H_1)

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_H2H_TEAM2
    )
    def h2h_team2_input(msg):
        _resolve_team_input(bot, msg, PENDING_H2H_2)

    @bot.message_handler(
        func=lambda m: session_manager.get_mode(m.chat.id) == SessionMode.WAITING_FOOTBALL_TEAM_PICK
    )
    def pick_team(msg):
        if msg.text == BACK_TO_MENU:
            show_main_menu(bot, msg)
            return

        session = session_manager.get_session(msg.chat.id)
        candidates = session.data.get("team_candidates") or []
        pending = session.data.get("pending_team_action")

        chosen = None
        for i, team in enumerate(candidates, 1):
            if msg.text == _team_button_label(team, i):
                chosen = team
                break

        if not chosen:
            bot.send_message(msg.chat.id, "❌ Choix invalide, utilisez les boutons proposés.")
            return

        _dispatch_team_action(bot, msg, chosen, pending)
