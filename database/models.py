from peewee import (
    Model,
    CharField,
    IntegerField,
    DateTimeField,
    ForeignKeyField,
    SqliteDatabase,
    BooleanField
)
from datetime import datetime

db = SqliteDatabase('telegram_bot.db')


# Базовая модель для наследования
class BaseModel(Model):
    class Meta:
        database = db


# Модель TelegramUser
class TelegramUser(BaseModel):
    telegram_id = IntegerField(unique=True)  # Уникальный идентификатор Telegram пользователя
    username = CharField(null=True)  # Имя пользователя (может быть пустым)
    created_at = DateTimeField(default=datetime.now)  # Дата и время регистрации

    def __str__(self):
        return f"{self.telegram_id} - {self.username or 'No Username'}"


# Модель InviteCode
class InviteCode(BaseModel):
    code = CharField(unique=True)  # Уникальный инвайт-код
    created_at = DateTimeField(default=datetime.now)  # Дата и время создания кода

    def __str__(self):
        return f"InviteCode({self.code})"
