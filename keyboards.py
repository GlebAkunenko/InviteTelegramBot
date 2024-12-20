from sys import prefix

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from models import Room, Computer

class InfoCallback(CallbackData, prefix='i'):
    command: str

class ReservationCallback(CallbackData, prefix='r'):
    state: str
    room: int | None
    comp: int | None
    time: str | None

def confirm() -> ReplyKeyboardMarkup:
    button_yes = KeyboardButton(text="Да")
    button_no = KeyboardButton(text="Нет")
    return ReplyKeyboardMarkup(keyboard=[[button_yes, button_no]])


def club_info(can_make_reservation = True) -> InlineKeyboardMarkup:
    if can_make_reservation:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Забронировать', callback_data=InfoCallback(command='res').pack())],
            [InlineKeyboardButton(text='Обновить', callback_data=InfoCallback(command='upd').pack())],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Обновить', callback_data=InfoCallback(command='upd').pack())],
        ])


def cancel_reservation() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отменить бронь', callback_data=InfoCallback(command='unbook').pack())],
        [InlineKeyboardButton(text='Обновить', callback_data=InfoCallback(command='upd').pack())],
    ])

def rooms(rooms: list[Room]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=room.name,
            callback_data=ReservationCallback(
                state='room',
                room=room.id,
                comp=None,
                time=None)
            .pack())]
        for room in rooms
    ])

def computers(computers: list[Computer]) -> InlineKeyboardMarkup:
    n = len(computers)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            (InlineKeyboardButton(
                text=str(computers[row * 3 + i].num),
                callback_data=ReservationCallback(
                    state='comp',
                    room=computers[row * 3 + i].room.id,
                    comp=computers[row * 3 + i].id,
                    time=None
                ).pack()
            )
             if
                row * 3 + i < len(computers)
             else
                InlineKeyboardButton(text=" ", callback_data=InfoCallback(command='skip').pack()))
            for i in range(0, 3)
        ]
        for row in range(n // 3 + 1)
    ])


def cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Отмена',
            callback_data=ReservationCallback(
                state='cancel',
                room=None,
                comp=None,
                time=None
            ).pack())],
    ])