import os
import random
import time
import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from aiogram import Bot

TOKEN = "8628464354:AAEQ0XKfv9OR-CR368dSaXq6tQsipn_Wy7w"
DOMAIN = "bot-1790034365-8732-prokudin95.bothost.tech"

bot = Bot(token=TOKEN)
app = FastAPI()

DB_FILE = "database.db"

POKEMON_DATA = {
    "Charmander": {"id": 4, "next": "Charmeleon", "evo_lvl": 3, "type": "Fire"},
    "Charmeleon": {"id": 5, "next": "Charizard", "evo_lvl": 6, "type": "Fire"},
    "Charizard": {"id": 6, "next": None, "evo_lvl": 99, "type": "Fire"},
    "Cyndaquil": {"id": 155, "next": "Quilava", "evo_lvl": 3, "type": "Fire"},
    "Quilava": {"id": 156, "next": "Typhlosion", "evo_lvl": 6, "type": "Fire"},
    "Typhlosion": {"id": 157, "next": None, "evo_lvl": 99, "type": "Fire"},
    "Torchic": {"id": 255, "next": "Combusken", "evo_lvl": 3, "type": "Fire"},
    "Combusken": {"id": 256, "next": "Blaziken", "evo_lvl": 6, "type": "Fire"},
    "Blaziken": {"id": 257, "next": None, "evo_lvl": 99, "type": "Fire"},

    "Squirtle": {"id": 7, "next": "Wartortle", "evo_lvl": 3, "type": "Water"},
    "Wartortle": {"id": 8, "next": "Blastoise", "evo_lvl": 6, "type": "Water"},
    "Blastoise": {"id": 9, "next": None, "evo_lvl": 99, "type": "Water"},
    "Totodile": {"id": 158, "next": "Croconaw", "evo_lvl": 3, "type": "Water"},
    "Croconaw": {"id": 159, "next": "Feraligatr", "evo_lvl": 6, "type": "Water"},
    "Feraligatr": {"id": 160, "next": None, "evo_lvl": 99, "type": "Water"},
    "Mudkip": {"id": 258, "next": "Marshtomp", "evo_lvl": 3, "type": "Water"},
    "Marshtomp": {"id": 259, "next": "Swampert", "evo_lvl": 6, "type": "Water"},
    "Swampert": {"id": 260, "next": None, "evo_lvl": 99, "type": "Water"},
    "Lugia": {"id": 249, "next": None, "evo_lvl": 99, "type": "Water"},

    "Bulbasaur": {"id": 1, "next": "Ivysaur", "evo_lvl": 3, "type": "Grass"},
    "Ivysaur": {"id": 2, "next": "Venusaur", "evo_lvl": 6, "type": "Grass"},
    "Venusaur": {"id": 3, "next": None, "evo_lvl": 99, "type": "Grass"},
    "Chikorita": {"id": 152, "next": "Bayleef", "evo_lvl": 3, "type": "Grass"},
    "Bayleef": {"id": 153, "next": "Meganium", "evo_lvl": 6, "type": "Grass"},
    "Meganium": {"id": 154, "next": None, "evo_lvl": 99, "type": "Grass"},
    "Treecko": {"id": 252, "next": "Grovyle", "evo_lvl": 3, "type": "Grass"},
    "Grovyle": {"id": 253, "next": "Sceptile", "evo_lvl": 6, "type": "Grass"},
    "Sceptile": {"id": 254, "next": None, "evo_lvl": 99, "type": "Grass"},

    "Pikachu": {"id": 25, "next": "Raichu", "evo_lvl": 5, "type": "Electric"},
    "Raichu": {"id": 26, "next": None, "evo_lvl": 99, "type": "Electric"},
    "Mareep": {"id": 179, "next": "Flaaffy", "evo_lvl": 4, "type": "Electric"},
    "Flaaffy": {"id": 180, "next": "Ampharos", "evo_lvl": 7, "type": "Electric"},
    "Ampharos": {"id": 181, "next": None, "evo_lvl": 99, "type": "Electric"},

    "Pidgey": {"id": 16, "next": None, "evo_lvl": 99, "type": "Normal"},
    "Zubat": {"id": 41, "next": None, "evo_lvl": 99, "type": "Poison"},
    "Diglett": {"id": 50, "next": None, "evo_lvl": 99, "type": "Ground"},
    "Geodude": {"id": 74, "next": None, "evo_lvl": 99, "type": "Rock"},
    "Mewtwo": {"id": 150, "next": None, "evo_lvl": 99, "type": "Psychic"},
    "Rattata": {"id": 19, "next": None, "evo_lvl": 99, "type": "Normal"},
    "Snorlax": {"id": 143, "next": None, "evo_lvl": 99, "type": "Normal"},
    "Gengar": {"id": 94, "next": None, "evo_lvl": 99, "type": "Ghost"},
    "Togepi": {"id": 175, "next": "Togetic", "evo_lvl": 5, "type": "Fairy"},
    "Togetic": {"id": 176, "next": None, "evo_lvl": 99, "type": "Fairy"},
    "Tyranitar": {"id": 248, "next": None, "evo_lvl": 99, "type": "Rock"},
    "Ralts": {"id": 280, "next": "Kirlia", "evo_lvl": 4, "type": "Psychic"},
    "Kirlia": {"id": 281, "next": "Gardevoir", "evo_lvl": 8, "type": "Psychic"},
    "Gardevoir": {"id": 282, "next": None, "evo_lvl": 99, "type": "Psychic"},
    "Rayquaza": {"id": 384, "next": None, "evo_lvl": 99, "type": "Dragon"}
}

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                starter TEXT,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                pokeballs INTEGER DEFAULT 5,
                masterballs INTEGER DEFAULT 1,
                potions INTEGER DEFAULT 2,
                coins INTEGER DEFAULT 150,
                stars INTEGER DEFAULT 10,
                rating INTEGER DEFAULT 1000,
                last_daily INTEGER DEFAULT 0,
                referred_by INTEGER DEFAULT 0,
                clan_name TEXT DEFAULT 'Без клана'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS collection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pokemon_name TEXT,
                rarity TEXT,
                is_shiny INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                hp INTEGER DEFAULT 50
            )
        """)
        await db.commit()

@app.on_event("startup")
async def startup_event():
    await init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pokémon World - MMORPG</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #090d16; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card-glow { box-shadow: 0 0 25px rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.25); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .shiny-card { background: linear-gradient(135deg, #311042 0%, #1e1b4b 100%); border: 1px solid #c084fc; }
        .pixel-art { image-rendering: pixelated; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-4 max-w-md mx-auto">

    <header class="flex justify-between items-center bg-slate-800/90 p-3 rounded-2xl card-glow mb-3 text-xs">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-indigo-600/30 rounded-full flex items-center justify-center font-bold text-indigo-300">⚡</div>
            <div>
                <h1 class="font-bold text-indigo-400 text-sm" id="tg-username">Тренер</h1>
                <span class="text-[10px] text-slate-400">Клан: <strong class="text-indigo-300">{{ user[15] if user else 'Без клана' }}</strong></span>
            </div>
        </div>
        <div class="flex items-center gap-1.5">
            <span class="bg-amber-500/20 text-amber-300 px-2 py-1 rounded-lg border border-amber-500/30 font-bold">🪙 {{ user[10] if user else 0 }}</span>
            <span class="bg-purple-500/20 text-purple-300 px-2 py-1 rounded-lg border border-purple-500/30 font-bold">⭐ {{ user[11] if user else 0 }}</span>
        </div>
    </header>

    <main class="my-auto">
        {% if not user %}
            <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                <h2 class="text-lg font-black text-yellow-400">Путь Тренера</h2>
                <p class="text-xs text-slate-300">Выберите стартового Pokémon:</p>
                
                <form action="/register" method="GET" class="space-y-3">
                    <input type="hidden" name="user_id" id="input_user_id" value="">
                    <input type="hidden" name="username" id="input_username" value="Trainer">

                    <div class="grid grid-cols-3 gap-2">
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Bulbasaur" class="peer hidden" checked>
                            <div class="p-2 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-emerald-500 peer-checked:bg-emerald-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png" class="w-14 h-14 mx-auto pixel-art">
                                <div class="text-[10px] font-bold text-emerald-400 mt-1">🌱 Бульбазавр</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Charmander" class="peer hidden">
                            <div class="p-2 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-orange-500 peer-checked:bg-orange-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png" class="w-14 h-14 mx-auto pixel-art">
                                <div class="text-[10px] font-bold text-orange-400 mt-1">🔥 Чармандер</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Squirtle" class="peer hidden">
                            <div class="p-2 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-blue-500 peer-checked:bg-blue-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png" class="w-14 h-14 mx-auto pixel-art">
                                <div class="text-[10px] font-bold text-blue-400 mt-1">💧 Сквиртл</div>
                            </div>
                        </label>
                    </div>

                    <button type="submit" class="w-full py-2.5 bg-gradient-to-r from-indigo-500 to-violet-600 font-bold rounded-xl text-xs shadow-lg text-white">
                        Начать приключение! 🚀
                    </button>
                </form>
            </div>
        {% else %}
            <!-- Вкладка 1: Профиль -->
            <div id="tab-profile" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-4 rounded-3xl card-glow text-center space-y-3">
                    <div class="inline-block p-2 bg-indigo-500/10 rounded-2xl border border-indigo-500/30">
                        <img id="starter-img" src="" class="w-20 h-20 mx-auto pixel-art">
                    </div>
                    <h2 class="text-sm font-bold text-indigo-200">Боевой покемон: <span class="text-yellow-400">{{ user[2] }}</span> (Ур. {{ user[3] }})</h2>
                    
                    <div class="bg-slate-900/60 p-2.5 rounded-2xl space-y-2 text-left text-xs">
                        <div class="flex justify-between text-[11px]">
                            <span class="text-slate-400">Здоровье (HP):</span>
                            <span class="font-bold text-rose-400">{{ user[5] }}/{{ user[6] }} HP</span>
                        </div>
                        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div class="bg-rose-500 h-full transition-all duration-500" style="width: {{ (user[5] / user[6]) * 100 }}%;"></div>
                        </div>
                    </div>

                    {% if message %}
                    <div class="p-2 bg-indigo-950/60 border border-indigo-500/40 rounded-xl text-xs">
                        <p class="font-bold text-yellow-300">{{ message }}</p>
                    </div>
                    {% endif %}

                    <div class="bg-indigo-950/50 p-3 rounded-2xl border border-indigo-500/40 text-xs text-left space-y-2">
                        <span class="font-bold text-indigo-300 block">🛡️ Ваш клан: <strong class="text-yellow-400">{{ user[15] }}</strong></span>
                        {% if user[15] == 'Без клана' %}
                        <div class="grid grid-cols-3 gap-1">
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Rocket&tab=profile" class="py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold text-[10px] text-center">Rocket</a>
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Mystic&tab=profile" class="py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold text-[10px] text-center">Mystic</a>
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Valor&tab=profile" class="py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-bold text-[10px] text-center">Valor</a>
                        </div>
                        {% else %}
                        <p class="text-[10px] text-slate-400">Клан зафиксирован навсегда!</p>
                        {% endif %}
                        
                        <div class="pt-2 border-t border-indigo-900">
                            <span class="font-bold text-slate-300 block mb-1">👑 Рейтинг кланов:</span>
                            <div class="space-y-1 text-[11px]">
                                {% for clan in clan_stats %}
                                <div class="flex justify-between bg-slate-900/60 px-2 py-1 rounded">
                                    <span class="text-indigo-200">🛡️ {{ clan[0] }}</span>
                                    <span class="text-yellow-400 font-bold">🏆 {{ clan[1] }} кубков</span>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Вкладка 2: Карта мира -->
            <div id="tab-map" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-indigo-300">🗺️ Карта Мира (Эндгейм)</h2>
                    {% if map_msg %}<p class="text-xs text-yellow-300 font-bold">{{ map_msg }}</p>{% endif %}
                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <div>
                                <span class="font-bold text-emerald-400 block">🌲 Лесная зона</span>
                                <span class="text-[10px] text-slate-400">Поиск обычных и редких покемонов</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=forest&tab=map" class="px-3 py-1.5 bg-emerald-600/30 border border-emerald-500 text-emerald-300 rounded-lg font-bold">Идти (-1 🔴)</a>
                        </div>
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <div>
                                <span class="font-bold text-amber-400 block">⛰️ Пещеры & Водоемы</span>
                                <span class="text-[10px] text-slate-400">Легендарные покемоны & Shiny шанс</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=cave&tab=map" class="px-3 py-1.5 bg-amber-600/30 border border-amber-500 text-amber-300 rounded-lg font-bold">Идти (-1 🔴)</a>
                        </div>
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-purple-500/50">
                            <div>
                                <span class="font-bold text-purple-300 block">✨ Ультра-Портал</span>
                                <span class="text-[10px] text-slate-400">Высокий шанс Shiny (Стоит 2 🔴)</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=portal&tab=map" class="px-3 py-1.5 bg-purple-600/30 border border-purple-500 text-purple-300 rounded-lg font-bold">Портал</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Вкладка 3: Коллекция -->
            <div id="tab-collection" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-yellow-400">📖 Pokédex: Собрано уникальных: {{ pokedex_count }}/38</h2>
                    
                    <h2 class="text-sm font-bold text-indigo-300 pt-1">🏆 Зал Славы (Топ Тренеров)</h2>
                    <div class="bg-slate-900/60 p-2.5 rounded-xl border border-slate-700 space-y-1 text-xs text-left max-h-24 overflow-y-auto">
                        {% for top in leaderboard %}
                        <div class="flex justify-between items-center border-b border-slate-800 pb-1">
                            <span class="font-bold text-indigo-300">{{ loop.index }}. @{{ top[1] or 'Тренер' }}</span>
                            <span class="text-yellow-400 font-bold">🏆 {{ top[2] }} кубков</span>
                        </div>
                        {% endfor %}
                    </div>

                    <h2 class="text-sm font-bold text-indigo-300 pt-1">📦 Моя Коллекция (Выбери бойца)</h2>
                    <div class="grid grid-cols-2 gap-2 text-left max-h-32 overflow-y-auto pr-1">
                        {% for p in collection %}
                        <div class="p-2 rounded-xl text-xs flex items-center justify-between {% if p[4] == 1 %}shiny-card{% else %}bg-slate-900/60 border border-slate-700{% endif %}">
                            <div class="flex items-center gap-2">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{{ p[6] }}.png" class="w-8 h-8 pixel-art">
                                <div>
                                    <span class="font-bold {% if p[4] == 1 %}text-purple-300{% else %}text-emerald-400{% endif %} block">{% if p[4] == 1 %}✨ {% endif %}{{ p[2] }}</span>
                                    <span class="text-[10px] text-slate-400">Ур. {{ p[5] }}</span>
                                </div>
                            </div>
                            <div class="flex flex-col gap-1">
                                <a href="/set_active?user_id={{ user[0] }}&poke_id={{ p[0] }}&tab=collection" class="px-1.5 py-0.5 bg-emerald-600/60 text-white rounded text-[9px] font-bold text-center">В бой!</a>
                                <a href="/sell?user_id={{ user[0] }}&poke_id={{ p[0] }}&tab=collection" class="px-1.5 py-0.5 bg-rose-600/40 text-rose-200 rounded text-[9px] font-bold text-center">Продать</a>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Вкладка 4: Арены -->
            <div id="tab-battle" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <h2 class="text-sm font-bold text-rose-400">⚔️ Тактические Арены</h2>
                    
                    {% if battle_msg %}
                    <div class="p-3 bg-rose-950/60 border border-rose-500/40 rounded-xl text-center text-xs">
                        <p class="font-bold text-yellow-300">{{ battle_msg }}</p>
                    </div>
                    {% endif %}

                    <div class="grid grid-cols-2 gap-2 text-xs">
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 space-y-2">
                            <span class="font-bold text-rose-400 block">🌲 PvE Бой</span>
                            <p class="text-[10px] text-slate-400">Качай активного покемона</p>
                            <a href="/battle?user_id={{ user[0] }}&tab=battle" class="block w-full py-1.5 bg-rose-600 hover:bg-rose-700 font-bold rounded-lg text-white">В бой!</a>
                        </div>
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-indigo-500/50 space-y-2">
                            <span class="font-bold text-indigo-400 block">🏆 PvP (Игроки)</span>
                            <p class="text-[10px] text-slate-400">Бой с реальным соперником</p>
                            <a href="/pvp_live?user_id={{ user[0] }}&tab=battle" class="block w-full py-1.5 bg-indigo-600 hover:bg-indigo-700 font-bold rounded-lg text-white">Найти бой!</a>
                        </div>
                    </div>

                    <div class="bg-amber-950/40 p-3 rounded-xl border border-amber-500/40 text-xs text-left flex justify-between items-center">
                        <div>
                            <span class="font-bold text-amber-400 block">👑 Легендарный Босс</span>
                            <span class="text-[10px] text-slate-400">Награда: +100 XP и +100 🪙</span>
                        </div>
                        <a href="/boss?user_id={{ user[0] }}&tab=battle" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg">Вызов</a>
                    </div>
                </div>
            </div>

            <!-- Вкладка 5: Магазин -->
            <div id="tab-shop" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-xs">
                    <h2 class="text-sm font-bold text-amber-400 text-center">🛒 Магазин Лиги</h2>
                    
                    <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-200 block">🔴 Poké Ball</span>
                            <span class="text-[10px] text-slate-400">В наличии: {{ user[7] }} шт.</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=pokeball&tab=shop" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 font-bold rounded-lg text-white">50 🪙</a>
                    </div>
                </div>
            </div>
        {% endif %}
    </main>

    {% if user %}
    <nav class="grid grid-cols-5 gap-1 bg-slate-800/90 p-2 rounded-2xl card-glow text-center text-xs mt-3">
        <button onclick="switchTab('profile', this)" class="tab-btn p-2 bg-indigo-600/30 text-indigo-300 rounded-xl font-bold">👤</button>
        <button onclick="switchTab('map', this)" class="tab-btn p-2 text-slate-400 hover:text-white">🗺️</button>
        <button onclick="switchTab('collection', this)" class="tab-btn p-2 text-slate-400 hover:text-white">📦</button>
        <button onclick="switchTab('battle', this)" class="tab-btn p-2 text-slate-400 hover:text-white">⚔️</button>
        <button onclick="switchTab('shop', this)" class="tab-btn p-2 text-slate-400 hover:text-white">🛒</button>
    </nav>
    {% endif %}

    <script>
        const urlParams = new URLSearchParams(window.location.search);
        let tgUserId = null;
        let tgUserName = "Тренер";

        try {
            if (window.Telegram && window.Telegram.WebApp) {
                const tg = window.Telegram.WebApp;
                tg.expand();
                if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                    tgUserId = tg.initDataUnsafe.user.id;
                    tgUserName = tg.initDataUnsafe.user.first_name || "Тренер";
                    const nameEl = document.getElementById('tg-username');
                    if (nameEl) nameEl.innerText = tgUserName;
                }
            }
        } catch (e) {}

        // Если в URL нет user_id, но Telegram передал реальный ID — перенаправляем
        if (!urlParams.has('user_id')) {
            if (tgUserId) {
                window.location.replace(`/?user_id=${tgUserId}`);
            } else {
                // Если открыли не в телеграме, даем тестовый ID, чтобы не было ошибки 404
                window.location.replace(`/?user_id=777888999`);
            }
        }

        const inputId = document.getElementById('input_user_id');
        const inputName = document.getElementById('input_username');
        if (inputId && tgUserId) inputId.value = tgUserId;
        else if (inputId) inputId.value = "777888999";
        
        if (inputName && tgUserName) inputName.value = tgUserName;

        const activeTab = urlParams.get('tab');
        if (activeTab) {
            const btnMap = { 'profile': 0, 'map': 1, 'collection': 2, 'battle': 3, 'shop': 4 };
            const buttons = document.querySelectorAll('.tab-btn');
            if (buttons[btnMap[activeTab]]) {
                switchTab(activeTab, buttons[btnMap[activeTab]]);
            }
        }

        const starterName = "{{ user[2] if user else '' }}";
        const POKEMON_IDS = {
            "Bulbasaur": 1, "Ivysaur": 2, "Venusaur": 3,
            "Charmander": 4, "Charmeleon": 5, "Charizard": 6,
            "Squirtle": 7, "Wartortle": 8, "Blastoise": 9,
            "Pikachu": 25, "Raichu": 26, "Pidgey": 16, "Zubat": 41,
            "Diglett": 50, "Geodude": 74, "Mewtwo": 150, "Rattata": 19,
            "Snorlax": 143, "Gengar": 94,
            "Chikorita": 152, "Bayleef": 153, "Meganium": 154,
            "Cyndaquil": 155, "Quilava": 156, "Typhlosion": 157,
            "Totodile": 158, "Croconaw": 159, "Feraligatr": 160,
            "Togepi": 175, "Togetic": 176, "Mareep": 179, "Flaaffy": 180, "Ampharos": 181,
            "Tyranitar": 248, "Lugia": 249,
            "Treecko": 252, "Grovyle": 253, "Sceptile": 254,
            "Torchic": 255, "Combusken": 256, "Blaziken": 257,
            "Mudkip": 258, "Marshtomp": 259, "Swampert": 260,
            "Ralts": 280, "Kirlia": 281, "Gardevoir": 282, "Rayquaza": 384
        };

        if (starterName && POKEMON_IDS[starterName]) {
            document.getElementById('starter-img').src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${POKEMON_IDS[starterName]}.png`;
        }

        function switchTab(tabName, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('bg-indigo-600/30', 'text-indigo-300', 'font-bold');
                b.classList.add('text-slate-400');
            });
            btn.classList.add('bg-indigo-600/30', 'text-indigo-300', 'font-bold');
            btn.classList.remove('text-slate-400');
        }
    </script>
</body>
</html>
"""

from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int = 12345, message: str = None, battle_msg: str = None, map_msg: str = None):
    async with aiosqlite.connect(DB_FILE) as db:
        user = None
        if user_id != 12345:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()
            
        collection = []
        pokedex_count = 0
        leaderboard = []
        clan_stats = []

        if user:
            async with db.execute("SELECT * FROM collection WHERE user_id = ?", (user_id,)) as cursor:
                raw_col = await cursor.fetchall()
                unique_pokes = set()
                for row in raw_col:
                    unique_pokes.add(row[2])
                    p_id = POKEMON_DATA.get(row[2], {}).get("id", 25)
                    collection.append(row + (p_id,))
                pokedex_count = len(unique_pokes)

            async with db.execute("SELECT user_id, username, rating FROM users ORDER BY rating DESC LIMIT 5") as cursor:
                leaderboard = await cursor.fetchall()

            async with db.execute("SELECT clan_name, SUM(rating) as total_rating FROM users GROUP BY clan_name ORDER BY total_rating DESC") as cursor:
                clan_stats = await cursor.fetchall()
            
    template = Template(HTML_TEMPLATE)
    return HTMLResponse(content=template.render(
        request=request, user=user, collection=collection, leaderboard=leaderboard, 
        pokedex_count=pokedex_count, clan_stats=clan_stats, message=message, 
        battle_msg=battle_msg, map_msg=map_msg
    ))

@app.get("/register")
async def register(user_id: int, username: str = "Тренер", starter: str = "Bulbasaur"):
    if not user_id or user_id == 12345:
        user_id = int(time.time())
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            exists = await cursor.fetchone()
        if not exists:
            await db.execute(
                "INSERT INTO users (user_id, username, starter, level, exp, hp, max_hp, pokeballs, coins, rating, clan_name) VALUES (?, ?, ?, 1, 0, 100, 100, 5, 150, 1000, 'Без клана')",
                (user_id, username, starter)
            )
            await db.execute(
                "INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, 'Обычный', 0, 1, 50)",
                (user_id, starter)
            )
            await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab=profile", status_code=303)

@app.get("/join_clan")
async def join_clan(user_id: int, clan: str, tab: str = "profile"):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT clan_name FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 'Без клана':
                await db.execute("UPDATE users SET clan_name = ? WHERE user_id = ?", (clan, user_id))
                await db.commit()
                msg = f"🛡️ Вы вступили в клан {clan}!"
            else:
                msg = "⚠️ Клан уже выбран!"
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message={msg}", status_code=303)

@app.get("/set_active")
async def set_active(user_id: int, poke_id: int, tab: str = "collection"):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokemon_name FROM collection WHERE id = ? AND user_id = ?", (poke_id, user_id)) as cursor:
            poke = await cursor.fetchone()
            if poke:
                await db.execute("UPDATE users SET starter = ? WHERE user_id = ?", (poke[0], user_id))
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message=⚡ Покемон изменен!", status_code=303)

@app.get("/explore")
async def explore(user_id: int, loc: str, tab: str = "map"):
    map_msg = ""
    cost = 2 if loc == "portal" else 1
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokeballs FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] >= cost:
                if loc == "forest":
                    pool = ["Pikachu", "Pidgey", "Bulbasaur", "Chikorita", "Snorlax"]
                elif loc == "cave":
                    pool = ["Mewtwo", "Rayquaza", "Lugia", "Tyranitar"]
                else:
                    pool = ["Mewtwo", "Rayquaza", "Lugia", "Gardevoir"]
                
                chosen = random.choice(pool)
                is_shiny = 1 if random.random() < (0.3 if loc == "portal" else 0.1) else 0
                await db.execute("UPDATE users SET pokeballs = pokeballs - ? WHERE user_id = ?", (cost, user_id))
                await db.execute("INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, 'Редкий', ?, 1, 50)", (user_id, chosen, is_shiny))
                await db.commit()
                map_msg = f"🎉 Пойман: {'✨ SHINY ' if is_shiny else ''}{chosen}!"
            else:
                map_msg = "❌ Недостаточно Poké Balls!"
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&map_msg={map_msg}", status_code=303)

@app.get("/pvp_live")
async def pvp_live(user_id: int, tab: str = "battle"):
    battle_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id, username, starter FROM users WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (user_id,)) as cursor:
            opponent = await cursor.fetchone()
        if not opponent:
            battle_msg = "👥 Нет соперников для PvP."
        else:
            opp_id, opp_name, opp_poke = opponent
            win = random.random() < 0.5
            if win:
                await db.execute("UPDATE users SET rating = rating + 25, coins = coins + 50 WHERE user_id = ?", (user_id,))
                battle_msg = f"🏆 Победа над @{opp_name or 'Тренер'}! (+25 🏆)"
            else:
                await db.execute("UPDATE users SET rating = MAX(0, rating - 15) WHERE user_id = ?", (user_id,))
                battle_msg = f"💥 Поражение от @{opp_name or 'Тренер'}! (-15 🏆)"
            await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}", status_code=303)

@app.get("/battle")
async def battle(user_id: int, tab: str = "battle"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET exp = exp + 35, coins = coins + 30 WHERE user_id = ?", (user_id,))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg=⚔️ Победа в PvE! (+35 XP)", status_code=303)

@app.get("/boss")
async def boss(user_id: int, tab: str = "battle"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET exp = exp + 100, coins = coins + 100, rating = rating + 50 WHERE user_id = ?", (user_id,))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg=👑 Победа над Боссом!", status_code=303)

@app.get("/buy")
async def buy(user_id: int, item: str, tab: str = "shop"):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] >= 50:
                await db.execute("UPDATE users SET coins = coins - 50, pokeballs = pokeballs + 1 WHERE user_id = ?", (user_id,))
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}", status_code=303)

@app.get("/sell")
async def sell(user_id: int, poke_id: int, tab: str = "collection"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM collection WHERE id = ?", (poke_id,))
        await db.execute("UPDATE users SET coins = coins + 40 WHERE user_id = ?", (user_id,))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message=💰 Продано за 40 🪙!", status_code=303)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
