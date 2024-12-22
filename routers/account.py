from aiogram import Router, types, html, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards, commands
from bot import bot
from keyboards import confirm, InfoCallback

from models import User
from routers import RegistrationStates

router = Router()

@router.message(commands.rename.command)
@router.message(F.text.casefold() == commands.rename.text_equivalent.casefold())
async def rename(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = User.get(telegram_id=telegram_id)
    if not user:
        await bot.send_message(telegram_id, f"Напиши {html.code('/start')}")
    else:
        await bot.send_message(telegram_id, f"Напиши новое имя", reply_markup=keyboards.cancel_rename())
        await state.set_state(RegistrationStates.wait_name)