from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message

from bot import bot

import random

router = Router()

@router.message(Command('/invite'))
async def handle_invite(message: Message):
    replicas = [
        "Да да это я",
        "Я принимаю вызов",
        "Жду тебя в миду на сфах",
        "Что сидим? Кого ждём?"
    ]
    await bot.send_message(
        message.from_user.id,
        random.choice(replicas)
    )


@router.message(Command('/dnk test'))
async def how_is_an_author(message: Message):
    await bot.send_message(
        message.from_user.id,
        "Father: 100% @Gleb1000\nMother: ???"
    )