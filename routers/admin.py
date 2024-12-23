from aiogram.filters import Command
from aiogram import F

import keyboards
from models import Room, User, Club, Computer
from bot import bot

from aiogram import types, Router

router = Router()

cache = dict()
admins: list[User] = list(User.select().where(User.role > 0))
print(admins)
club = Club.get(id=1)

def get_admin_message(telegram_id: int, room: Room) -> tuple[int, int] | None:
    by_admin = cache.get(telegram_id)
    if by_admin:
        result = by_admin.get(room.id)
        if result:
            return result
    return None


async def update_information(room: Room):
    state = keyboards.room_status(room)
    for admin in admins:
        message = get_admin_message(admin.telegram_id, room)
        if message:
            try:
                chat_id, message_id = message
                await bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=state
                )
            except Exception:
               await bot.send_message(admin.telegram_id, text=room.name, reply_markup=state)



@router.message(Command('rooms'))
async def get_rooms(message: types.Message):
    user = User.get(telegram_id=message.from_user.id)
    if user.role < 1:
        await message.answer("Кто тебе рассказал про эту команду?")
        return
    rooms = Room.select().where(Room.club == club)
    chat_id = message.chat.id
    telegram_id = message.from_user.id
    for room in rooms:
        message = await bot.send_message(chat_id=chat_id, text=room.name, reply_markup=keyboards.room_status(room))
        if telegram_id not in cache:
            cache[telegram_id] = {room.id: (chat_id, message.message_id)}
        else:
            cache[telegram_id][room.id] = (chat_id, message.message_id)


@router.callback_query(keyboards.AdminCallBack.filter(F.computer > 0))
async def update_state(query: types.CallbackQuery):
    unit = keyboards.AdminCallBack.unpack(query.data).computer
    computer: Computer = Computer.get(id=unit)
    computer.is_work = not computer.is_work
    computer.save()
    await update_information(computer.room)