from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from bot import bot

from models import *
from cache import ComputerReservation
import views, keyboards, commands
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

def has_reservation(user: User) -> bool:
    return user in computer_reservation.reservation.values()

@router.message(commands.club_info.command)
@router.message(F.text.casefold() == commands.club_info.text_equivalent.casefold())
async def get_club_info(message: types.Message):
    club = Club.get(id=1)
    telegram_id = message.from_user.id
    user: User = User.get(telegram_id=telegram_id)
    if not user.disable_help:
        await bot.send_message(telegram_id, views.club_info_help(), reply_markup=keyboards.block_help())
    text = views.get_club_info(club, user)
    if has_reservation(user):
        await bot.send_message(telegram_id, text, reply_markup=keyboards.cancel_reservation())
    else:
        await bot.send_message(telegram_id, text, reply_markup=keyboards.club_info(can_make_reservation(text)))


@router.callback_query(keyboards.InfoCallback.filter(F.command == "upd"))
async def update_club_info(query: CallbackQuery):
    club = Club.get(id=1)
    user = User.get(telegram_id=query.from_user.id)
    new_text = views.get_club_info(club, user)

    chat_id = query.message.chat.id
    message_id = query.message.message_id
    await bot.edit_message_text(new_text, chat_id=chat_id, message_id=message_id)
    if has_reservation(user):
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboards.cancel_reservation())
    else:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboards.club_info(can_make_reservation(new_text)))
    await query.answer()


@router.callback_query(keyboards.InfoCallback.filter(F.command == "unbook"))
async def unbook(query: CallbackQuery):
    telegram_id = query.from_user.id
    user = User.get(telegram_id=telegram_id)
    arr = [
        reservation
        for reservation in computer_reservation.all_reservations
        if reservation.user == user
    ]
    if len(arr) == 0:
        await query.answer("Уже неактуально")
    else:
        Reservation.delete().where(Reservation.user == user).execute()
        await update_club_info(query)


@router.callback_query(keyboards.InfoCallback.filter(F.command == "res"))
async def choose_room(query: CallbackQuery):
    telegram_id = query.from_user.id
    user = User.get(telegram_id=telegram_id)
    free_computers = computer_reservation.free_computers
    rooms = {c.room for c in free_computers}
    rooms = list(rooms)
    rooms.sort(key=lambda r: r.id)
    if len(rooms) == 0:
        await query.answer("К сожалению свободных мест не осталось")
        return
    if has_reservation(user):
        await query.answer("Вы уже забронировали 1 компьютер")
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
        reply_markup=keyboards.cancel_reservation()
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
    if re.match("[0-9]{1,2}:[0-9]{2}", text):
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
        if time < now.time():
            date += dt.timedelta(days=1)
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


@router.callback_query(keyboards.InfoCallback.filter(F.command == 'block'))
async def disable_help(query: CallbackQuery):
    telegram_id = query.from_user.id
    user: User = User.get(telegram_id=telegram_id)
    user.disable_help = True
    user.save()
    await query.answer("Для включения справки напиши /справка")