from aiogram import types, Dispatcher
from create_bot import dp


# @dp.message_handler()
async def echo_send(message: types.Message):
    await message.answer('Такой команды нет(')


# await message.reply(message.text)
# await bot.send_message(message.from_user.id, message.text)

def register_general_handlers(dp: Dispatcher):
    dp.register_message_handler(echo_send)
