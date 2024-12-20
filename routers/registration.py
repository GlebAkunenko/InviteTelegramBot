import html

from aiogram import Bot, Router, types, html, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

import keyboards
from bot import bot
from keyboards import confirm, InfoCallback

from models import User

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
    elif text == "нет":
        await bot.send_message(telegram_id, "Напиши ещё раз имя", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.wait_name)
    else:
        await bot.send_message(telegram_id, "Напиши да/нет")


@router.callback_query(keyboards.InfoCallback.filter(F.command == 'skip'))
async def skip_empty_button(query: types.CallbackQuery):
    await query.answer()

# @router.callback_query(ConfirmCallbackData.filter(F.command == 'reg1'))
# async def handle_button_click(query: CallbackQuery, state: FSMContext):
#     data = ConfirmCallbackData.unpack(query.data)
#     if data.body == 'yes':
#         user = User.get(User.telegram_id == query.from_user.id)
#         user.nickname = cache[query.from_user.id]
#         del cache[query.from_user.id]
#         user.save()
#         await state.set_state(None)
#         await bot.send_message(query.from_user.id, "Подтверждено")
#     elif data.body == 'no':
#         await bot.send_message(query.from_user.id, "Напиши ещё раз имя")
#         await state.set_state(RegistrationStates.wait_name)
#     await bot.delete_message(query.from_user.id, query.message.message_id)