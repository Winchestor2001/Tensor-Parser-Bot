from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.crud import get_all_telegram_ids
from loader import ADMINS


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMINS or message.from_user.id in await get_all_telegram_ids()
