import datetime as dt
from enum import Enum
from models import Computer, Reservation, Club


class Status(Enum):
    free = 'free'
    work = 'work'
    lite_res = 'lite_res' # the reservation is after 3+ hours
    hard_res = 'hard_res' # the reservation is soon
    broken = 'broken'


def get_computer_status(computer: Computer, reservations: list[Reservation]) -> Status:
    if computer.is_broken:
        return Status.broken
    elif computer.is_work:
        return Status.work
    elif len(reservations) == 0:
        return Status.free
    else:
        now = dt.datetime.now()
        times = [(r.start - now).seconds / 60 / 60 for r in reservations]
        next_reservation = min(times)
        if next_reservation > 7:
            return Status.free
        elif next_reservation > 3:
            return Status.lite_res
        else:
            return Status.hard_res


