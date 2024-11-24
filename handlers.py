import os

from aiogram import types, F
from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, CommandObject, Command
from peewee import DoesNotExist

from database.crud import create_invite_link, check_invite_code, create_user
from filters import IsAdminFilter
from loader import bot
from parser import run_parse

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject):
    referral_code = command.args
    if referral_code:
        invite_code = await check_invite_code(invite_code=referral_code)

        if invite_code:
            await create_user(telegram_id=message.from_user.id, username=message.from_user.username)
            await message.answer("Вы успешно зарегистрированы через реферальный код!")


@router.message(Command("inv"))
async def invite_handler(message: types.Message):
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    invite_link = await create_invite_link(bot_username)
    await message.answer(invite_link)


@router.message(F.text.startswith("https://"), IsAdminFilter())
async def get_url_handler(message: types.Message):
    nft_name = message.text.split("/")[-1]
    user_id = message.from_user.id
    filename = f"{user_id}.pdf"
    wait_message = await message.answer("⏳")
    run_parse(telegram_id=user_id, nft_name=nft_name)
    await wait_message.delete()
    await message.reply_document(types.FSInputFile(filename))
    os.unlink(filename)
