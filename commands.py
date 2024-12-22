from aiogram.filters import Command

class MyCommand:
    def __init__(self, command: Command, text_equivalent: str):
        self.command = command
        self.text_equivalent = text_equivalent


club_info = MyCommand(Command('free'), "/свободные места")
rename = MyCommand(Command('rename'), "/смена имени")
help = MyCommand(Command('help'), '/справка')