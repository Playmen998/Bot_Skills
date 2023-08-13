from aiogram import  types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from DataBase import task_db
from create_bot import bot
from keyboards import kb, adminKB
import re
from aiogram.types import ReplyKeyboardRemove
#from keyboards_inline.admin import adminKB

START = """
<b>Добро пожаловать.
Выберите один из пунктов</b>

🖊 Отметить достижения:  /note
📊 Получить статистику:  /stat
📝 Описание целей и бота:  /goal
⚒ Администрирование:  /admin
⏱ Уведомления: /notify
"""

GOAL = """
<b>SkillsBot</b> - является ботом, который может: 
✅ Отслеживать прогресс профессиональных навыков, как hard, так и soft skills
🖊 Добавлять и изменять навыки/цели, которые вы развиваете 
📊 Получить подробную статистику за любое время в виде графика или таблицы
📝 Редактировать и изменять свои записи
⏱ Отправлять уведомления

Как работает бот:
Чтобы начать пользоваться ботом нужно:
1. Создать задания по команде /add
   - Указать название задания
   - Ввести минимальный и максимальный балл
   - Дать описание задания
2. Выбрать задание для отслеживания по команде\n /show_tasks
3. Чтобы отслеживать свой ежедневный прогресс введите команду /note
4. Получить подробную статистику по команде /stat

● Также есть возможность удалять задания и последние записанные результаты в команде /admin
● Чтобы отменить любую команду введите /cancel

Чтобы получить описание целей нажмите команду /descrip

Также в боте реализован функционал отправка уведомлений, через команду /notify
Присутствует возможность отправлять сообщения в разные временные периоды

PS: Если вы вели неправильно данные или сделали это несколько раз, то просто удалите последнюю запись выбранного задания 

Чтобы вернуться в главное меню нажмите /start
"""




async def start_command(message : types.Message):
    'Команда start'
    await bot.send_message(chat_id=message.from_user.id,
                           text=START,
                           reply_markup=kb,
                           parse_mode='html')

async def bot_description(message : types.Message):
    'Команда goal'
    await bot.send_message(chat_id=message.from_user.id,
                           text=GOAL,
                           reply_markup=types.ReplyKeyboardRemove(),
                           parse_mode='html')

class FSMAdmin_descripGoal(StatesGroup):
    goal = State()


async def choose_goal_description(message : types.Message):
    'Вводим номер задания для того чтобы получить его описание'
    string = task_db.all_tasks()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Введите номер задания, чтобы получить описание:\n{string}\n'
                           )
    await FSMAdmin_descripGoal.goal.set()

async def goal_description(message : types.Message, state: FSMContext):
    'Получаем описание задания из БД'
    global CHOOSE_TASKS_DESCRIP
    s = message.text
    nums = re.findall(r'\d+', s)
    text = task_db.sql_et_descrip_task(nums)
    string = f"""
Задание: {text[0][1]}
Описание: {text[0][2]}
Минимальный балл: {text[0][3]}
Максимальный балл: {text[0][4]}

Чтобы вернуться в главное меню нажмите: /start
              """
    await bot.send_message(chat_id=message.from_user.id,
                           text=string)
    await state.finish()

async def echo_command(message : types.Message):
    await message.answer(text = 'Чтобы использовать бота нажмите /start')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(bot_description, commands=['goal'])
    dp.register_message_handler(choose_goal_description, commands=['descrip'])
    dp.register_message_handler(goal_description, state=FSMAdmin_descripGoal.goal)
    dp.register_message_handler(echo_command)