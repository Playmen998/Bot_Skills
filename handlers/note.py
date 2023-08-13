from aiogram import  types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from handlers import admin
from datetime import date
from DataBase import task_db, resalt_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re


global dict_num
"""
Глобальная переменная для записи баллов, которые вводит пользователь
Значения перезаписываются при получение баллов для следующего задания
"""
dict_num = {}

class FSMAdmin_save(StatesGroup):
    save1 = State()
    save2 = State()
    save3 = State()
    save4 = State()
    save5 = State()


def get_inline_keyboard(name, string):
    'Функция, которая создает инлайн клавиатуру'
    score = ['❶','❷','❸','❹','❺','❻','❼','❽','❾','❿','⓫','⓬','⓭','⓮','⓯','⓰','⓱','⓲','⓳','⓴']
    markup = InlineKeyboardMarkup(row_width=3)
    button_row = []
    for i in range(0, name[1]):
        "Условные операторы нужны, чтобы можно было создать клавиатуру не больше, чем 3 значения в ряд"
        button = InlineKeyboardButton(text=score[i], callback_data=string + '_' +name[0] + '_' + str(i + 1))
        button_row.append(button)
        if len(button_row) == 3:

            markup.add(button_row[0], button_row[1], button_row[2])
            button_row = []
        elif i == name[1] - 1:
            if len(button_row) == 2:
                markup.add(button_row[0], button_row[1])
                button_row = []
            else:
                markup.add(button)
    return markup

async def note_command(message : types.Message):
    'Запуск по команде /note - всего для оценки доступно максимум 5 заданий'
    global name, id
    try:
        name, id = task_db.sort_tasks(admin.save_data()) #Получем выбранные задания

        await bot.send_message(text=f"Оцените задание: {name[0][0]}", chat_id=message.from_user.id, reply_markup=get_inline_keyboard(name[0], 'first'))
    except:
        await bot.send_message(chat_id=message.from_user.id, text="Чтобы выбрать задания нажмите команду /show_tasks")

async def first_task_callback(callback : types.CallbackQuery):
    'Обработка первого задания'
    s = callback.data
    nums = re.findall(r'\d+', s) #находим числа из str
    dict_num['id'] = id[0][0]
    dict_num['Задание'] = name[0][0]
    dict_num['Балл'] = int(nums[0])
    dict_num['Дата'] = date.today()
    await resalt_db.sql_add_command(dict_num) #добавляем баллы пользователя в БД
    await callback.answer()
    try:
        await callback.message.answer(text=f"Оцените задание: {name[1][0]}", reply_markup=get_inline_keyboard(name[1], 'second'))
    except:
        await callback.message.answer(text=f"Вы оценили все задания\nЧтобы вернуться в главное меню нажмите: /start")


async def second_task_handler(callback : types.CallbackQuery):
    'Обработка второго задания'
    s = callback.data
    nums = re.findall(r'\d+', s)
    dict_num['id'] = id[1][0]
    dict_num['Задание'] = name[1][0]
    dict_num['Балл'] = int(nums[0])
    dict_num['Дата'] = date.today()
    "Отсылаем сразу в БД"
    await resalt_db.sql_add_command(dict_num)
    await callback.answer()
    try:
        await callback.message.answer(text=f"Оцените задание: {name[2][0]}",
                                  reply_markup=get_inline_keyboard(name[2], 'third'))
    except:
        await callback.message.answer(text=f"Вы оценили все задания\nЧтобы вернуться в главное меню нажмите: /start")

async def third_task_handler(callback : types.CallbackQuery):
    'Обработка третьего задания'
    s = callback.data
    nums = re.findall(r'\d+', s)
    dict_num['id'] = id[2][0]
    dict_num['Задание'] = name[2][0]
    dict_num['Балл'] = int(nums[0])
    dict_num['Дата'] = date.today()
    "Отсылаем сразу в БД"
    await resalt_db.sql_add_command(dict_num)
    await callback.answer()
    try:
        await callback.message.answer(text=f"Оцените задание: {name[3][0]}",
                                  reply_markup=get_inline_keyboard(name[3], 'fourth'))
    except:
        await callback.message.answer(text=f"Вы оценили все задания\nЧтобы вернуться в главное меню нажмите: /start")

async def fourth_task_handler(callback : types.CallbackQuery):
    'Обработка четвертого задания'
    s = callback.data
    nums = re.findall(r'\d+', s)
    dict_num['id'] = id[3][0]
    dict_num['Задание'] = name[3][0]
    dict_num['Балл'] = int(nums[0])
    dict_num['Дата'] = date.today()
    "Отсылаем сразу в БД"
    await resalt_db.sql_add_command(dict_num)
    await callback.answer()
    try:
        await callback.message.answer(text=f"Оцените задание: {name[4][0]}",
                                  reply_markup=get_inline_keyboard(name[4], 'fifth'))
    except:
        await callback.message.answer(text=f"Вы оценили все задания\nЧтобы вернуться в главное меню нажмите: /start")

async def fifth_task_handler(callback : types.CallbackQuery):
    'Обработка пятого задания'
    s = callback.data
    nums = re.findall(r'\d+', s)
    dict_num['id'] = id[4][0]
    dict_num['Задание'] = name[4][0]
    dict_num['Балл'] = int(nums[0])
    dict_num['Дата'] = date.today()
    "Отсылаем сразу в БД"
    await resalt_db.sql_add_command(dict_num)
    await callback.answer()
    await callback.message.answer(text=f"Вы оценили все задания на сегодня!\nЧтобы вернуться в главное меню нажмите: /start")



def register_handlers_note(dp: Dispatcher):
    dp.register_message_handler(note_command, commands=['note'])
    dp.register_callback_query_handler(first_task_callback, lambda callback_query: callback_query.data.startswith('first'))
    dp.register_callback_query_handler(second_task_handler, lambda callback_query: callback_query.data.startswith('second'))
    dp.register_callback_query_handler(third_task_handler, lambda callback_query: callback_query.data.startswith('third'))
    dp.register_callback_query_handler(fourth_task_handler, lambda callback_query: callback_query.data.startswith('fourth'))
    dp.register_callback_query_handler(fifth_task_handler, lambda callback_query: callback_query.data.startswith('fifth'))