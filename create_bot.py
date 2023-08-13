from aiogram import Bot
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv

"Создание бота"

storage = MemoryStorage()

load_dotenv(find_dotenv())

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
