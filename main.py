import os
import random
import time
import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from contextlib import asynccontextmanager

TOKEN = "8628464354:AAEQ0XKfv9OR-CR368dSaXq6tQsipn_Wy7w"
DOMAIN = "bot-1790034365-8732-prokudin95.bothost.tech"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))
    yield
    await bot.session.close()

app = FastAPI(lifespan=lifespan)
DB_FILE = "database.db"

POKEMON_DATA = {
    "Bulbasaur": {"id": 1, "next": "Ivysaur", "evo_lvl": 3, "type": "Grass", "hp": 100, "rarity": "Обычный"},
    "Ivysaur": {"id": 2, "next": "Venusaur", "evo_lvl": 6, "type": "Grass", "hp": 150, "rarity": "Редкий"},
    "Venusaur": {"id": 3, "next": None, "evo_lvl": 99, "type": "Grass", "hp": 220, "rarity": "Эпический"},
    
    "Charmander": {"id": 4, "next": "Charmeleon", "evo_lvl": 3, "type": "Fire", "hp": 95, "rarity": "Обычный"},
    "Charmeleon": {"id": 5, "next": "Charizard", "evo_lvl": 6, "type": "Fire", "hp": 145, "rarity": "Редкий"},
    "Charizard": {"id": 6, "next": None, "evo_lvl": 99, "type": "Fire", "hp": 230, "rarity": "Эпический"},

    "Squirtle": {"id": 7, "next": "Wartortle", "evo_lvl": 3, "type": "Water", "hp": 105, "rarity": "Обычный"},
    "Wartortle": {"id": 8, "next": "Blastoise", "evo_lvl": 6, "type": "Water", "hp": 155, "rarity": "Редкий"},
    "Blastoise": {"id": 9, "next": None, "evo_lvl": 99, "type": "Water", "hp": 225, "rarity": "Эпический"},

    "Pikachu": {"id": 25, "next": "Raichu", "evo_lvl": 5, "type": "Electric", "hp": 110, "rarity": "Редкий"},
    "Raichu": {"id": 26, "next": None, "evo_lvl": 99, "type": "Electric", "hp": 180, "rarity": "Эпический"},

    "Pidgey": {"id": 16, "next": None, "evo_lvl": 99, "type": "Normal", "hp": 80, "rarity": "Обычный"},
    "Zubat": {"id": 41, "next": None, "evo_lvl": 99, "type": "Poison", "hp": 85, "rarity": "Обычный"},
    "Snorlax": {"id": 143, "next": None, "evo_lvl": 99, "type": "Normal", "hp": 300, "rarity": "Эпический"},

    "Mewtwo": {"id": 150, "next": None, "evo_lvl": 99, "type": "Psychic", "hp": 450, "rarity": "Легендарный"},
    "Lugia": {"id": 249, "next": None, "evo_lvl": 99, "type": "Water", "hp": 420, "rarity": "Легендарный"},
    "Rayquaza": {"id": 384, "next": None, "evo_lvl": 99, "type": "Dragon", "hp": 500, "rarity": "Легендарный"}
}

TYPE_ADVANTAGES = {
    "Fire": {"Grass": 1.5, "Water": 0.6, "Fire": 1.0, "Electric": 1.0, "Normal": 1.0, "Poison": 1.0, "Psychic": 1.0, "Dragon": 1.0},
    "Water": {"Fire": 1.5, "Grass": 0.6, "Water": 1.0, "Electric": 0.8, "Normal": 1.0, "Poison": 1.0, "Psychic": 1.0, "Dragon": 1.0},
    "Grass": {"Water": 1.5, "Fire": 0.6, "Grass": 1.0, "Electric": 1.0, "Normal": 1.0, "Poison": 0.8, "Psychic": 1.0, "Dragon": 1.0},
    "Electric": {"Water": 1.5, "Grass": 0.8, "Electric": 1.0, "Fire": 1.0, "Normal": 1.0, "Poison": 1.0, "Psychic": 1.0, "Dragon": 1.0},
    "Psychic": {"Poison": 1.5, "Normal": 1.2, "Psychic": 1.0, "Fire": 1.0, "Water": 1.0, "Grass": 1.0, "Electric": 1.0, "Dragon": 1.0},
    "Dragon": {"Dragon": 1.5, "Fire": 1.2, "Water": 1.2, "Grass": 1.2, "Electric": 1.2, "Normal": 1.0, "Poison": 1.0, "Psychic": 1.0},
    "Normal": {},
    "Poison": {}
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
                energy INTEGER DEFAULT 100,
                pokeballs INTEGER DEFAULT 3,
                potions INTEGER DEFAULT 1,
                coins INTEGER DEFAULT 50,
                stars INTEGER DEFAULT 5,
                rating INTEGER DEFAULT 1000,
                last_daily INTEGER DEFAULT 0,
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
                hp INTEGER DEFAULT 100
            )
        """)
        await db.commit()

# Команда /start без кнопки (кнопка теперь только через меню BotFather)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "⚡ **Pokémon World MMORPG**\n\nДобро пожаловать в лигу тренеров!\nЧтобы начать приключение, нажмите кнопку **«Играть»** в меню слева внизу экрана."
    )

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
                <span class="text-[10px] text-slate-400">Клан: <strong class="text-indigo-300">{{ user[14] if user else 'Без клана' }}</strong></span>
            </div>
        </div>
        <div class="flex items-center gap-1.5">
            <span class="bg-amber-500/20 text-amber-300 px-2 py-1 rounded-lg border border-amber-500/30 font-bold">🪙 {{ user[10] if user else 0 }}</span>
            <span class="bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded-lg border border-cyan-500/30 font-bold">⚡ {{ user[7] if user else 100 }}/100</span>
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
            <!-- Профиль -->
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

                    {% if message %}
                    <div class="p-2 bg-indigo-950/60 border border-indigo-500/40 rounded-xl text-xs">
                        <p class="font-bold text-yellow-300">{{ message }}</p>
                    </div>
                    {% endif %}

                    <!-- Бонус / Ежедневная награда -->
                    <a href="/daily?user_id={{ user[0] }}&tab=profile" class="block w-full py-2 bg-gradient-to-r from-amber-500 to-orange-600 font-bold rounded-xl text-xs text-white shadow">
                        🎁 Забрать ежедневный бонус
                    </a>

                    <div class="bg-indigo-950/50 p-3 rounded-2xl border border-indigo-500/40 text-xs text-left space-y-2">
                        <span class="font-bold text-indigo-300 block">🛡️ Клан: <strong class="text-yellow-400">{{ user[14] }}</strong></span>
                        {% if user[14] == 'Без клана' %}
                        <div class="grid grid-cols-3 gap-1">
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Rocket&tab=profile" class="py-1.5 bg-indigo-600 text-white rounded-lg font-bold text-[10px] text-center">Rocket</a>
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Mystic&tab=profile" class="py-1.5 bg-blue-600 text-white rounded-lg font-bold text-[10px] text-center">Mystic</a>
                            <a href="/join_clan?user_id={{ user[0] }}&clan=Team Valor&tab=profile" class="py-1.5 bg-rose-600 text-white rounded-lg font-bold text-[10px] text-center">Valor</a>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Карта мира -->
            <div id="tab-map" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-indigo-300">🗺️ Карта Мира</h2>
                    {% if map_msg %}<p class="text-xs text-yellow-300 font-bold">{{ map_msg }}</p>{% endif %}
                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <div>
                                <span class="font-bold text-emerald-400 block">🌲 Густой Лес</span>
                                <span class="text-[10px] text-slate-400">Стоит: 1 🔴 Ball + 15 ⚡</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=forest&tab=map" class="px-3 py-1.5 bg-emerald-600/30 border border-emerald-500 text-emerald-300 rounded-lg font-bold">Идти</a>
                        </div>
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <div>
                                <span class="font-bold text-amber-400 block">⛰️ Темные Пещеры</span>
                                <span class="text-[10px] text-slate-400">Стоит: 1 🔴 Ball + 25 ⚡</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=cave&tab=map" class="px-3 py-1.5 bg-amber-600/30 border border-amber-500 text-amber-300 rounded-lg font-bold">Идти</a>
                        </div>
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-purple-500/50">
                            <div>
                                <span class="font-bold text-purple-300 block">✨ Ультра-Портал</span>
                                <span class="text-[10px] text-slate-400">Стоит: 2 🔴 Ball + 40 ⚡</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=portal&tab=map" class="px-3 py-1.5 bg-purple-600/30 border border-purple-500 text-purple-300 rounded-lg font-bold">Портал</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Коллекция -->
            <div id="tab-collection" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-yellow-400">📦 Коллекция (Уникальных: {{ pokedex_count }}/12)</h2>
                    <div class="grid grid-cols-2 gap-2 text-left max-h-40 overflow-y-auto pr-1">
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
                                <a href="/set_active?user_id={{ user[0] }}&poke_id={{ p[0] }}&tab=collection" class="px-1.5 py-0.5 bg-emerald-600/60 text-white rounded text-[9px] font-bold text-center">В бой</a>
                                <a href="/sell?user_id={{ user[0] }}&poke_id={{ p[0] }}&tab=collection" class="px-1.5 py-0.5 bg-rose-600/40 text-rose-200 rounded text-[9px] font-bold text-center">Продать</a>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Арена -->
            <div id="tab-battle" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <h2 class="text-sm font-bold text-rose-400">⚔️ Боевые Арены</h2>
                    {% if battle_msg %}<p class="text-xs text-yellow-300 font-bold">{{ battle_msg }}</p>{% endif %}
                    <div class="grid grid-cols-2 gap-2 text-xs">
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 space-y-2">
                            <span class="font-bold text-rose-400 block">🌲 PvE Тренировка</span>
                            <span class="text-[10px] text-slate-400">Стоит: 20 ⚡</span>
                            <a href="/battle?user_id={{ user[0] }}&tab=battle" class="block w-full py-1.5 bg-rose-600 text-white font-bold rounded-lg">В бой</a>
                        </div>
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-indigo-500/50 space-y-2">
                            <span class="font-bold text-indigo-400 block">🏆 PvP Дуэль</span>
                            <span class="text-[10px] text-slate-400">Стоит: 30 ⚡</span>
                            <a href="/pvp_live?user_id={{ user[0] }}&tab=battle" class="block w-full py-1.5 bg-indigo-600 text-white font-bold rounded-lg">Найти</a>
                        </div>
                    </div>
                    <a href="/boss?user_id={{ user[0] }}&tab=battle" class="block w-full py-2 bg-amber-600 text-white font-bold rounded-xl text-xs">👑 Рейд на Босса (50 ⚡)</a>
                </div>
            </div>

            <!-- Магазин -->
            <div id="tab-shop" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-xs">
                    <h2 class="text-sm font-bold text-amber-400 text-center">🛒 Магазин Лиги</h2>
                    <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-200 block">🔴 Poké Ball (+1)</span>
                            <span class="text-[10px] text-slate-400">Цена: 60 🪙</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=pokeball&tab=shop" class="px-3 py-1.5 bg-amber-600 font-bold rounded-lg text-white">Купить</a>
                    </div>
                    <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-cyan-300 block">⚡ Энергетик (+50 ⚡)</span>
                            <span class="text-[10px] text-slate-400">Цена: 40 🪙</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=energy&tab=shop" class="px-3 py-1.5 bg-cyan-600 font-bold rounded-lg text-white">Купить</a>
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

        if (!urlParams.has('user_id')) {
            if (tgUserId) {
                window.location.replace(`/?user_id=${tgUserId}`);
            } else {
                document.body.innerHTML = '<div style="background:#090d16; color:#fff; padding:40px; text-align:center; font-family:sans-serif;"><h2 style="color:#facc15;">⚠️ Ошибка доступа</h2><p style="margin-top:10px; font-size:14px; color:#94a3b8;">Пожалуйста, открывайте игру через кнопку в официальном Telegram-боте!</p></div>';
            }
        }

        const inputId = document.getElementById('input_user_id');
        const inputName = document.getElementById('input_username');
        if (inputId && tgUserId) inputId.value = tgUserId;
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
            "Snorlax": 143, "Mewtwo": 150, "Lugia": 249, "Rayquaza": 384
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
        return RedirectResponse(url="/", status_code=303)
    
    starter_info = POKEMON_DATA.get(starter, {"hp": 100})
    base_hp = starter_info["hp"]

    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            exists = await cursor.fetchone()
        if not exists:
            await db.execute(
                "INSERT INTO users (user_id, username, starter, level, exp, hp, max_hp, energy, pokeballs, coins, rating, clan_name) VALUES (?, ?, ?, 1, 0, ?, ?, 100, 3, 50, 1000, 'Без клана')",
                (user_id, username, starter, base_hp, base_hp)
            )
            await db.execute(
                "INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, 'Обычный', 0, 1, ?)",
                (user_id, starter, base_hp)
            )
            await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab=profile", status_code=303)

@app.get("/daily")
async def daily(user_id: int, tab: str = "profile"):
    now = int(time.time())
    msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                last_d = row[0]
                if now - last_d >= 86400:
                    await db.execute("UPDATE users SET coins = coins + 100, energy = 100, pokeballs = pokeballs + 2, last_daily = ? WHERE user_id = ?", (now, user_id))
                    await db.commit()
                    msg = "🎁 Ежедневный бонус получен! (+100 🪙, +2 🔴 Balls, полный запас ⚡)"
                else:
                    hours_left = int((86400 - (now - last_d)) / 3600)
                    msg = f"⏳ Бонус будет доступен через {hours_left} ч."
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message={msg}", status_code=303)

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
        async with db.execute("SELECT pokemon_name, level, hp FROM collection WHERE id = ? AND user_id = ?", (poke_id, user_id)) as cursor:
            poke = await cursor.fetchone()
            if poke:
                p_name, p_lvl, p_hp = poke
                await db.execute("UPDATE users SET starter = ?, level = ?, hp = ?, max_hp = ? WHERE user_id = ?", (p_name, p_lvl, p_hp, p_hp, user_id))
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message=⚡ Боевой покемон изменен!", status_code=303)

@app.get("/explore")
async def explore(user_id: int, loc: str, tab: str = "map"):
    map_msg = ""
    energy_cost = 15 if loc == "forest" else (25 if loc == "cave" else 40)
    ball_cost = 2 if loc == "portal" else 1

    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokeballs, energy FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] >= ball_cost and row[1] >= energy_cost:
                if loc == "forest":
                    pool = ["Pikachu", "Pidgey", "Bulbasaur", "Charmander", "Squirtle", "Zubat"]
                    is_shiny = 1 if random.random() < 0.03 else 0
                elif loc == "cave":
                    pool = ["Ivysaur", "Charmeleon", "Wartortle", "Raichu", "Snorlax"]
                    is_shiny = 1 if random.random() < 0.07 else 0
                else:
                    pool = ["Venusaur", "Charizard", "Blastoise", "Mewtwo", "Lugia", "Rayquaza"]
                    is_shiny = 1 if random.random() < 0.15 else 0
                
                chosen = random.choice(pool)
                p_info = POKEMON_DATA.get(chosen, {"hp": 100, "rarity": "Редкий"})
                p_hp = p_info["hp"]
                p_rarity = p_info["rarity"]

                await db.execute("UPDATE users SET pokeballs = pokeballs - ?, energy = energy - ? WHERE user_id = ?", (ball_cost, energy_cost, user_id))
                await db.execute("INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, ?, ?, 1, ?)", (user_id, chosen, p_rarity, is_shiny, p_hp))
                await db.commit()
                map_msg = f"🎉 Пойман: {'✨ SHINY ' if is_shiny else ''}{chosen} ({p_rarity})!"
            else:
                map_msg = "❌ Не хватает Poké Balls или Энергии (⚡)!"
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&map_msg={map_msg}", status_code=303)

@app.get("/pvp_live")
async def pvp_live(user_id: int, tab: str = "battle"):
    battle_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT starter, energy FROM users WHERE user_id = ?", (user_id,)) as cursor:
            my_user = await cursor.fetchone()
        
        if not my_user or my_user[1] < 30:
            battle_msg = "⚡ Недостаточно энергии для PvP (нужно 30 ⚡)!"
        else:
            async with db.execute("SELECT user_id, username, starter FROM users WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (user_id,)) as cursor:
                opponent = await cursor.fetchone()
            
            if not opponent:
                battle_msg = "👥 Нет соперников для PvP."
            else:
                opp_id, opp_name, opp_poke = opponent
                win = random.random() < 0.5
                if win:
                    await db.execute("UPDATE users SET rating = rating + 25, coins = coins + 40, energy = energy - 30 WHERE user_id = ?", (user_id,))
                    await db.execute("UPDATE users SET rating = MAX(0, rating - 15) WHERE user_id = ?", (opp_id,))
                    battle_msg = f"🏆 Победа в PvP над @{opp_name or 'Тренер'}! (+25 🏆, +40 🪙)"
                else:
                    await db.execute("UPDATE users SET rating = MAX(0, rating - 15), energy = energy - 30 WHERE user_id = ?", (user_id,))
                    battle_msg = f"💥 Поражение в PvP! (-15 🏆)"
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}", status_code=303)

@app.get("/battle")
async def battle(user_id: int, tab: str = "battle"):
    battle_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT exp, level, starter, energy FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user_data = await cursor.fetchone()
            if user_data:
                exp, lvl, starter_name, energy = user_data
                if energy < 20:
                    battle_msg = "❌ Недостаточно энергии (⚡) для боя!"
                else:
                    # PvE может как дать опыт, так и наказать при низком уровне
                    success = random.random() < (0.6 + (lvl * 0.05))
                    energy -= 20
                    
                    if success:
                        exp += 35
                        p_info = POKEMON_DATA.get(starter_name, {"next": None, "evo_lvl": 99, "hp": 100})
                        next_poke = p_info["next"]
                        evo_lvl = p_info["evo_lvl"]
                        
                        if exp >= 100:
                            lvl += 1
                            exp = 0
                            if lvl >= evo_lvl and next_poke and next_poke in POKEMON_DATA:
                                starter_name = next_poke
                                new_hp = POKEMON_DATA[next_poke]["hp"]
                                battle_msg = f"✨ ЭВОЛЮЦИЯ! Покемон превратился в {next_poke} (Ур. {lvl})!"
                                await db.execute("UPDATE users SET starter = ?, level = ?, exp = ?, hp = ?, max_hp = ?, energy = ? WHERE user_id = ?", (starter_name, lvl, exp, new_hp, new_hp, energy, user_id))
                                await db.execute("INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, 'Редкий', 0, ?, ?)", (user_id, starter_name, lvl, new_hp))
                            else:
                                battle_msg = f"🏆 Победа в PvE! Уровень вырос до {lvl}!"
                                await db.execute("UPDATE users = users..., level = ?, exp = ?, energy = ?, coins = coins + 20 WHERE user_id = ?", (lvl, exp, energy, user_id))
                        else:
                            battle_msg = f"⚔️ Победа в PvE! (+35 XP, +20 🪙)."
                            await db.execute("UPDATE users SET exp = ?, energy = ?, coins = coins + 20 WHERE user_id = ?", (exp, energy, user_id))
                    else:
                        battle_msg = "💀 Вы проиграли дикому покемону в лесу! Энергия потрачена впустую."
                        await db.execute("UPDATE users SET energy = ? WHERE user_id = ?", (energy, user_id))
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}", status_code=303)

@app.get("/boss")
async def boss(user_id: int, tab: str = "battle"):
    battle_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("Energy, level FROM users WHERE user_id = ?", (user_id,)) as cursor:
            # упрощенный рейд босса
            await db.execute("UPDATE users SET exp = exp + 80, coins = coins + 70, rating = rating + 30 WHERE user_id = ?", (user_id,))
            await db.commit()
            battle_msg = "👑 Победа над Боссом! (+80 XP, +70 🪙)"
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&battle_msg={battle_msg}", status_code=303)

@app.get("/buy")
async def buy(user_id: int, item: str, tab: str = "shop"):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                coins = row[0]
                if item == "pokeball" and coins >= 60:
                    await db.execute("UPDATE users SET coins = coins - 60, pokeballs = pokeballs + 1 WHERE user_id = ?", (user_id,))
                    await db.commit()
                elif item == "energy" and coins >= 40:
                    await db.execute("UPDATE users SET coins = coins - 40, energy = MIN(100, energy + 50) WHERE user_id = ?", (user_id,))
                    await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}", status_code=303)

@app.get("/sell")
async def sell(user_id: int, poke_id: int, tab: str = "collection"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM collection WHERE id = ?", (poke_id,))
        await db.execute("UPDATE users SET coins = coins + 30 WHERE user_id = ?", (user_id,))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}&tab={tab}&message=💰 Продано за 30 🪙!", status_code=303)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
