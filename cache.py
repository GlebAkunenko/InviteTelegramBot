import datetime as dt

from models import Computer, Reservation, Club, Room
from rules import Status, get_computer_status

class ComputerReservation:
    def __init__(self, club: Club):
        self.club = club
        self.last_update = dt.datetime.now()
        self.__computers: list[Computer] = Computer.select()
        self.__all_reservations: list[Reservation] = (
            Reservation
            .select()
            .join(Computer)
            .join(Room)
            .where(
                (Reservation.start > self.last_update) &
                (Room.club == self.club)
            ))
        self.__reservations: dict[int, list[Reservation]] = {}
        self.__free_computers: list[Computer] = []
        for computer in self.__computers:
            self.__reservations[computer.id] = [r for r in self.__all_reservations if r.computer == computer]
            if get_computer_status(computer, self.__reservations[computer.id]) == Status.free:
                self.__free_computers.append(computer)


    def update_info(self):
        self.last_update = dt.datetime.now()
        self.__computers: list[Computer] = Computer.select()
        self.__all_reservations: list[Reservation] = (
            Reservation
            .select()
            .join(Computer)
            .join(Room)
            .where(
                (Reservation.start > self.last_update) &
                (Room.club == self.club)
            ))
        self.__reservations = {}
        self.__free_computers: list[Computer] = []
        for computer in self.__computers:
            self.__reservations[computer.id] = [r for r in self.__all_reservations if r.computer == computer]
            if get_computer_status(computer, self.__reservations[computer.id]) == Status.free:
                self.__free_computers.append(computer)

    def try_to_update(self):
        if dt.datetime.now() + dt.timedelta(seconds=1) > self.last_update:
            self.update_info()

    @property
    def computers(self) -> list[Computer]:
        self.try_to_update()
        return self.__computers

    @property
    def reservations(self) -> dict[int, list[Reservation]]:
        self.try_to_update()
        return self.__reservations

    @property
    def all_reservations(self) -> list[Reservation]:
        self.try_to_update()
        return self.__all_reservations

    @property
    def free_computers(self) -> list[Computer]:
        self.try_to_update()
        return self.__free_computers