from create_bot import bot
from aiogram import  types,Dispatcher

from handlers import admin
from keyboards import statKB, tableKB, chartKB
from DataBase import resalt_db, task_db
from prettytable import PrettyTable
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import pandas as pd
import matplotlib.pyplot as plt
import re

NOTE = """
<b>Выберете пункт:</b>
●Получить график результатов:  /show_chart
●Получить таблицу результатов:  /show_table
"""

TABLE = """
<b>Выберете пункт:</b>
●Получить результаты по заданию за весь период: /all_dateT
●Получить результаты по заданию за выбранный период: /choose_dateT
"""

CHART = """
<b>Выберете пункт:</b>
●Получить результаты за весь период: /all_dateC
●Получить результаты за выбранный период: /choose_dateC
"""




async def note_command(message : types.Message):
    "Начало команды /stat"
    await bot.send_message(chat_id=message.from_user.id,
                           text=NOTE,
                           parse_mode='html',
                           reply_markup=statKB)

"""
================================
=======Обработка Таблицы========
================================
"""

class FSMTable_dateAll(StatesGroup):
    num = State()


async def table_command(message : types.Message):
    "Выбор или за весь период или за определенный"
    await bot.send_message(chat_id=message.from_user.id,
                           text = TABLE,
                           parse_mode='html',
                           reply_markup=tableKB)


async def table_choose_task(message : types.Message):
    "Выбор задания, когда выбран весь период"
    string = task_db.all_tasks()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберете номер задание:\n{string}',
                           reply_markup=types.ReplyKeyboardRemove()
                           )
    await FSMTable_dateAll.num.set()

async def all_get_table_command(message: types.Message, state: FSMContext):
    "Вывод таблицы, когда выбран весь период"
    s = message.text
    nums = re.findall(r'\d+', s) #выделение из текста цифр
    nums = [int(i) for i in nums]
    "Обработка таблицы"
    result = resalt_db.get_table_name(nums[0])
    table = PrettyTable()
    table.field_names = ['Задание', 'Оценка', 'Дата']
    for i in result:
        table.add_row(list(i[1:]))
    response = '```\n{}```'.format(table.get_string())
    await bot.send_message(chat_id=message.from_user.id,
                           text='Таблица за весь период')
    await bot.send_message(chat_id=message.from_user.id,
                           text=response,
                           parse_mode="Markdown")
    await bot.send_message(chat_id=message.from_user.id,
                           text='Чтобы вернуться в главное меню нажмите: /start')
    await state.finish()

class FSMTable_date(StatesGroup):
    num = State()
    mindate = State()
    maxdate = State()

async def table_choose_task_date(message : types.Message):
    "Вывод таблицы, за нужный период"
    string = task_db.all_tasks()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберете номер задание:\n{string}',
                           reply_markup=types.ReplyKeyboardRemove()
                           )
    await FSMTable_date.num.set()

async def choose_get_table_command(message : types.Message, state: FSMContext):
    "Ввод минимальную дату"
    s = message.text
    nums = re.findall(r'\d+', s)
    nums = [int(i) for i in nums]
    async with state.proxy() as data:
        data['num'] = int(nums[0])

    await bot.send_message(chat_id=message.from_user.id,
                           text="Введите минимальную дату в формате '2023-07-20'")
    await FSMTable_date.next()

async def get_min_date(message : types.Message, state: FSMContext):
    "Ввод максимальную дату"
    async with state.proxy() as data:
        data['mindate'] = str(message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Введите максимальную дату в формате '2023-07-20'")
    await FSMTable_date.next()


async def get_max_date(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['maxdate'] = str(message.text)
    result = resalt_db.choose_table(data) #получаем данные из БД
    if not result:
        await bot.send_message(chat_id=message.from_user.id,
                               text='За данный период нет данных\nВведите другой диапазон через команду /choose_dateT\nВернуться в главное меню /start'
                               )
        await state.finish()
    else:
        table = PrettyTable()
        table.field_names = ['Задание', 'Оценка', 'Дата']
        for i in result:
            table.add_row(list(i[1:]))
        response = '```\n{}```'.format(table.get_string())
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Таблица за период {data['mindate']}-{data['maxdate']}"
                               )
        await bot.send_message(chat_id=message.from_user.id,
                               text=response,
                               parse_mode="Markdown")
        await bot.send_message(chat_id=message.from_user.id,
                               text='Чтобы вернуться в главное меню нажмите: /start')
        await state.finish()


"""
================================
=======Обработка Графика========
================================
"""

class FSMChart_date(StatesGroup):
    mindate = State()
    maxdate = State()

def get_cumulative_mean(df):
    "Обработка таблицы из БД"
    list_name = df['name'].unique()
    main = pd.DataFrame()
    for i in list_name:
        mid_tab = df[df['name'] == i].reset_index()
        add_tab = pd.concat([mid_tab,pd.DataFrame({'score_mean' : mid_tab['score'].expanding().mean().to_list()})],axis = 1)
        #Идет подсчет накопительного среднего функция expanding
        main = pd.concat([main, add_tab])
    return main

async def chart_command(message : types.Message):
    "Выбор или за весь период или за определенный"
    await bot.send_message(chat_id=message.from_user.id,
                           text = CHART,
                           parse_mode='html',
                           reply_markup=chartKB)

async def all_get_chart_command(message : types.Message):
    "Отправляем график с данными по заданиям за весь период"
    result = resalt_db.get_all_table(admin.save_data())
    """
    Сюда передаются задания в БД через функцию admin.save_data() те таски, которые мы выбрали
    по команде /show_tasks
    """
    df = pd.DataFrame(result, columns=['id', 'name', 'score', 'date'])
    svod_tab = get_cumulative_mean(df) #Получение накопительного среднего

    fig, ax = plt.subplots(figsize=(14, 8))
    "Построение графика, чтобы потом его отослать"
    svod_tab['date'] = pd.to_datetime(svod_tab["date"], errors='coerce')
    list_name = svod_tab['name'].unique()
    legend = []

    for name in list_name:
        plt.plot(svod_tab.query(f"name == '{name}'").groupby(['date'])['score_mean'].sum(), marker='o', markersize=4,
                 linewidth=2)
        legend.append(name)

        svod = svod_tab.query(f"name == '{name}'").groupby(['date'])['score_mean'].sum().reset_index().values
        for ind in range(0,len(svod),3):
            ax.text(svod[ind][0], svod[ind][1], round(svod[ind][1], 2), size=8,fontweight = 'semibold')
    plt.legend(legend, fontsize="medium")
    plt.grid(linewidth=0.5)
    ax.set_title(f'График накопительного среднего', fontsize=13)
    plt.savefig('my_plot.png', bbox_inches='tight')
    file = open('my_plot.png', 'rb')
    await bot.send_message(chat_id=message.from_user.id,
                           text = 'График за весь период',
                           reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(message.from_user.id,file)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Чтобы вернуться в главное меню нажмите: /start')

async def choose_get_chart_command(message : types.Message):
    "Вводим минимальную дату"
    await bot.send_message(chat_id=message.from_user.id,
                           text="Введите минимальную дату в формате '2023-07-20'",
                           reply_markup=types.ReplyKeyboardRemove())
    await FSMChart_date.mindate.set()

async def get_min_date_chart(message : types.Message, state: FSMContext):
    "Вводим максимальную дату"
    async with state.proxy() as data:
        data['mindate'] = str(message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Введите максимальную дату в формате '2023-07-20'")
    await FSMChart_date.next()

async def get_max_date_chart(message : types.Message, state: FSMContext):
    "Отправляем график с данными по заданиям за выбранный период"
    async with state.proxy() as data:
        data['maxdate'] = str(message.text)
        data['num'] = admin.save_data()
    result = resalt_db.choose_chart(data)
    if not result:
        await bot.send_message(chat_id=message.from_user.id,
                               text='За данный период нет данных\nВведите другой диапазон через команду /choose_dateC\nВернуться в главное меню /start'
                               )
        await state.finish()
    else:
        df = pd.DataFrame(result, columns=['id', 'name', 'score', 'date'])
        svod_tab = get_cumulative_mean(df)
        fig, ax = plt.subplots(figsize=(14, 8))

        svod_tab['date'] = pd.to_datetime(svod_tab["date"], errors='coerce')
        list_name = svod_tab['name'].unique()
        legend = []

        for name in list_name:
            plt.plot(svod_tab.query(f"name == '{name}'").groupby(['date'])['score_mean'].sum(), marker='o', markersize=4,
                     linewidth=2)
            legend.append(name)

            svod = svod_tab.query(f"name == '{name}'").groupby(['date'])['score_mean'].sum().reset_index().values
            for ind in range(0,len(svod),3):
                ax.text(svod[ind][0], svod[ind][1] + 0.5, round(svod[ind][1], 2), size=8,fontweight = 'semibold')

        plt.legend(legend, fontsize="medium")
        plt.grid(linewidth=0.5)
        ax.set_title(f'График накопительного среднего', fontsize=13)
        plt.savefig('my_plot.png', bbox_inches='tight')
        file = open('my_plot.png', 'rb')
        await bot.send_message(chat_id=message.from_user.id,
                               text= f"График за период {data['mindate']}-{data['maxdate']}"
                               )
        await bot.send_photo(message.from_user.id, file)
        await bot.send_message(chat_id=message.from_user.id,
                               text='Чтобы вернуться в главное меню нажмите: /start')
        await state.finish()


def register_handlers_stat(dp: Dispatcher):
    dp.register_message_handler(note_command, commands=['stat'])

    #Таблицы
    dp.register_message_handler(table_command, commands=['show_table'])
    #Весь период
    dp.register_message_handler(table_choose_task, commands=['all_dateT'], state = "*")
    dp.register_message_handler(all_get_table_command, state=FSMTable_dateAll.num)
    #Выбранный период
    dp.register_message_handler(table_choose_task_date, commands=['choose_dateT'], state = "*")
    dp.register_message_handler(choose_get_table_command, state=FSMTable_date.num)
    dp.register_message_handler(get_min_date, state=FSMTable_date.mindate)
    dp.register_message_handler(get_max_date, state=FSMTable_date.maxdate)
    #Графики
    dp.register_message_handler(chart_command, commands=['show_chart'])
    dp.register_message_handler(all_get_chart_command, commands=['all_dateC'])
    dp.register_message_handler(choose_get_chart_command, commands=['choose_dateC'], state = "*")
    dp.register_message_handler(get_min_date_chart, state=FSMChart_date.mindate)
    dp.register_message_handler(get_max_date_chart, state=FSMChart_date.maxdate)