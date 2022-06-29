import sqlite3 as sq

import config
from create_bot import bot
from keyboards import vote_kb, all_listened, kb_client
from aiogram import types


def sql_start():
    global base, cur
    base = sq.connect('ritmometr.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS users(nick TEXT, instrument TEXT, mp3 TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(num, message):
    # print(cur.execute(f'SELECT nick, instrument, mp3 FROM users WHERE instrument="{config.cur_instrument}"').arraysize)
    print(config.cur_instrument)
    if num < cur.execute(f'SELECT nick, instrument, mp3 FROM users WHERE instrument="{config.cur_instrument}"').arraysize:
        res = cur.execute(f'SELECT nick, instrument, mp3 FROM users WHERE instrument="{config.cur_instrument}"').fetchall()
        print(res)
        await bot.send_audio(message.from_user.id, res[config.number_mp][2], reply_markup=vote_kb)
        config.cur_username = res[num][0]
    else:
        await bot.send_message(message.from_user.id, 'Кажется вы всех прослушали...', reply_markup=all_listened)


async def sql_delete(message: types.Message):
    cur.execute(f'DELETE FROM users WHERE nick="{message.from_user.username}"')
    base.commit()
    await bot.send_message(message.from_user.id, 'Данные успешно удалены', reply_markup=kb_client)
