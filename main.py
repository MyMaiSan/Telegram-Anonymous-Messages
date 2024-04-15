from aiogram import Dispatcher, Bot
import asyncio
from config import API_TOKEN
from handlers.client import client, dp
from handlers.admin import admin
from database.db import DB

async def main():
    bot = Bot(API_TOKEN)
    dp.include_routers(client, admin)
    await DB.create()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
asyncio.run(main())