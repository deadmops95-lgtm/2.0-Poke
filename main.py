import os
import random
import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8628464354:AAEQ0XKfv9OR-CR368dSaXq6tQsipn_Wy7w"
DOMAIN = "bot-1790034365-8732-prokudin95.bothost.tech"

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

DB_FILE = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        # Таблица тренера (профиль, экономика, валюта)
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
                coins INTEGER DEFAULT 100
            )
        """)
        # Таблица коллекции покемонов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS collection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pokemon_name TEXT,
                level INTEGER,
                hp INTEGER
            )
        """)
        await db.commit()

@app.on_event("startup")
async def startup_event():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Открыть мир Pokémon", web_app=types.WebAppInfo(url=f"https://{DOMAIN}"))
    await message.answer(
        "👋 Добро пожаловать в официальную MMORPG по миру Pokémon!\n\nНажми кнопку ниже, чтобы запустить игру:",
        reply_markup=builder.as_markup()
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pokémon Mini App - Full Version</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card-glow { box-shadow: 0 0 20px rgba(129, 140, 248, 0.2); border: 1px solid rgba(129, 140, 248, 0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-4 max-w-md mx-auto">

    <!-- Шапка -->
    <header class="flex justify-between items-center bg-slate-800/90 p-4 rounded-2xl card-glow mb-4">
        <div>
            <h1 class="font-bold text-sm text-indigo-400">⚡ Лига Тренеров</h1>
            <p class="text-xs text-slate-400" id="tg-username">Загрузка...</p>
        </div>
        <div class="flex items-center gap-2">
            <span class="bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2.5 py-1 rounded-full text-xs font-bold">🪙 {{ user[8] if user else 0 }}</span>
        </div>
    </header>

    <!-- Основной контент -->
    <main class="my-auto">
        {% if not user %}
            <!-- Экран регистрации -->
            <div class="bg-slate-800/90 p-6 rounded-3xl card-glow text-center">
                <h2 class="text-xl font-bold mb-2 text-yellow-400">Регистрация Тренера</h2>
                <p class="text-xs text-slate-300 mb-6">Выберите своего первого стартового Pokémon:</p>
                
                <form action="/register" method="GET" class="space-y-4">
                    <input type="hidden" name="user_id" id="input_user_id" value="12345">
                    <input type="hidden" name="username" id="input_username" value="Trainer">

                    <div class="grid grid-cols-3 gap-2">
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Bulbasaur" class="peer hidden" checked>
                            <div class="p-3 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-emerald-500 peer-checked:bg-emerald-950/40">
                                <div class="text-2xl">🌱</div>
                                <div class="text-[10px] font-bold text-emerald-400 mt-1">Бульбазавр</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Charmander" class="peer hidden">
                            <div class="p-3 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-orange-500 peer-checked:bg-orange-950/40">
                                <div class="text-2xl">🔥</div>
                                <div class="text-[10px] font-bold text-orange-400 mt-1">Чармандер</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Squirtle" class="peer hidden">
                            <div class="p-3 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-blue-500 peer-checked:bg-blue-950/40">
                                <div class="text-2xl">💧</div>
                                <div class="text-[10px] font-bold text-blue-400 mt-1">Сквиртл</div>
                            </div>
                        </label>
                    </div>

                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-600 font-bold rounded-xl text-xs shadow-lg">
                        Начать путешествие! 🚀
                    </button>
                </form>
            </div>
        {% else %}
            <!-- Вкладка 1: Профиль -->
            <div id="tab-profile" class="tab-content active space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <div class="inline-block p-3 bg-indigo-500/10 rounded-full border border-indigo-500/30 text-4xl">
                        {% if user[2] == 'Charmander' %}🔥{% elif user[2] == 'Squirtle' %}💧{% else %}🌱{% endif %}
                    </div>
                    <h2 class="text-base font-bold text-indigo-200">Стартер: <span class="text-yellow-400">{{ user[2] }}</span></h2>
                    
                    <div class="grid grid-cols-3 gap-2 bg-slate-900/60 p-2 rounded-2xl text-center text-[11px]">
                        <div><span class="text-slate-400 block">Уровень</span><span class="font-bold text-indigo-400">{{ user[3] }}</span></div>
                        <div><span class="text-slate-400 block">Опыт</span><span class="font-bold text-emerald-400">{{ user[4] }}</span></div>
                        <div><span class="text-slate-400 block">HP</span><span class="font-bold text-rose-400">{{ user[5] }}/{{ user[6] }}</span></div>
                    </div>
                </div>
            </div>

            <!-- Вкладка 2: Карта мира (Поиск покемонов) -->
            <div id="tab-map" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3">
                    <h2 class="text-sm font-bold text-indigo-300 text-center">🗺️ Карта Мира</h2>
                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <span>🌲 Маршрут 1 (Лес)</span>
                            <a href="/explore?user_id={{ user[0] }}&loc=forest" class="px-3 py-1 bg-emerald-600/30 border border-emerald-500 text-emerald-300 rounded-lg font-bold">Искать</a>
                        </div>
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <span>⛰️ Пещера Диглетта</span>
                            <a href="/explore?user_id={{ user[0] }}&loc=cave" class="px-3 py-1 bg-amber-600/30 border border-amber-500 text-amber-300 rounded-lg font-bold">Искать</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Вкладка 3: Коллекция (Pokédex / Box) -->
            <div id="tab-collection" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-indigo-300">📦 Коллекция Покемонов</h2>
                    <div class="grid grid-cols-2 gap-2 text-left max-h-48 overflow-y-auto">
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-xs">
                            <span class="font-bold text-yellow-400">⭐ {{ user[2] }}</span>
                            <p class="text-[10px] text-slate-400">Уровень: {{ user[3] }}</p>
                        </div>
                        {% for p in collection %}
                        <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-xs">
                            <span class="font-bold text-emerald-400">⚡ {{ p[2] }}</span>
                            <p class="text-[10px] text-slate-400">Уровень: {{ p[3] }} (HP: {{ p[4] }})</p>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Вкладка 4: PvE Арена Боев -->
            <div id="tab-battle" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <h2 class="text-sm font-bold text-rose-400">⚔️ PvE Арена</h2>
                    <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700 space-y-3">
                        <p class="text-xs text-slate-300">Сразись с диким тренером за опыт и монеты!</p>
                        <a href="/battle?user_id={{ user[0] }}" class="block w-full py-2 bg-rose-600 hover:bg-rose-700 font-bold rounded-xl text-xs transition text-white">
                            💥 Начать бой!
                        </a>
                    </div>
                </div>
            </div>

            <!-- Вкладка 5: Магазин и Инвентарь -->
            <div id="tab-shop" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <h2 class="text-sm font-bold text-amber-400">🛒 Магазин и Инвентарь</h2>
                    <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-xs flex justify-between items-center">
                        <span>🔴 Poké Balls в наличии</span>
                        <span class="font-bold text-yellow-400">{{ user[7] }} шт.</span>
                    </div>
                    <a href="/buy?user_id={{ user[0] }}" class="block w-full py-2 bg-amber-600 hover:bg-amber-700 font-bold rounded-xl text-xs transition text-white">
                        🛍️ Купить Poké Ball (50 🪙)
                    </a>
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
            document.getElementById('tg-username').innerText = '@' + (u.username || u.first_name);
            document.getElementById('input_user_id').value = u.id;
            document.getElementById('input_username').value = u.first_name;
        }

        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('user_id') && userId !== 12345) {
            window.location.href = `/?user_id=${userId}`;
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
async def index(request: Request, user_id: int = 12345):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
        collection = []
        if user:
            async with db.execute("SELECT * FROM collection WHERE user_id = ?", (user_id,)) as cursor:
                collection = await cursor.fetchall()
            
    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(request=request, user=user, collection=collection)
    return HTMLResponse(content=rendered_html)

@app.get("/register")
async def register(user_id: int, username: str = "Тренер", starter: str = "Bulbasaur"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, starter, level, exp, hp, max_hp, pokeballs, coins) VALUES (?, ?, ?, 1, 0, 100, 100, 5, 100)",
            (user_id, username, starter)
        )
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/explore")
async def explore(user_id: int, loc: str):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokeballs FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] > 0:
                wild_pokemons = ["Pikachu", "Rattata", "Pidgey", "Zubat"] if loc == "forest" else ["Diglett", "Geodude", "Zubat"]
                caught = random.choice(wild_pokemons)
                
                await db.execute("UPDATE users SET pokeballs = pokeballs - 1 WHERE user_id = ?", (user_id,))
                if random.random() < 0.65:
                    await db.execute("INSERT INTO collection (user_id, pokemon_name, level, hp) VALUES (?, ?, 1, 50)", (user_id, caught))
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/battle")
async def battle(user_id: int):
    # PvE бой: победа дает опыт и монеты
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE users SET exp = exp + 25, coins = coins + 20 WHERE user_id = ?", (user_id,))
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/buy")
async def buy(user_id: int):
    # Покупка покеболов за монеты
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] >= 50:
                await db.execute("UPDATE users SET coins = coins - 50, pokeballs = pokeballs + 1 WHERE user_id = ?", (user_id,))
                await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000)
