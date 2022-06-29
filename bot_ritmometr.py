from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db
from handlers import client, general


async def on_startup(_):
    print('Bot is online')
    sqlite_db.sql_start()


client.register_client_handlers(dp)
general.register_general_handlers(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
