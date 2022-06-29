from aiogram import types, Dispatcher

import config
from create_bot import dp, bot
from data_base.sqlite_db import sql_add_command
from keyboards import kb_client, instrument_types, only_find, dalshe, menu_kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db


class FSMClient(StatesGroup):
    nick = State()
    instrument = State()
    mp3 = State()


# @dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    config.number_mp = 0
    await bot.send_message(message.from_user.id,
                           'Привет!👋🏻 Ты👤 хочешь💫 найти🔍 музыканта🥁 или загрузить📮 музыкальное🎷 портфолио🗂, '
                           'чтобы нашли🔎 тебя👤?',
                           reply_markup=kb_client)


# @dp.message_handler(commands='add_portfolio', state=None)
async def add_portfolio_command(message: types.Message):
    await FSMClient.instrument.set()
    await bot.send_message(message.from_user.id, 'Выберите✅ группу👩🏻‍🤝‍👨🏼 инструментов🥁',
                           reply_markup=instrument_types)


# @dp.message_handler(content_types=['instrument'], state=FSMClient.instrument)
async def load_instrument(message: types.Message, state: FSMContext):
    if message.text in ['Ударные🥁', 'Струнные🎸', 'Духовые🎷', 'Вокал🎤', 'Другое🪗']:
        instrument_types.clean()
        async with state.proxy() as data:
            data['nick'] = message.from_user.username
            data['instrument'] = message.text
        await FSMClient.next()
        await bot.send_message(message.from_user.id, "Добавь📮 файл mp3🎶", reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=FSMClient.mp3)
async def load_mp3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.content_type == 'audio':
            data['mp3'] = message.audio.file_id
        elif message.content_type == 'voice':
            data['mp3'] = message.voice.file_id
    await sql_add_command(state)
    # async with state.proxy() as data:
    #     await message.reply(str(data))
    await state.finish()
    await bot.send_message(message.from_user.id, 'Идем дальше...', reply_markup=only_find)


# @dp.message_handler(commands=['find_musician'])
async def find_musician_command(message: types.Message):
    await bot.send_message(message.from_user.id, 'Выберите✅ кого вы хотите найти👩🏻‍', reply_markup=instrument_types)
    await message.delete()


@dp.message_handler(lambda message: message.text in ['Ударные🥁', 'Струнные🎸', 'Духовые🎷', 'Вокал🎤', 'Другое🪗'])
async def start_listening(message: types.Message):
    config.number_mp = 0
    config.cur_instrument = message.text
    await sqlite_db.sql_read(config.number_mp, message)
    # await bot.send_message(message.from_user.id, 'Оцените...', reply_markup=vote_kb)
    config.number_mp += 1


async def make_match(message: types.Message):
    await bot.send_message(message.from_user.id, config.cur_username, reply_markup=dalshe)


async def next_voice(message: types.Message):
    await sqlite_db.sql_read(config.number_mp, message)
    config.number_mp += 1


async def menu(message: types.Message):
    await bot.send_message(message.from_user.id, 'Меню', reply_markup=menu_kb)


async def delete_data(message: types.Message):
    await sqlite_db.sql_delete(message)


async def reload(message: types.Message):
    config.number_mp = 0
    await bot.send_message(message.from_user.id,
                           'Привет!👋🏻 Ты👤 хочешь💫 найти🔍 музыканта🥁 или загрузить📮 музыкальное🎷 портфолио🗂, '
                           'чтобы нашли🔎 тебя👤?',
                           reply_markup=kb_client)


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(add_portfolio_command, Text(equals="Добавить📮портфолио🗂"), state=None)
    dp.register_message_handler(find_musician_command, Text(equals="Я👤 хочу🤍 найти🔎 музыканта🎻"))
    dp.register_message_handler(load_instrument, state=FSMClient.instrument)
    dp.register_message_handler(load_mp3, content_types=[types.ContentType.VOICE, types.ContentType.AUDIO],
                                state=FSMClient.mp3)
    dp.register_message_handler(make_match, Text(equals="Понравилось🔥"))
    dp.register_message_handler(next_voice, Text(equals="Идем🚶🏻 дальше▶️"))
    dp.register_message_handler(menu, Text(equals="Перейти🚶🏻 в меню📱"))
    dp.register_message_handler(delete_data, Text(equals="Удалить🗑 свои👤 данные📇"))
    dp.register_message_handler(reload, Text(equals="Перезапустить 🔄бот📱"))
