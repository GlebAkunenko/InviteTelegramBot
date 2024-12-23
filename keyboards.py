from math import ceil
from sys import prefix

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

import commands
from models import Room, Computer


class InfoCallback(CallbackData, prefix='i'):
    command: str


class AdminCallBack(CallbackData, prefix='a'):
    computer: int


class ReservationCallback(CallbackData, prefix='r'):
    state: str
    room: int | None
    comp: int | None
    time: str | None


def confirm() -> ReplyKeyboardMarkup:
    button_yes = KeyboardButton(text="Да")
    button_no = KeyboardButton(text="Нет")
    return ReplyKeyboardMarkup(keyboard=[[button_yes, button_no]], resize_keyboard=True, one_time_keyboard=True)


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


def club_info_reservated() -> InlineKeyboardMarkup:
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


def cancel_reservation() -> InlineKeyboardMarkup:
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

def cancel_rename() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Отмена',
            callback_data=InfoCallback(command='canc ren').pack())],
    ])


def menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=commands.club_info.text_equivalent)],
        [KeyboardButton(text=commands.rename.text_equivalent)],
    ], resize_keyboard=True)


def block_help() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Больше не показывать", callback_data=InfoCallback(command='block').pack())],
    ])


def room_status(room: Room) -> InlineKeyboardMarkup:
    def button(computer: Computer) -> InlineKeyboardButton:
        status = "🔴" if computer.is_work else "🟢"
        if computer.is_broken:
            status = "⚫️"
        return InlineKeyboardButton(
            text=f'№{0 if computer.num < 10 else ''}{computer.num} {status}',
            callback_data=AdminCallBack(computer=computer.id).pack()
        )
    computers = Computer.select().where(Computer.room == room)
    n = len(computers)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            (button(computers[row * 3 + i]) if row * 3 + i < len(computers)
             else InlineKeyboardButton(text=" ", callback_data=InfoCallback(command='skip').pack()))
            for i in range(0, 3)
        ]
        for row in range(ceil(n / 3))
    ])
