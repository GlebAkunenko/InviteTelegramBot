from aiogram import Bot, Router, types, html, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from bot import bot

from models import *
from cache import ComputerReservation
import views, keyboards
import re

from rules import Status

router = Router()

cache = {}
computer_reservation = ComputerReservation(Club.get(id=1))

class ReservationStates(StatesGroup):
    wait_time = State()
    wait_confirm = State()

def can_make_reservation(text: str) -> bool:
    return text.count(views.status_symbol[Status.free]) > 0

@router.message(Command("now"))
@router.message(F.text.casefold() == 'Сейчас')
async def get_club_info(message: types.Message):
    club = Club.get(id=1)
    telegram_id = message.from_user.id
    text = views.get_club_info(club)
    await bot.send_message(telegram_id, text, reply_markup=keyboards.club_info(can_make_reservation(text)))


@router.callback_query(keyboards.InfoCallback.filter(F.command == "upd"))
async def update_club_info(query: CallbackQuery):
    club = Club.get(id=1)
    new_text = views.get_club_info(club)

    chat_id = query.message.chat.id
    message_id = query.message.message_id
    await bot.edit_message_text(new_text, chat_id=chat_id, message_id=message_id)
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboards.club_info(can_make_reservation(new_text)))
    await query.answer()


@router.callback_query(keyboards.InfoCallback.filter(F.command == "res"))
async def choose_room(query: CallbackQuery):
    telegram_id = query.from_user.id
    free_computers = computer_reservation.free_computers
    rooms = {c.room for c in free_computers}
    rooms = list(rooms)
    rooms.sort(key=lambda r: r.id)
    if len(rooms) == 0:
        await query.answer("К сожалению свободных мест не осталось")
        return
    await bot.send_message(
        telegram_id,
        "Выберите зал в котором хотите забронировать компьютер",
        reply_markup=keyboards.rooms(rooms)
    )
    await query.answer()


@router.callback_query(keyboards.ReservationCallback.filter(F.state == 'room'))
async def choose_computer(query: CallbackQuery):
    room = keyboards.ReservationCallback.unpack(query.data).room
    computers = [
        computer
        for computer in computer_reservation.free_computers
        if computer.room.id == room
    ]
    if len(computers) == 0:
        await query.answer("К сожалению свободных мест не осталось")
        return
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    await bot.edit_message_text(
        "Выбери номер компьютера",
        chat_id=chat_id,
        message_id=message_id
    )
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboards.computers(computers)
    )
    await query.answer()


@router.callback_query(keyboards.ReservationCallback.filter(F.state == 'comp'))
async def choose_time(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    data = keyboards.ReservationCallback.unpack(query.data)
    cache[query.from_user.id] = (data.room, data.comp)
    await bot.edit_message_text(
        "Напиши время брони. Можешь написать час в 24-часовом формате или указать точное время (например 16:30)",
        chat_id=chat_id,
        message_id=message_id
    )
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboards.cancel()
    )
    await state.set_state(ReservationStates.wait_time)
    await query.answer()


@router.callback_query(keyboards.ReservationCallback.filter(F.state == 'cancel'))
async def choose_time(query: CallbackQuery):
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    await bot.edit_message_text(
        "Действие отменено",
        chat_id=chat_id,
        message_id=message_id
    )
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None
    )
    await query.answer()


@router.message(ReservationStates.wait_time)
async def book_computer(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    text = message.text
    if re.match("[0-9]{2}:[0-9]{2}", text):
        h, m = map(int, text.split(":"))
    elif re.match("^[0-9]{1,2}$", text):
        h = int(text)
        m = 0
    else:
        await bot.send_message(telegram_id, "Неверный формат времени. Напиши на какой час регистрировать бронь. Например 15")
        return
    if 0 <= h <= 23 and 0 <= m <= 59:
        time = dt.time(h, m)
        now = dt.datetime.now()
        date = dt.datetime(now.year, now.month, now.day, time.hour, time.minute)
        room, computer = cache[telegram_id]
        user = User.get(telegram_id=message.from_user.id)
        request = Reservation(
            computer=computer,
            user=user,
            start=date
        )
        cache[telegram_id] = request
        await state.set_state(ReservationStates.wait_confirm)
        await bot.send_message(telegram_id, views.confirm_reservation(request), reply_markup=keyboards.confirm())
    else:
        await bot.send_message(telegram_id, "Указано некорректное время")
        return


@router.message(ReservationStates.wait_confirm)
async def confirm_name(message: types.Message, state: FSMContext):
    text = message.text.lower()
    telegram_id = message.from_user.id
    if text == "да":
        request = cache[telegram_id]
        reservations = (Reservation
                        .select()
                        .where(
                            Reservation.computer == request.computer &
                            Reservation.start > dt.datetime.now()))
        if len(list(reservations)) != 0:
            del cache[telegram_id]
            await state.set_state(None)
            await bot.send_message(telegram_id,
                                   "К сожалению ты не успел. Кто-то другой забронировал этот компьютер быстрее тебя(",
                                   reply_markup=ReplyKeyboardRemove())
        else:
            request.save()
            await bot.send_message(telegram_id, "Бронь подтверждена", reply_markup=ReplyKeyboardRemove())
    elif text == "нет":
        del cache[telegram_id]
        await state.set_state(None)
        await bot.send_message(telegram_id, "Бронь отменена", reply_markup=ReplyKeyboardRemove())
    else:
        await bot.send_message(telegram_id, "Напиши да/нет")

# @router.callback_query(keyboards.ReservationCallback.filter(F.state == 'comp'))
# async def book_computer(query: CallbackQuery):
#     id = keyboards.ReservationCallback.unpack(query.data).data
#     computer = Computer.get(id=id)
#     Reservation.create(
#         computer=computer,
#
#     )