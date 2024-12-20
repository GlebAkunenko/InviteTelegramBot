import os

import dotenv
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

dotenv.load_dotenv()

bot = Bot(token=os.getenv('token'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
