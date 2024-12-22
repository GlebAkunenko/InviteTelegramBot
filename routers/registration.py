import html

from aiogram import Bot, Router, types, html, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

import keyboards
from bot import bot
from keyboards import confirm, InfoCallback

from models import User
from routers.help import command_help_handler

router = Router()

class RegistrationStates(StatesGroup):
    wait_name = State()
    wait_confirm = State()

cache = {}

@router.message(RegistrationStates.wait_name)
async def set_name(message: types.Message, state: FSMContext):
    nickname = message.text
    telegram_id = message.from_user.id
    cache[telegram_id] = message.text
    await bot.send_message(telegram_id, f"Ваше имя: {html.bold(nickname)}?", reply_markup=confirm())
    await state.set_state(RegistrationStates.wait_confirm)

@router.message(RegistrationStates.wait_confirm)
async def confirm_name(message: types.Message, state: FSMContext):
    text = message.text.lower()
    telegram_id = message.from_user.id
    if text == "да":
        user = User.get(User.telegram_id == telegram_id)
        user.nickname = cache[telegram_id]
        del cache[telegram_id]
        user.save()
        await state.set_state(None)
        await bot.send_message(telegram_id, "Подтверждено", reply_markup=ReplyKeyboardRemove())
        await command_help_handler(message)
    elif text == "нет":
        await bot.send_message(telegram_id, "Напиши ещё раз имя", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.wait_name)
    else:
        await bot.send_message(telegram_id, "Напиши да/нет")


@router.callback_query(keyboards.InfoCallback.filter(F.command == 'skip'))
async def skip_empty_button(query: types.CallbackQuery):
    await query.answer()

@router.callback_query(keyboards.InfoCallback.filter(F.command == 'canc ren'))
async def cancel_rename(query: types.CallbackQuery, state: FSMContext):
    telegram_id = query.from_user.id
    await state.set_state(None)
    await bot.send_message(
        telegram_id,
        "Окей. Оставим как есть"
    )
    await query.answer()

