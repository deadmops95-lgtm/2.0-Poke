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

# Словарь официальных ID покемонов для выгрузки картинок спрайтов
POKEMON_IDS = {
    "Bulbasaur": 1, "Charmander": 4, "Squirtle": 7,
    "Pikachu": 25, "Pidgey": 16, "Zubat": 41,
    "Diglett": 50, "Geodude": 74, "Mewtwo": 150, "Rattata": 19
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
                coins INTEGER DEFAULT 150,
                stars INTEGER DEFAULT 10
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
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Играть в Pokémon MMORPG", web_app=types.WebAppInfo(url=f"https://{DOMAIN}"))
    await message.answer(
        "👋 Добро пожаловать в мир Pokémon!\n\nСобери свою коллекцию, сражайся и стань мастером. Жми кнопку ниже:",
        reply_markup=builder.as_markup()
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

    <!-- Верхняя панель -->
    <header class="flex justify-between items-center bg-slate-800/90 p-3 rounded-2xl card-glow mb-3 text-xs">
        <div class="flex items-center gap-2">
            <div id="header-avatar" class="w-8 h-8 bg-indigo-600/30 rounded-full flex items-center justify-center font-bold text-indigo-300">⚡</div>
            <div>
                <h1 class="font-bold text-indigo-400 text-sm" id="tg-username">Тренер</h1>
                <span class="text-[10px] text-slate-400">Уровень тренера: <strong class="text-indigo-300">{{ user[3] if user else 1 }}</strong></span>
            </div>
        </div>
        <div class="flex items-center gap-1.5">
            <span class="bg-amber-500/20 text-amber-300 px-2 py-1 rounded-lg border border-amber-500/30 font-bold">🪙 {{ user[9] if user else 0 }}</span>
            <span class="bg-purple-500/20 text-purple-300 px-2 py-1 rounded-lg border border-purple-500/30 font-bold">⭐ {{ user[10] if user else 0 }}</span>
        </div>
    </header>

    <!-- Основной контент -->
    <main class="my-auto">
        {% if not user %}
            <!-- Регистрация -->
            <div class="bg-slate-800/90 p-6 rounded-3xl card-glow text-center space-y-4">
                <h2 class="text-xl font-black text-yellow-400">Путь Тренера</h2>
                <p class="text-xs text-slate-300">Выберите своего первого стартового Pokémon:</p>
                
                <form action="/register" method="GET" class="space-y-4">
                    <input type="hidden" name="user_id" id="input_user_id" value="12345">
                    <input type="hidden" name="username" id="input_username" value="Trainer">

                    <div class="grid grid-cols-3 gap-2">
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Bulbasaur" class="peer hidden" checked>
                            <div class="p-3 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-emerald-500 peer-checked:bg-emerald-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png" class="w-16 h-16 mx-auto pixel-art">
                                <div class="text-[11px] font-bold text-emerald-400 mt-1">Бульбазавр</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Charmander" class="peer hidden">
                            <div class="p-3 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-orange-500 peer-checked:bg-orange-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png" class="w-16 h-16 mx-auto pixel-art">
                                <div class="text-[11px] font-bold text-orange-400 mt-1">Чармандер</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Squirtle" class="peer hidden">
                            <div class="p-3 bg-slate-900 rounded-2xl border border-slate-700 peer-checked:border-blue-500 peer-checked:bg-blue-950/40 text-center">
                                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png" class="w-16 h-16 mx-auto pixel-art">
                                <div class="text-[11px] font-bold text-blue-400 mt-1">Сквиртл</div>
                            </div>
                        </label>
                    </div>

                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-600 font-bold rounded-xl text-xs shadow-lg text-white">
                        Начать приключение! 🚀
                    </button>
                </form>
            </div>
        {% else %}
            <!-- Вкладка 1: Профиль -->
            <div id="tab-profile" class="tab-content active space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <div class="inline-block p-2 bg-indigo-500/10 rounded-2xl border border-indigo-500/30">
                        <img id="starter-img" src="" class="w-24 h-24 mx-auto pixel-art">
                    </div>
                    <h2 class="text-base font-bold text-indigo-200">Ваш стартер: <span class="text-yellow-400">{{ user[2] }}</span></h2>
                    
                    <!-- Прогресс бар опыта -->
                    <div class="bg-slate-900/60 p-3 rounded-2xl space-y-1 text-left text-xs">
                        <div class="flex justify-between text-[11px]">
                            <span class="text-slate-400">Опыт до след. уровня:</span>
                            <span class="font-bold text-emerald-400">{{ user[4] }}/100 XP</span>
                        </div>
                        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div class="bg-emerald-500 h-full transition-all duration-500" style="width: {{ user[4] }}%;"></div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2 bg-slate-900/60 p-2.5 rounded-2xl text-center text-xs">
                        <div><span class="text-slate-400 block">Здоровье (HP)</span><span class="font-bold text-rose-400">{{ user[5] }}/{{ user[6] }}</span></div>
                        <div><span class="text-slate-400 block">Покеболы</span><span class="font-bold text-amber-400">🔴 {{ user[7] }} шт.</span></div>
                    </div>
                </div>
            </div>

            <!-- Вкладка 2: Карта мира (С уведомлением о поимке) -->
            <div id="tab-map" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3">
                    <h2 class="text-sm font-bold text-indigo-300 text-center">🗺️ Карта Мира</h2>
                    
                    {% if message %}
                    <div class="p-3 bg-indigo-950/60 border border-indigo-500/40 rounded-xl text-center text-xs animate-pulse">
                        <p class="font-bold text-yellow-300">{{ message }}</p>
                    </div>
                    {% endif %}

                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <div>
                                <span class="font-bold text-emerald-400 block">🌲 Лес Кенто</span>
                                <span class="text-[10px] text-slate-400">Пикачу, Пиджи, Бульбазавр</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=forest" class="px-3 py-1.5 bg-emerald-600/30 border border-emerald-500 text-emerald-300 rounded-lg font-bold hover:bg-emerald-600/50">Идти (-1 🔴)</a>
                        </div>
                        <div class="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-700">
                            <div>
                                <span class="font-bold text-amber-400 block">⛰️ Пещера Мьюту</span>
                                <span class="text-[10px] text-slate-400">Редкие покемоны & Шанс Shiny!</span>
                            </div>
                            <a href="/explore?user_id={{ user[0] }}&loc=cave" class="px-3 py-1.5 bg-amber-600/30 border border-amber-500 text-amber-300 rounded-lg font-bold hover:bg-amber-600/50">Идти (-1 🔴)</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Вкладка 3: Коллекция / Покемоны с картинками -->
            <div id="tab-collection" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-center">
                    <h2 class="text-sm font-bold text-indigo-300">📦 Коллекция Pokémon (Box)</h2>
                    <div class="grid grid-cols-2 gap-2 text-left max-h-52 overflow-y-auto pr-1">
                        <!-- Стартовый покемон -->
                        <div class="bg-slate-900/60 p-2.5 rounded-xl border border-slate-700 flex items-center gap-2 text-xs">
                            <img src="" id="starter-box-img" class="w-10 h-10 pixel-art">
                            <div>
                                <span class="font-bold text-yellow-400 block">{{ user[2] }}</span>
                                <span class="text-[10px] text-slate-400">Ур. {{ user[3] }} (Стартер)</span>
                            </div>
                        </div>
                        
                        <!-- Пойманные покемоны -->
                        {% for p in collection %}
                        <div class="p-2.5 rounded-xl text-xs flex items-center gap-2 {% if p[4] == 1 %}shiny-card{% else %}bg-slate-900/60 border border-slate-700{% endif %}">
                            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{{ p[6] }}.png" class="w-10 h-10 pixel-art">
                            <div>
                                <span class="font-bold {% if p[4] == 1 %}text-purple-300{% else %}text-emerald-400{% endif %} block">
                                    {% if p[4] == 1 %}✨ {% endif %}{{ p[2] }}
                                </span>
                                <span class="text-[10px] text-slate-400">Ур. {{ p[5] }} | {{ p[3] }}</span>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Вкладка 4: Арена PvE (С логом битвы) -->
            <div id="tab-battle" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow text-center space-y-3">
                    <h2 class="text-sm font-bold text-rose-400">⚔️ PvE Арена Сражений</h2>
                    
                    {% if battle_msg %}
                    <div class="p-3 bg-rose-950/60 border border-rose-500/40 rounded-xl text-center text-xs">
                        <p class="font-bold text-rose-300">{{ battle_msg }}</p>
                    </div>
                    {% endif %}

                    <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700 space-y-3 text-xs">
                        <p class="text-slate-300">Бейтесь с дикими тренерами, поднимайте опыт покемона и получайте 🪙 монеты!</p>
                        <a href="/battle?user_id={{ user[0] }}" class="block w-full py-2.5 bg-rose-600 hover:bg-rose-700 font-bold rounded-xl transition text-white shadow-lg">
                            💥 Атаковать противника
                        </a>
                    </div>
                </div>
            </div>

            <!-- Вкладка 5: Магазин -->
            <div id="tab-shop" class="tab-content space-y-3">
                <div class="bg-slate-800/90 p-5 rounded-3xl card-glow space-y-3 text-xs">
                    <h2 class="text-sm font-bold text-amber-400 text-center">🛒 Магазин Лиги</h2>
                    
                    <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-700 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-200 block">🔴 Poké Ball (Поимка)</span>
                            <span class="text-[10px] text-slate-400">В наличии: {{ user[7] }} шт.</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=pokeball" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 font-bold rounded-lg text-white">50 🪙</a>
                    </div>

                    <div class="bg-purple-950/40 p-3 rounded-xl border border-purple-500/50 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-purple-300 block">⭐ Мастер-Болл (Гарант Shiny)</span>
                            <span class="text-[10px] text-purple-200">100% поимка редкого покемона</span>
                        </div>
                        <a href="/buy?user_id={{ user[0] }}&item=masterball" class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 font-bold rounded-lg text-white">5 ⭐</a>
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

        // Автоматически подставляем спрайты покемонов из PokeAPI по имени
        const starterName = "{{ user[2] if user else '' }}";
        const starterIds = { "Bulbasaur": 1, "Charmander": 4, "Squirtle": 7 };
        if (starterName && starterIds[starterName]) {
            const spriteUrl = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${starterIds[starterName]}.png`;
            const sImg = document.getElementById('starter-img');
            const sbImg = document.getElementById('starter-box-img');
            if(sImg) sImg.src = spriteUrl;
            if(sbImg) sbImg.src = spriteUrl;
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
async def index(request: Request, user_id: int = 12345, message: str = None, battle_msg: str = None):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
        collection = []
        if user:
            async with db.execute("SELECT * FROM collection WHERE user_id = ?", (user_id,)) as cursor:
                raw_col = await cursor.fetchall()
                # Добавляем ID покемона для красивого вывода картинок спрайтов
                for row in raw_col:
                    p_name = row[2]
                    p_id = POKEMON_IDS.get(p_name, 25)
                    collection.append(row + (p_id,))
            
    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(request=request, user=user, collection=collection, message=message, battle_msg=battle_msg)
    return HTMLResponse(content=rendered_html)

@app.get("/register")
async def register(user_id: int, username: str = "Тренер", starter: str = "Bulbasaur"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, starter, level, exp, hp, max_hp, pokeballs, masterballs, coins, stars) VALUES (?, ?, ?, 1, 0, 100, 100, 5, 1, 150, 10)",
            (user_id, username, starter)
        )
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/explore")
async def explore(user_id: int, loc: str):
    msg = "Вы ничего не нашли..."
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT pokeballs FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] > 0:
                if loc == "forest":
                    pool = [("Pikachu", "Редкий"), ("Pidgey", "Обычный"), ("Bulbasaur", "Обычный")]
                else:
                    pool = [("Mewtwo", "Легендарный"), ("Zubat", "Обычный"), ("Diglett", "Редкий"), ("Geodude", "Редкий")]
                
                chosen, rarity = random.choice(pool)
                is_shiny = 1 if random.random() < (0.15 if loc == "cave" else 0.05) else 0

                await db.execute("UPDATE users SET pokeballs = pokeballs - 1 WHERE user_id = ?", (user_id,))
                await db.execute("INSERT INTO collection (user_id, pokemon_name, rarity, is_shiny, level, hp) VALUES (?, ?, ?, ?, 1, 50)", 
                                 (user_id, chosen, rarity, is_shiny))
                await db.commit()
                
                shiny_text = "✨ SHINY " if is_shiny else ""
                msg = f"Успех! Вы поймали покемона: {shiny_text}{chosen} ({rarity})!"
            else:
                msg = "Недостаточно Poké Balls! Купите их в магазине."
                
    return RedirectResponse(url=f"/?user_id={user_id}&message={msg}", status_code=303)

@app.get("/battle")
async def battle(user_id: int):
    battle_msg = ""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT exp, level FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            if user:
                exp, lvl = user[0], user[1]
                exp += 35
                if exp >= 100:
                    lvl += 1
                    exp = 0
                    battle_msg = f"🏆 Победа! Ваш уровень повысился до {lvl} уровня и получено +30 🪙!"
                else:
                    battle_msg = f"⚔️ Победа в бою! Получено +35 XP и +30 🪙."
                
                await db.execute("UPDATE users SET exp = ?, level = ?, coins = coins + 30 WHERE user_id = ?", (exp, lvl, user_id))
                await db.commit()
                
    return RedirectResponse(url=f"/?user_id={user_id}&battle_msg={battle_msg}", status_code=303)

@app.get("/buy")
async def buy(user_id: int, item: str):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT coins, stars FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                coins, stars = row[0], row[1]
                if item == "pokeball" and coins >= 50:
                    await db.execute("UPDATE users SET coins = coins - 50, pokeballs = pokeballs + 1 WHERE user_id = ?", (user_id,))
                    await db.commit()
                elif item == "masterball" and stars >= 5:
                    await db.execute("UPDATE users SET stars = stars - 5, masterballs = masterballs + 1 WHERE user_id = ?", (user_id,))
                    await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000)
