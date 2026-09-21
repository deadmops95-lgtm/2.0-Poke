import os
import aiosqlite
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен твоего бота (Bothost сам передает его через переменные окружения, либо можно указать здесь)
TOKEN = os.getenv("BOT_TOKEN", "ТВОЙ_ТОКЕН_БОТА")
DOMAIN = os.getenv("BOTHOUSE_DOMAIN", "http://localhost:8000") # Bothost автоматически заменит домен

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_FILE = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
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

# Команда /start в боте
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Ссылка на Mini App, которая откроет наш сайт прямо в Telegram
    web_app_url = f"https://{DOMAIN}" if "http" not in DOMAIN else DOMAIN
    builder.button(text="🎮 Открыть игру (Mini App)", web_app=types.WebAppInfo(url=web_app_url))
    
    await message.answer(
        "👋 Добро пожаловать в мир Pokémon!\n\nНажми кнопку ниже, чтобы запустить игру, выбрать своего первого покемона и начать путешествие:",
        reply_markup=builder.as_markup()
    )

# Главная страница Mini App (интерфейс игры)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int = 12345): # Для теста берем заглушку user_id
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# Регистрация и выбор стартовика
@app.post("/register")
async def register(user_id: int = Form(...), username: int = Form(...), starter: str = Form(...)):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, starter, level, exp, hp) VALUES (?, ?, ?, 1, 0, 100)",
            (user_id, "Тренер", starter)
        )
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

# Запуск бота в фоне при старте FastAPI
@app.on_event("startup")
async def on_startup():
    import asyncio
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
