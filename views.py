import datetime as dt
from aiogram import html
from models import *
from rules import get_computer_status, Status
from cache import ComputerReservation, Status

status_symbol = {
    Status.free: '🟢',
    Status.lite_res: '🟡',
    Status.hard_res: '🟠',
    Status.work: '🔴',
    Status.broken: '⚫️',
    Status.your: '🔵',
}

computer_reservation = ComputerReservation(Club.get(id=1))

def _get_computer_info(computer: Computer, sender: User) -> str:
    if computer.num > 9:
        number = f"№{html.code(computer.num)}"
    else:
        number = f"№{html.code(f'0{computer.num}')}"
    reservations: list[Reservation] = computer_reservation.reservations[computer.id]
    status = status_symbol[get_computer_status(computer, reservations, sender)]
    return f"{number} {status}"


def _get_room_info(room: Room, sender: User):
    computers = [c for c in room.computers]
    columns = {}
    for computer in computers:
        if computer.stack in columns:
            columns[computer.stack].append(computer)
        else:
            columns[computer.stack] = [computer]
    result = f"{html.bold(room.name)}\n"
    rows = []
    for i in range(max((len(columns[c]) for c in columns))):
        row: list[Computer] = []
        for c in columns:
            if i < len(columns[c]):
                row.append(columns[c][i])
        rows.append(row)
    for row in rows:
        result += "   ".join([_get_computer_info(comp, sender) for comp in row]) + "\n"
    return result


def get_club_info(club: Club, sender: User) -> str:
    rooms = Room.select().where(Room.club == club)
    return "\n".join([_get_room_info(room, sender) for room in rooms])


def confirm_reservation(request: Reservation) -> str:
    return (f"Бронь компьютера №{html.code(request.computer.num)}\n"
            f"в {request.computer.room.name}\n"
            f"на {request.start.strftime("%d.%m.%Y %H:%M")}\n"
            f"Верно?")