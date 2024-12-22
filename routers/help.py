import views, keyboards, commands
from bot import bot

from aiogram import Router, F
from aiogram.types import Message

from models import User

router = Router()

@router.message(commands.help.command)
@router.message(F.text.casefold() == commands.help.text_equivalent.casefold())
async def command_help_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    user: User = User.get(telegram_id=telegram_id)
    user.disable_help = False
    user.save()
    await bot.send_message(
        telegram_id,
        views.menu(),
        reply_markup=keyboards.menu()
    )

