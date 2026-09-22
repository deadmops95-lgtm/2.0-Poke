import os
import random
import time
import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

TYPE_ADVANTAGES = {
    "Fire": {"Grass": 1.5, "Water": 0.5, "Fire": 0.5},
    "Water": {"Fire": 1.5, "Grass": 0.5, "Water": 0.5},
    "Grass": {"Water": 1.5, "Fire": 0.5, "Grass": 0.5},
    "Electric": {"Water": 1.5, "Electric": 0.5, "Grass": 0.5},
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

    <!-- Верхняя панель -->
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

    <!-- Основной контент -->
    <main class="my-auto">
        {% if not user %}
            <!-- Регистрация -->
            <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                <h2 class="text-lg font-black text-yellow-400">Путь Тренера</h2>
                <p class="text-xs text-slate-300">Выберите стартового Pokémon:</p>
                
                <form action="/register" method="GET" class="space-y-3">
                    <input type="hidden" name="user_id" id="input_user_id" value="12345">
                    <input type="hidden" name="username" id="input_username" value="Trainer">
                    <input type="hidden" name="ref" id="input_ref" value="0">

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
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Cyndaquil" class="peer hidden">
                            <div class="p-2 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-amber-500 peer-checked:bg-amber-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/155.png" class="w-14 h-14 mx-auto pixel-art">
                                <div class="text-[10px] font-bold text-amber-400 mt-1">🔥 Синдаквил</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Treecko" class="peer hidden">
                            <div class="p-2 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-teal-500 peer-checked:bg-teal-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/252.png" class="w-14 h-14 mx-auto pixel-art">
                                <div class="text-[10px] font-bold text-teal-400 mt-1">🌱 Трико</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Torchic" class="peer hidden">
                            <div class="p-2 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-rose-500 peer-checked:bg-rose-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/255.png" class="w-14 h-14 mx-auto pixel-art">
                                <div class="text-[10px] font-bold text-rose-400 mt-1">🔥 Торчик</div>
                            </div>
                        </label>
                    </div>

                    <button type="submit" class="w-full py-2.5 bg-gradient-to-r from-indigo-500 to-violet-600 font-bold rounded-xl text-xs shadow-lg text-white">
                        Начать приключение! 🚀
                    </button>
                </form>
            </div>
        {% else %}
            <!-- Вкладка 1: Профиль и Боевой покемон -->
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
                        <div class="flex justify-between text-[11px] pt-1">
                            <span class="text-slate-400">Опыт до след. уровня:</span>
                            <span class="font-bold text-emerald-400">{{ user[4] }}/100 XP</span>
                        </div>
                        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div class="bg-emerald-500 h-full transition-all duration-500" style="width: {{ user[4] }}%;"></div>
                        </div>
                    </div>

                    <div class="bg-indigo-950/50 p-2.5 rounded-xl border border-indigo-500/40 text-xs text-left space-y-2">
                        <span class="font-bold text-indigo-300 block">🛡️ Клан: {{ user[15] }}</span>
                        <div class="flex gap-1">
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Rocket&tab=profile" class="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold text-[10px]">Rocket</a>
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Mystic&tab=profile" class="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-bold text-[10px]">Mystic</a>
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Valor&tab=profile" class="px-2 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded font-bold text-[10px]">Valor</a>
                        </div>
                    </div>

                    <div class="bg-slate-900/60 p-2.5 rounded-xl border border-slate-700 text-xs text-left space-y-1">
                        <span class="font-bold text-indigo-400 block">💬 Разработчик</span>
                        <a href="https://t.me/Prokudin95" target="_blank" class="block w-full py-1.5 bg-indigo-600/40 hover:bg-indigo-600/60 border border-indigo-500 text-indigo-200 text-center rounded-lg font-bold">Написать @Prokudin95 ✉️</a>
                    </div>
                </div>
            </div>

            <!-- Вкладка 2: Карта мира -->
            <div id="tab-map" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3">
                    <h2 class="text-sm font-bold text-indigo-300 text-center">🗺️ Карта Мира</h2>
                    
                    {% if message %}
                    <div class="p-3 bg-indigo-950/60 border border-indigo-500/40 rounded-xl text-center text-xs">
                        <p class="font-bold text-yellow-300">{{ message }}</p>
                    </div>
                    {% endif %}

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

            <!-- Вкладка 3: Pokédex и Коллекция -->
            <div id="tab-collection" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-yellow-400">📖 Pokédex: Собрано: {{ pokedex_count }}/38</h2>
                    
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
                    <div class="p-3 bg-rose-950/60 border border-rose-500/40 rounded-xl text-center text-xs space-y-1">
                        <p class="font-bold text-rose-300">{{ battle_msg }}</p>
                        {% if evo_msg %}
                        <p class="font-bold text-yellow-300 animate-bounce">{{ evo_msg }}</p>
                        {% endif %}
                    </div>
                    {% endif %}

                    <div class="grid grid-cols-2 gap-2 text-xs">
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 space-y-2">
                            <span class="font-bold text-rose-400 block">🌲 PvE Бой</span>
                            <p class="text-[10px] text-slate-400">Качай активного покемона</p>
                            <a href="/battle?user_id={{ user[0] }}&tab=battle" class="block w-full py-1.5 bg-rose-600 hover:bg-rose-700 font-bold rounded-lg text-white">В бой!</a>
                        </div>
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-indigo-500/50 space-y-2">
                            <span class="font-bold text-indigo-400 block">🏆 PvP Арена</span>
                            <p class="text-[10px] text-slate-400">Рейтинговые бои тренеров</p>
                            <a href="/pvp?user_id={{ user[0] }}&tab=battle" class="block w-full py-1.5 bg-indigo-600 hover:bg-indigo-700 font-bold rounded-lg text-white">Рейтинг!</a>
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

                    <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-rose-300 block">🧪 Зелье лечения</span>
                            <span class="text-[10px] text-slate-400">В наличии: {{ user[9] }} шт.</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=potion&tab=shop" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 font-bold rounded-lg text-white">30 🪙</a>
                    </div>

                    <div class="bg-purple-950/40 p-3 rounded-xl border border-purple-500/50 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-purple-300 block">⭐ Мастер-Болл</span>
                            <span class="text-[10px] text-purple-200">100% поимка редкого покемона</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=masterball&tab=shop" class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 font-bold rounded-lg text-white">5 ⭐</a>
                    </div>

                    <!-- Админ-панель -->
                    <div class="bg-slate-900/80 p-3 rounded-xl border border-indigo-500/50 space-y-2 text-left mt-4">
                        <span class="font-bold text-indigo-400 block">🛠️ Админ-Панель выдачи</span>
                        <form action="/admin_give" method="GET" class="space-y-2">
                            <input type="hidden" name="admin_id" value="{{ user[0] }}">
                            <input type="hidden" name="tab" value="shop">
                            <div>
                                <label class="text-[10px] text-slate-400">ID игрока:</label>
                                <input type="number" name="target_id" placeholder="ID игрока" class="w-full bg-slate-800 p-1.5 rounded text-xs text-white border border-slate-700" required>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="text-[10px] text-slate-400">Монеты 🪙:</label>
                                    <input type="number" name="add_coins" value="100" class="w-full bg-slate-800 p-1.5 rounded text-xs text-white border border-slate-700">
                                </div>
                                <div>
                                    <label class="text-[10px] text-slate-400">Покеболы 🔴:</label>
                                    <input type="number" name="add_balls" value="5" class="w-full bg-slate-800 p-1.5 rounded text-xs text-white border border-slate-700">
                                </div>
                            </div>
                            <button type="submit" class="w-full py-1.5 bg-indigo-600 hover:bg-indigo-700 font-bold rounded-lg text-white">Выдать ресурсы</button>
                        </form>
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
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        let userId = 12345;
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            const u = tg.initDataUnsafe.user;
            userId = u.id;
            document.getElementById('tg-username').innerText = u.first_name;
        }

        const urlParams = new URLSearchParams(window.location.search);
        const refParam = urlParams.get('ref');
        if (refParam && document.getElementById('input_ref')) {
            document.getElementById('input_ref').value = refParam;
        }

        // Если открыли с телефона без параметра user_id, подставляем ID из Telegram WebApp автоматически
        if (!urlParams.has('user_id') && userId !== 12345) {
            window.location.href = `/?user_id=${userId}` + (refParam ? `&ref=${refParam}` : '');
        }

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
            const spriteUrl = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${POKEMON_IDS[starterName]}.png`;
            const sImg = document.getElementById('starter-img');
            if(sImg) sImg.src = spriteUrl;
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
async def index(request: Request, user_id: int = 12345, message: str = None, battle_msg: str = None, evo_msg: str = None, trade_msg: str = None):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
        collection = []
        leaderboard = []
        pokedex_count = 0
        can_claim = False

        if user:
            current_time = time.time()
            last_daily = user[13]
            if current_time - last_daily >= 86400:
                can_claim = True

            async with db.execute("SELECT * FROM collection WHERE user_id = ?", (user_id,)) as cursor:
                raw_col = await cursor.fetchall()
                unique_pokes = set()
                for row in raw_col:
                    p_name = row[2]
                    unique_pokes.add(p_name)
                    p_id = POKEMON_DATA.get(p_name, {}).get("id", 25)
                    collection.append(row + (p_id,))
                pokedex_count = len(unique_pokes)

            async with db.execute("SELECT user_id, username, rating FROM users ORDER BY rating DESC LIMIT 5") as cursor:
                leaderboard = await cursor.fetchall()
            
    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(
        request=request, user=user, collection=collection, leaderboard=leaderboard,
        pokedex_count=pokedex_count, message=message, battle_msg=battle_msg, 
        evo_msg=evo_msg, trade_msg=trade_msg, can_claim=can_claim
    )
    return HTMLResponse(content=rendered_html)

@app.get("/register")
async def register(user_id: int, username: str = "Тренер", starter: str = "Bulbasaur", ref: int = 0):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            exists = await cursor.fetchone()

        if not exists:
            initial_pokeballs = 5
            if ref and ref != user_id:
                initial_pokeballs += 3
                await db.execute("UPDATE users SET pokeballs = pokeballs + 3, coins = coins + 50 WHERE user_id = ?", (ref,))

            await db.execute(
                "INSERT INTO users (user_id, username, starter, level, exp, hp, max_hp, pokeballs, masterballs, potions, coins, stars, rating, last_daily, referred_by, clan_name) VALUES (?, ?, ?, 1, 0, 100, 100, ?, 1, 2, 150, 10, 1000, 0, ?, 'Без клана')",
                (user_id, username, starter, initial_pokeballs, ref)
            )
            await db.commit()

    return RedirectResponse(url=f"/?user_id={user_id}&tab=profile", status_code=303)

@app.get("/set_active")
async def set_active(user_id: int, poke_id: int, tab: str = "collection"):
    msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokemon_name FROM collection WHERE id = ? AND user_id = ?", (poke_id, user_id)) as cursor:
            poke = await cursor.fetchone()
            if poke:
                p_name = poke[0]
                await db.execute("UPDATE users SET starter = ? WHERE user_id = ?", (p_name, user_id))
                await db.commit()
                msg = f"⚡ Боевой покемон успешно изменен на {p_name}!"
            else:
                msg = "Ошибка: покемон не найден."
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message={msg}", status_code=303)

@app.get("/admin_give")
async def admin_give(admin_id: int, target_id: int, add_coins: int = 100, add_balls: int = 5, tab: str = "shop"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET coins = coins + ?, pokeballs = pokeballs + ? WHERE user_id = ?", (add_coins, add_balls, target_id))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={admin_id}&tab={tab}&message=🛠️ Успешно выдано игроку {target_id}: +{add_coins} 🪙, +{add_balls} 🔴!", status_code=303)

@app.get("/sell")
async def sell(user_id: int, poke_id: int, tab: str = "collection"):
    msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokemon_name FROM collection WHERE id = ? AND user_id = ?", (poke_id, user_id)) as cursor:
            poke = await cursor.fetchone()
            if poke:
                await db.execute("DELETE FROM collection WHERE id = ?", (poke_id,))
                await db.execute("UPDATE users SET coins = coins + 40 WHERE user_id = ?", (user_id,))
                await db.commit()
                msg = f"💰 Покемон успешно продан за 40 🪙!"
            else:
                msg = "Ошибка: покемон не найден."
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&trade_msg={msg}", status_code=303)

@app.get("/join_clan")
async def join_clan(user_id: int, clan: str, tab: str = "profile"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET clan_name = ? WHERE user_id = ?", (clan, user_id))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message=🛡️ Клан изменен на {clan}!", status_code=303)

@app.get("/daily")
async def daily(user_id: int, tab: str = "profile"):
    current_time = time.time()
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and (current_time - row[0] >= 86400):
                await db.execute("UPDATE users SET pokeballs = pokeballs + 2, coins = coins + 50, last_daily = ? WHERE user_id = ?", (current_time, user_id))
                await db.commit()
                msg = "🎁 Ежедневный бонус получен: +2 Poké Balls и +50 🪙!"
            else:
                msg = "⚠️ Награда уже получена! Приходите через 24 часа."
                
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message={msg}", status_code=303)

@app.get("/heal")
async def heal(user_id: int, tab: str = "profile"):
    msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT hp, max_hp, potions FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            if user:
                hp, max_hp, potions = user[0], user[1], user[2]
                if potions > 0 and hp < max_hp:
                    new_hp = min(max_hp, hp + 50)
                    await db.execute("UPDATE users SET hp = ?, potions = potions - 1 WHERE user_id = ?", (new_hp, user_id))
                    await db.commit()
                    msg = "🧪 Зелье использовано! Здоровье восстановлено."
                elif hp >= max_hp:
                    msg = "⚠️ У покемона полный запас здоровья!"
                else:
                    msg = "❌ У вас закончились лечебные зелья!"
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message={msg}", status_code=303)

@app.get("/explore")
async def explore(user_id: int, loc: str, tab: str = "map"):
    msg = "Вы ничего не нашли..."
    cost = 2 if loc == "portal" else 1
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokeballs FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] >= cost:
                if loc == "forest":
                    pool = [
                        ("Pikachu", "Редкий"), ("Pidgey", "Обычный"), ("Bulbasaur", "Обычный"),
                        ("Chikorita", "Обычный"), ("Mareep", "Обычный"), ("Cyndaquil", "Обычный"),
                        ("Snorlax", "Редкий"), ("Togepi", "Редкий")
                    ]
                elif loc == "cave":
                    pool = [
                        ("Mewtwo", "Легендарный"), ("Rayquaza", "Легендарный"), ("Lugia", "Легендарный"),
                        ("Treecko", "Обычный"), ("Torchic", "Обычный"), ("Mudkip", "Обычный"),
                        ("Ralts", "Редкий"), ("Tyranitar", "Легендарный"), ("Gengar", "Редкий")
                    ]
                else:
                    pool = [
                        ("Mewtwo", "Легендарный"), ("Rayquaza", "Легендарный"), ("Lugia", "Легендарный"),
                        ("Tyranitar", "Легендарный"), ("Snorlax", "Редкий"), ("Gardevoir", "Легендарный")
                    ]
                
                chosen, rarity = random.choice(pool)
                shiny_chance = 0.30 if loc == "portal" else (0.15 if loc == "cave" else 0.05)
                is_shiny = 1 if random.random() < shiny_chance else 0

                await db.execute("UPDATE users SET pokeballs = pokeballs - ? WHERE user_id = ?", (cost, user_id))
                await db.execute("INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, ?, ?, 1, 50)", 
                                 (user_id, chosen, rarity, is_shiny))
                await db.commit()
                
                shiny_text = "✨ SHINY " if is_shiny else ""
                msg = f"Успех! Пойман покемон: {shiny_text}{chosen} ({rarity})!"
            else:
                msg = "Недостаточно Poké Balls! Купите их в магазине."
                
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message={msg}", status_code=303)

@app.get("/battle")
async def battle(user_id: int, tab: str = "battle"):
    battle_msg = ""
    evo_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT exp, level, starter, hp, max_hp FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            if user:
                exp, lvl, starter, hp, max_hp = user[0], user[1], user[2], user[3], user[4]
                
                if hp <= 10:
                    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg=💀 Покемон устал! Вылечите его зельем в профиле.", status_code=303)

                enemy_poke = random.choice(list(POKEMON_DATA.keys()))
                player_type = POKEMON_DATA.get(starter, {}).get("type", "Normal")
                enemy_type = POKEMON_DATA.get(enemy_poke, {}).get("type", "Normal")
                
                multiplier = TYPE_ADVANTAGES.get(player_type, {}).get(enemy_type, 1.0)
                gained_exp = int(35 * multiplier)
                exp += gained_exp
                new_hp = max(5, hp - 15)
                
                if exp >= 100:
                    lvl += 1
                    exp = 0
                    max_hp += 25
                    new_hp = max_hp
                    battle_msg = f"🏆 Победа! Уровень тренера вырос до {lvl}!"
                    
                    current_poke_info = POKEMON_DATA.get(starter, {})
                    evo_level_req = current_poke_info.get("evo_lvl", 99)
                    next_form = current_poke_info.get("next")
                    
                    if lvl >= evo_level_req and next_form:
                        starter = next_form
                        evo_msg = f"🌟 ЭВОЛЮЦИЯ! Ваш покемон превратился в форму: {starter}!"
                else:
                    battle_msg = f"⚔️ Победа в PvE! Получено +{gained_exp} XP и +30 🪙."
                
                await db.execute(
                    "UPDATE users SET exp = ?, level = ?, starter = ?, hp = ?, max_hp = ?, coins = coins + 30 WHERE user_id = ?", 
                    (exp, lvl, starter, new_hp, max_hp, user_id)
                )
                await db.commit()
                
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}&evo_msg={evo_msg}", status_code=303)

@app.get("/pvp")
async def pvp(user_id: int, tab: str = "battle"):
    battle_msg = ""
    win = random.random() < 0.65
    async with aiosqlite.connect(DB_FILE) as db:
        if win:
            await db.execute("UPDATE users SET rating = rating + 25, coins = coins + 50, hp = MAX(5, hp - 20) WHERE user_id = ?", (user_id,))
            battle_msg = "🏆 Успех в PvP! Вы победили соперника (+25 кубков 🏆, +50 🪙)!"
        else:
            await db.execute("UPDATE users SET rating = MAX(0, rating - 15), hp = MAX(5, hp - 35) WHERE user_id = ?", (user_id,))
            battle_msg = "💥 Поражение в PvP! Покемон потерял здоровье (-15 кубков 🏆)."
        await db.commit()
        
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}", status_code=303)

@app.get("/boss")
async def boss(user_id: int, tab: str = "battle"):
    battle_msg = ""
    win = random.random() < 0.50
    async with aiosqlite.connect(DB_FILE) as db:
        if win:
            await db.execute("UPDATE users SET exp = exp + 100, coins = coins + 100, rating = rating + 50, hp = MAX(5, hp - 30) WHERE user_id = ?", (user_id,))
            battle_msg = "👑 ТРИУМФ! Вы победили Легендарного Босса (+100 XP, +100 🪙)!"
        else:
            await db.execute("UPDATE users SET hp = MAX(5, hp - 45) WHERE user_id = ?", (user_id,))
            battle_msg = "💀 Босс разгромил вас! Покемон ранен, полечите его зельем."
        await db.commit()
        
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}", status_code=303)

@app.get("/trade")
async def trade(user_id: int, poke_id: int, tab: str = "collection"):
    trade_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokemon_name FROM collection WHERE id = ? AND user_id = ?", (poke_id, user_id)) as cursor:
            poke = await cursor.fetchone()
            if poke:
                p_name = poke[0]
                trade_pool = ["Pikachu", "Cyndaquil", "Treecko", "Torchic", "Mudkip", "Snorlax", "Ralts", "Gengar"]
                new_poke = random.choice([p for p in trade_pool if p != p_name])
                
                await db.execute("UPDATE collection SET pokemon_name = ? WHERE id = ?", (new_poke, poke_id))
                await db.commit()
                trade_msg = f"🤝 Обмен успешен! Вы получили: {new_poke}!"
            else:
                trade_msg = "Ошибка обмена: покемон не найден."
                
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&trade_msg={trade_msg}", status_code=303)

@app.get("/buy")
async def buy(user_id: int, item: str, tab: str = "shop"):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT coins, stars FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                coins, stars = row[0], row[1]
                if item == "pokeball" and coins >= 50:
                    await db.execute("UPDATE users SET coins = coins - 50, pokeballs = pokeballs + 1 WHERE user_id = ?", (user_id,))
                    await db.commit()
                elif item == "potion" and coins >= 30:
                    await db.execute("UPDATE users SET coins = coins - 30, potions = potions + 1 WHERE user_id = ?", (user_id,))
                    await db.commit()
                elif item == "masterball" and stars >= 5:
                    await db.execute("UPDATE users SET stars = stars - 5, masterballs = masterballs + 1 WHERE user_id = ?", (user_id,))
                    await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}", status_code=303)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000)
