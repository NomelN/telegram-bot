# 🤖 Assistant IA Thématique — Bot Telegram

Bot Telegram multi-fonctions écrit en Python, qui combine plusieurs API externes (météo, actualités, devises, football) avec un assistant IA conversationnel basé sur DeepSeek.

---

## ✨ Fonctionnalités

| Module | Description | API utilisée |
|---|---|---|
| 🌤️ **Météo** | Météo en temps réel pour n'importe quelle ville | OpenWeather |
| 📰 **Actualités** | Résumé des dernières actualités par thème | NewsAPI + DeepSeek |
| 🗺️ **Itinéraire** | Planification de trajets entre deux villes | DeepSeek |
| 💱 **Convertisseur** | Conversion de devises en temps réel (taux quotidiens) | ExchangeRate-API V6 |
| ⚽ **Football** | Classements, top buteurs, stats d'équipe, confrontations, matchs du jour, classement live | API-Football + football-data.org |
| 💬 **Chat Libre** | Discussion ouverte avec l'IA | DeepSeek |

### Détails de la rubrique Football

Le module Football combine deux sources :

- **Saisons 2022-2024** (API-Football, plan gratuit) : classements, stats d'équipe, top buteurs/passeurs, confrontations directes.
- **Saison actuelle** (football-data.org, plan gratuit) : matchs du jour live, classement live, top buteurs live, journée en cours.

Compétitions exposées : Ligue 1, Premier League, La Liga, Bundesliga, Serie A, Ligue des Champions, CAN, Coupe du Monde (selon l'API).

---

## 🚀 Démarrage

### 1. Prérequis

- Python 3.10+
- Un bot Telegram créé via [@BotFather](https://t.me/BotFather) (récupère le `TELEGRAM_TOKEN`)
- Les clés API des services utilisés (voir section suivante)

### 2. Installation

```bash
git clone <url-de-ce-repo>
cd bot-telegram
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Crée un fichier `.env` à la racine du projet :

```env
# Obligatoires
TELEGRAM_TOKEN=xxx
DEEPSEEK_API_KEY=xxx
OPENWEATHER_API_KEY=xxx
EXCHANGE_RATE_API_KEY=xxx

# Optionnelles
NEWS_API_KEY=xxx
FOOTBALL_API_KEY=xxx
FOOTBALL_DATA_API_KEY=xxx

# Paramètres (optionnels, avec valeurs par défaut)
MAX_HISTORY_LENGTH=20
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=1000
LOG_LEVEL=INFO
FOOTBALL_MAX_SEASON=2024
```

#### Où obtenir les clés

| Variable | URL | Plan |
|---|---|---|
| `TELEGRAM_TOKEN` | [@BotFather](https://t.me/BotFather) | gratuit |
| `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com) | crédit initial offert |
| `OPENWEATHER_API_KEY` | [openweathermap.org](https://openweathermap.org/api) | gratuit |
| `EXCHANGE_RATE_API_KEY` | [exchangerate-api.com](https://www.exchangerate-api.com/) | gratuit (1500 req/mois) |
| `NEWS_API_KEY` | [newsapi.org](https://newsapi.org/) | gratuit (100 req/jour) |
| `FOOTBALL_API_KEY` | [api-football.com](https://www.api-football.com/) | gratuit (100 req/jour, saisons 2022-2024) |
| `FOOTBALL_DATA_API_KEY` | [football-data.org](https://www.football-data.org/) | gratuit (10 req/min, saison actuelle) |

### 4. Lancement

```bash
python3 bot.py
```

Tu devrais voir :

```
2026-05-14 ... | INFO    | __main__ | 🚀 Bot thématique démarré ! (Ctrl+C pour arrêter)
```

Ouvre Telegram, cherche ton bot et tape `/start`.

---

## 📁 Structure du projet

```
bot-telegram/
├── bot.py                      # Point d'entrée, classe BotThematique
├── config.py                   # Configuration centralisée (.env, validation)
├── requirements.txt
├── .env                        # (à créer, ignoré par git)
│
├── handlers/                   # Gestionnaires de messages Telegram
│   ├── menu.py                 # Menu principal, /start, /help
│   ├── meteo.py                # Météo
│   ├── actualites.py           # Actualités
│   ├── itineraire.py           # Itinéraire
│   ├── currency.py             # Convertisseur de devises
│   ├── football.py             # Football (multi-API)
│   ├── chat.py                 # Chat libre IA
│   └── actions.py              # Actions transverses (suivi météo / actu)
│
├── services/                   # Wrappers des API externes
│   ├── __init__.py             # Singletons partagés
│   ├── deepseek_service.py
│   ├── meteo_service.py
│   ├── news_service.py
│   ├── currency_service.py
│   ├── football_service.py     # API-Football
│   └── football_data_service.py # football-data.org
│
└── utils/
    ├── session_manager.py      # Sessions utilisateur + état machine
    ├── keyboards.py            # Claviers Telegram
    ├── constants.py            # Labels UI partagés
    └── logger.py               # Configuration logging
```

### Conventions

- **Services** : un service par API, instancié en singleton dans `services/__init__.py`, cache mémoire interne quand pertinent.
- **Handlers** : un handler par feature, enregistrés via `register_xxx_handlers(bot)` depuis `bot.py`.
- **État utilisateur** : `SessionMode` enum + `session_manager` pour gérer les conversations multi-étapes (ex: saisie ville → affichage météo).
- **Logging** : `from utils.logger import get_logger` ; niveau pilotable via `LOG_LEVEL`.

---

## 🛠️ Choix techniques

- **`pyTelegramBotAPI`** (telebot) plutôt que `python-telegram-bot` — API plus simple et synchrone, suffisante pour ce besoin.
- **Cache mémoire** plutôt que Redis — le bot tourne en single-instance, le cache se reconstruit au redémarrage.
- **Pas de base de données** — les sessions sont en mémoire ; un redémarrage du bot réinitialise toutes les sessions actives (acceptable pour un bot perso).
- **Markdown classique** comme `parse_mode` Telegram — compromis entre lisibilité et facilité d'écriture.

---

## 🎛️ Variables d'environnement

| Variable | Obligatoire | Défaut | Description |
|---|---|---|---|
| `TELEGRAM_TOKEN` | ✅ | — | Token Telegram du bot |
| `DEEPSEEK_API_KEY` | ✅ | — | Clé API DeepSeek |
| `OPENWEATHER_API_KEY` | ✅ | — | Clé OpenWeather |
| `EXCHANGE_RATE_API_KEY` | ✅ | — | Clé ExchangeRate-API |
| `NEWS_API_KEY` | ❌ | — | Clé NewsAPI (sinon résumés IA seuls) |
| `FOOTBALL_API_KEY` | ❌ | — | Clé API-Football |
| `FOOTBALL_DATA_API_KEY` | ❌ | — | Clé football-data.org |
| `MAX_HISTORY_LENGTH` | ❌ | `20` | Taille max de l'historique chat libre |
| `DEFAULT_TEMPERATURE` | ❌ | `0.7` | Température DeepSeek par défaut |
| `MAX_TOKENS` | ❌ | `1000` | Tokens max DeepSeek par réponse |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `FOOTBALL_MAX_SEASON` | ❌ | `2024` | Saison max accessible sur le plan API-Football |

Au démarrage, `Config.validate()` vérifie la présence des clés obligatoires et émet un warning pour les optionnelles manquantes.

---

## 🐛 Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `ValueError: Clés API manquantes` | Une clé obligatoire est absente de `.env` | Compléter le `.env` |
| Bot ne répond pas | Token Telegram invalide ou bot non démarré sur Telegram | Vérifier le token chez BotFather, taper `/start` |
| `API-Football erreurs: 'plan'` | Saison demandée hors plan gratuit (2022-2024) | Ajuster `FOOTBALL_MAX_SEASON` ou changer de saison dans le bot |
| `football-data : rate limit dépassé` | Plus de 10 req/min sur football-data.org | Attendre ; le cache de 5 min absorbe la plupart des appels |
| Émojis cassés / Markdown qui n'affiche pas le gras | Un caractère réservé Markdown non échappé | Voir les helpers `_md_safe()` dans les handlers |

---

## 📦 Dépendances principales

- [`pyTelegramBotAPI`](https://github.com/eternnoir/pyTelegramBotAPI) — client Telegram
- [`openai`](https://github.com/openai/openai-python) — SDK utilisé pour DeepSeek (compatible OpenAI)
- [`requests`](https://requests.readthedocs.io/) — appels HTTP
- [`python-dotenv`](https://github.com/theskumar/python-dotenv) — chargement du `.env`

Liste complète dans [`requirements.txt`](requirements.txt).

---

## 📄 Licence

Projet personnel — usage libre.
