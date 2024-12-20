from peewee import Model, CharField, ForeignKeyField, IntegerField, AutoField, DateTimeField, BooleanField
from peewee import MySQLDatabase
from dotenv import load_dotenv
import os
import datetime as dt

load_dotenv()

# Подключаемся к базе данных MySQL
db = MySQLDatabase(
    os.getenv("database_name"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    host=os.getenv("host"),
    port=int(os.getenv("port")),
)

def initialize_db():
    if not db.connect():
        print("Ошибка подключения к базе данных")
    db.create_tables([User, Club, Room, Computer, Reservation])  # Создаём все таблицы


# Модель для пользователей
class User(Model):
    telegram_id = IntegerField(unique=True)  # chat_id для Telegram
    nickname = CharField(null=True)  # Никнейм пользователя
    role = IntegerField(default=0)

    def is_admin(self):
        return self.role == 1

    class Meta:
        database = db  # Указываем базу данных, с которой работаем

# Модель для клубов
class Club(Model):
    name = CharField(max_length=32)  # Название клуба
    address = CharField(max_length=64)  # Адрес клуба

    class Meta:
        database = db  # Указываем базу данных, с которой работаем

# Модель для комнат в клубах
class Room(Model):
    id = AutoField(primary_key=True)
    club = ForeignKeyField(Club, backref='rooms')  # Внешний ключ к клубу
    name = CharField(max_length=32)  # Название комнаты

    class Meta:
        database = db  # Указываем базу данных, с которой работаем

# Модель для компьютеров в комнатах
class Computer(Model):
    id = AutoField(primary_key=True)
    room = ForeignKeyField(Room, backref='computers')  # Внешний ключ к комнате
    num = IntegerField()  # Номер компьютера в комнате
    stack = IntegerField()
    is_work = BooleanField(default=False)
    is_broken = BooleanField(default=False)

    class Meta:
        database = db  # Указываем базу данных, с которой работаем


class Reservation(Model):
    computer = ForeignKeyField(Computer, backref='reservations')
    user = ForeignKeyField(User, backref='reservations')
    start = DateTimeField(null=False)

    class Meta:
        database = db


initialize_db()