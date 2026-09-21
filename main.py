import os
import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8628464354:AAEQ0XKfv9OR-CR368dSaXq6tQsipn_Wy7w"
DOMAIN = "bot-1790032438-3286-prokudin95.bothost.tech"

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

DB_FILE = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'") as cursor:
            table_exists = await cursor.fetchone()
        
        if not table_exists:
            await db.execute("""
                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    starter TEXT,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    hp INTEGER DEFAULT 100
                )
            """)
            await db.commit()

@app.on_event("startup")
async def startup_event():
    await init_db()
    asyncio.create_task(dp.start_polling(bot))

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    web_app_url = f"https://{DOMAIN}"
    builder.button(text="🎮 Открыть игру (Mini App)", web_app=types.WebAppInfo(url=web_app_url))
    
    await message.answer(
        "👋 Добро пожаловать в мир Pokémon!\n\nНажми кнопку ниже, чтобы запустить игру, выбрать своего первого покемона и начать путешествие:",
        reply_markup=builder.as_markup()
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pokémon Mini App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .card-glow {
            box-shadow: 0 0 20px rgba(129, 140, 248, 0.2);
            border: 1px solid rgba(129, 140, 248, 0.3);
        }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-4">

    <header class="flex justify-between items-center bg-slate-800/60 backdrop-blur-md p-4 rounded-2xl card-glow">
        <div>
            <h1 class="font-bold text-lg text-indigo-400">⚡ Лига Тренеров</h1>
            <p class="text-xs text-slate-400" id="tg-username">Игрок Telegram</p>
        </div>
        <div class="bg-indigo-600/30 px-3 py-1 rounded-full border border-indigo-500/50 text-xs font-semibold text-indigo-300">
            MVP Версия
        </div>
    </header>

    <main class="my-auto py-6">
        {% if not user %}
            <div class="bg-slate-800/80 backdrop-blur-md p-6 rounded-3xl card-glow text-center">
                <h2 class="text-2xl font-black mb-2 text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">Выбери своего первого Pokémon!</h2>
                <p class="text-sm text-slate-300 mb-6">С этого верного спутника начнется твое грандиозное путешествие.</p>
                
                <form action="/register" method="GET" class="space-y-4">
                    <input type="hidden" name="user_id" id="input_user_id" value="12345">
                    <input type="hidden" name="username" id="input_username" value="Trainer">

                    <div class="grid grid-cols-3 gap-3">
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Bulbasaur" class="peer hidden" checked>
                            <div class="p-3 bg-slate-900/80 rounded-2xl border border-slate-700 peer-checked:border-emerald-500 peer-checked:bg-emerald-950/30 transition">
                                <div class="text-3xl mb-1">🌱</div>
                                <div class="text-xs font-bold text-emerald-400">Бульбазавр</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Charmander" class="peer hidden">
                            <div class="p-3 bg-slate-900/80 rounded-2xl border border-slate-700 peer-checked:border-orange-500 peer-checked:bg-orange-950/30 transition">
                                <div class="text-3xl mb-1">🔥</div>
                                <div class="text-xs font-bold text-orange-400">Чармандер</div>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="starter" value="Squirtle" class="peer hidden">
                            <div class="p-3 bg-slate-900/80 rounded-2xl border border-slate-700 peer-checked:border-blue-500 peer-checked:bg-blue-950/30 transition">
                                <div class="text-3xl mb-1">💧</div>
                                <div class="text-xs font-bold text-blue-400">Сквиртл</div>
                            </div>
                        </label>
                    </div>

                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 font-bold rounded-xl shadow-lg shadow-indigo-500/35 transition transform active:scale-95">
                        Начать приключение! 🚀
                    </button>
                </form>
            </div>
        {% else %}
            <div class="bg-slate-800/80 backdrop-blur-md p-6 rounded-3xl card-glow text-center space-y-4">
                <div class="inline-block p-4 bg-indigo-500/10 rounded-full border border-indigo-500/30 text-5xl mb-2">
                    {% if user[2] == 'Charmander' %}🔥{% elif user[2] == 'Squirtle' %}💧{% else %}🌱{% endif %}
                </div>
                <h2 class="text-xl font-bold text-indigo-200">Твой покемон: <span class="text-yellow-400">{{ user[2] }}</span></h2>
                
                <div class="grid grid-cols-3 gap-2 bg-slate-900/60 p-3 rounded-2xl text-center text-xs">
                    <div>
                        <span class="text-slate-400 block">Уровень</span>
                        <span class="font-bold text-base text-indigo-400">{{ user[3] }}</span>
                    </div>
                    <div>
                        <span class="text-slate-400 block">Опыт</span>
                        <span class="font-bold text-base text-emerald-400">{{ user[4] }}</span>
                    </div>
                    <div>
                        <span class="text-slate-400 block">Здоровье</span>
                        <span class="font-bold text-base text-rose-400">{{ user[5] }} HP</span>
                    </div>
                </div>

                <div class="p-3 bg-slate-900/40 rounded-xl border border-slate-700/50 text-xs text-slate-300">
                    ✨ База данных успешно подключена! Все данные твоего тренера надежно сохраняются.
                </div>
            </div>
        {% endif %}
    </main>

    <nav class="grid grid-cols-4 gap-2 bg-slate-800/80 backdrop-blur-md p-2 rounded-2xl card-glow text-center text-xs">
        <a href="#" class="p-2 bg-indigo-600/30 text-indigo-300 rounded-xl font-bold">🗺️ Карта</a>
        <a href="#" class="p-2 text-slate-400 hover:text-white transition">🎒 Инвентарь</a>
        <a href="#" class="p-2 text-slate-400 hover:text-white transition">⚔️ Бой</a>
        <a href="#" class="p-2 text-slate-400 hover:text-white transition">👤 Профиль</a>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            const user = tg.initDataUnsafe.user;
            document.getElementById('tg-username').innerText = '@' + (user.username || user.first_name);
            document.getElementById('input_user_id').value = user.id;
            document.getElementById('input_username').value = user.first_name;
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
            
    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(request=request, user=user)
    return HTMLResponse(content=rendered_html)

@app.get("/register")
async def register(user_id: int, username: str = "Тренер", starter: str = "Bulbasaur"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, starter, level, exp, hp) VALUES (?, ?, ?, 1, 0, 100)",
            (user_id, username, starter)
        )
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    # Запускаем на порту 3000, который ждет Bothost
    uvicorn.run("main:app", host="0.0.0.0", port=3000)
