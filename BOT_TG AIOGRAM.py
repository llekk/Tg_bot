import asyncio
import sqlite3
from datetime import datetime

import requests

from config import BOT_TOKEN, weather_token
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging
from aiogram import F, Router

router = Router()

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
star = []
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
clava = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Узнать погоду'), KeyboardButton(text='Help')],
    [KeyboardButton(text='Погода в любимом городе'), KeyboardButton(text='Установить любимый город')],
], resize_keyboard=True, input_field_placeholder='Выберите команду')
logger = logging.getLogger(__name__)
count = 0


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.username}, хочешь узнать погоду?', reply_markup=clava)


@dp.message(F.text == 'Узнать погоду')
async def weather(message: Message):
    await message.answer('Хорошо, чтобы узнать погоду напиши сообщение типа "/w <Название города>"')


@dp.message(F.text == 'Help')
async def help(message: Message):
    await message.answer(f'Бот-помощник определения погоды)')


@dp.message(F.text == 'Установить любимый город')
async def lsv_country(message: Message):
    await message.answer(f'Хорошо, чтобы установить любимый город, напиши сообщение типа "/nc <Название города>')


@dp.message(F.text == 'Погода в любимом городе')
async def lv_country(message: Message):
    smiles = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32B',
    }
    flag = True
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM login_id')
    users = cursor.fetchall()
    for i in users:
        if i[0] == message.from_user.id:
            re = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={i[1]}&appid={weather_token}&units=metric"
            )
            data = re.json()
            real_temp = round(data['main']['temp'])
            feel_temp = round(data['main']['feels_like'])
            now_time = str(datetime.now())[:19]
            country = data['sys']['country']
            sunrise = (str(datetime.fromtimestamp(data['sys']['sunrise'])))[11:]
            sunset = (str(datetime.fromtimestamp(data['sys']['sunset'])))[11:]
            wind = data['wind']['speed']
            if real_temp > 0:
                real_temp = f'+{real_temp}'
            if feel_temp > 0:
                feel_temp = f'+{feel_temp}'
            main_weather = data['weather'][0]['main']
            if main_weather in smiles:
                wsmile = smiles[main_weather]
            else:
                wsmile = 'Нипон'
            await message.answer(f"***{now_time}*** \n"
                                 f"Город:{i[1]} Страна:{country} \n"
                                 f"Погода: {wsmile} \n"
                                 f"Температура воздуха: {real_temp}°С \n"
                                 f"Ощущается как: {feel_temp}°С \n"
                                 f"Время рассвета: {sunrise} МСК\n"
                                 f"Время заката: {sunset} МСК\n"
                                 f"Скорость ветра: {wind} м/c \n"
                                 f"Хорошего дня! 🥰"
                                 )
            flag = False
    if flag:
        await message.answer('Ты еще не установил свой любимый город!')


@dp.message(Command('nc'))
async def love_country(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    if len(command.args.split()):
        name_love_country = ' '.join(command.args.split())
    if len(command.args.split()) > 1:
        name_love_country = ' '.join(command.args.split())

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
            id INTEGER, gorod TEXT
    )""")
    connect.commit()
    cursor.execute(f"SELECT id FROM login_id WHERE id = {message.from_user.id}")
    data = cursor.fetchone()
    if data is None:
        cursor.execute("INSERT INTO login_id VALUES(?, ?);", [message.from_user.id, name_love_country])
        connect.commit()
    else:
        cursor.execute(f"DELETE FROM login_id WHERE id = {message.from_user.id}")
        cursor.execute("INSERT INTO login_id VALUES(?, ?);", [message.from_user.id, name_love_country])
        connect.commit()
    await message.answer('Успешно!')


@dp.message(Command('w'))
async def tr(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    if len(command.args.split()):
        name_country = ''.join(command.args.split())
    if len(command.args.split()) > 1:
        name_country = ' '.join(command.args.split())
    smiles = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32B',
    }
    try:
        re = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={name_country}&appid={weather_token}&units=metric"
        )
        data = re.json()
        real_temp = round(data['main']['temp'])
        feel_temp = round(data['main']['feels_like'])
        now_time = str(datetime.now())[:19]
        country = data['sys']['country']
        sunrise = (str(datetime.fromtimestamp(data['sys']['sunrise'])))[11:]
        sunset = (str(datetime.fromtimestamp(data['sys']['sunset'])))[11:]
        wind = data['wind']['speed']
        if real_temp > 0:
            real_temp = f'+{real_temp}'
        if feel_temp > 0:
            feel_temp = f'+{feel_temp}'
        main_weather = data['weather'][0]['main']
        if main_weather in smiles:
            wsmile = smiles[main_weather]
        else:
            wsmile = 'Нипон'
        await message.answer(f"***{now_time}*** \n"
                             f"Город:{name_country} Страна:{country} \n"
                             f"Погода: {wsmile} \n"
                             f"Температура воздуха: {real_temp}°С \n"
                             f"Ощущается как: {feel_temp}°С \n"
                             f"Время рассвета: {sunrise} МСК\n"
                             f"Время заката: {sunset} МСК \n"
                             f"Скорость ветра: {wind} м/c \n"
                             f"Хорошего дня! 🥰"
                             )
    except:
        await message.answer('Вы ввели несуществующий город')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
