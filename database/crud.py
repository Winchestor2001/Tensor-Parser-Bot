import uuid

from database.models import TelegramUser, InviteCode, db


async def create_user(telegram_id: int, username: str | None = None):
    TelegramUser.create(telegram_id=telegram_id, username=username)


async def create_invite_link(bot_username: str):
    invite_code = str(uuid.uuid4())[:5]
    InviteCode.create(code=invite_code)
    return f"https://t.me/{bot_username}?start={invite_code}"


async def get_all_telegram_ids():
    return [user.telegram_id for user in TelegramUser.select()]


async def check_invite_code(invite_code):
    return InviteCode.select().where(InviteCode.code == invite_code).exists()


async def delete_invite_code(invite_code):
    InviteCode.delete().where(InviteCode.code == invite_code).execute()

