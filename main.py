import asyncio
import logging
import sys

from aiogram import Dispatcher, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from models import *
from bot import bot
from routers import RegistrationStates, registration, reservation

dp = Dispatcher()
dp.include_router(registration)
dp.include_router(reservation)

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    user, created = User.get_or_create(telegram_id=telegram_id)
    if created:
        await bot.send_message(user.telegram_id, f"Это бот компьютерного клуба {html.code('/invite')}. Напиши своё имя чтобы, я тебя узнавал")
        await state.set_state(RegistrationStates.wait_name)
        user.save()


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    print("Bot has started")