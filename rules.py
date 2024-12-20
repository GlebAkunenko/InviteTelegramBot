import datetime as dt
from enum import Enum
from models import Computer, Reservation, Club, User


class Status(Enum):
    free = 'free'
    work = 'work'
    lite_res = 'lite_res' # the reservation is after 3+ hours
    hard_res = 'hard_res' # the reservation is soon
    broken = 'broken'
    your = 'your'


def get_computer_status(computer: Computer, reservations: list[Reservation], user: User | None = None) -> Status:
    if computer.is_broken:
        return Status.broken
    elif computer.is_work:
        return Status.work
    elif len(reservations) == 0:
        return Status.free
    else:
        now = dt.datetime.now()
        reservations.sort(key=lambda r: r.start)
        next_reservation = reservations[0]
        if user is not None and next_reservation.user == user:
            return Status.your
        time = (next_reservation.start - now).total_seconds() / 60 / 60
        if time > 7:
            return Status.free
        elif time > 3:
            return Status.lite_res
        else:
            return Status.hard_res


