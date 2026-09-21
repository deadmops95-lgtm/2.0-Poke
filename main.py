import os
import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8628464354:AAEQ0XKfv9OR-CR368dSaXq6tQsipn_Wy7w"
# Получаем домен от Bothost и гарантируем, что он безопасный (https)
RAW_DOMAIN = os.getenv("BOTHOUSE_DOMAIN", "localhost:8000")
DOMAIN = RAW_DOMAIN.replace("http://", "").replace("https://", "")

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_FILE = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER INTEGER PRIMARY KEY,
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
    # Жестко прописываем https:// для Telegram
    web_app_url = f"https://{DOMAIN}"
    builder.button(text="🎮 Открыть игру (Mini App)", web_app=types.WebAppInfo(url=web_app_url))
    
    await message.answer(
        "👋 Добро пожаловать в мир Pokémon!\n\nНажми кнопку ниже, чтобы запустить игру, выбрать своего первого покемона и начать путешествие:",
        reply_markup=builder.as_markup()
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int = 12345):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/register")
async def register(user_id: int, username: str = "Тренер", starter: str = "Bulbasaur"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, starter, level, exp, hp) VALUES (?, ?, ?, 1, 0, 100)",
            (user_id, username, starter)
        )
        await db.commit()
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
