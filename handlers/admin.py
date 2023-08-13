from aiogram import  types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from datetime import date
from DataBase import task_db, resalt_db
from keyboards import adminKB
import time
import re




def save_data():
    "Функция для передачи данных"
    x = CHOOSE_TASKS
    return x




ADMIN = """
<b>Выберете пункт:</b>
●Выбрать задания:  /show_tasks
●Добавить задания:  /add
●Удалить выбранное задания:\n/delete_task
●Удалить последнюю запись результатов:  /delete_res
"""


"""
============= Команды админа ============
"""

async def admin_command(message : types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=ADMIN,
                           parse_mode='html',
                           reply_markup=adminKB)


"""
============= Машинное состояние - выбор заданий ============
"""

class FSMAdmin_choiceTask(StatesGroup):
    string = State()


async def show_tasks(message : types.Message):
    string = task_db.all_tasks()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Задания, которые доступны для выбора:\n{string}\nВыберете не больше 5',
                           reply_markup=types.ReplyKeyboardRemove()
                           )
    time.sleep(1)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Укажите номера заданий из списка через пробел')
    await FSMAdmin_choiceTask.string.set()

async def save_numTasks(message: types.Message, state: FSMContext):
    global CHOOSE_TASKS
    s = message.text
    nums = re.findall(r'\d+', s)
    nums = [int(i) for i in nums]
    async with state.proxy() as data:
        CHOOSE_TASKS = nums
    text = ''
    for i in CHOOSE_TASKS:
        text += str(i) + ' '
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Вы выбрали задания: {text}')
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Чтобы вернуться в главное меню нажмите: /start')
    await state.finish()
    return CHOOSE_TASKS

    
"""
============= Машинное состояние - добавлений новых заданий ============
"""

class FSMAdmin_addTask(StatesGroup):
    name = State()
    score_min = State()
    score_max = State()
    descrip = State()


async def add_command(message : types.Message, state: FSMContext):
    global NAME, CANCEL
    CANCEL = await bot.send_message(chat_id=message.from_user.id,
                           text='Для отмены нажмите /cancel в любой момент')
    NAME = await bot.send_message(chat_id=message.from_user.id,
                           text='Введите названия задания:',
                           reply_markup=types.ReplyKeyboardRemove())
    await FSMAdmin_addTask.name.set()


async def add_name(message : types.Message, state: FSMContext):
    global SCORE_MIN
    async with state.proxy() as data:
        data['name'] = message.text
        await FSMAdmin_addTask.name.set()
    SCORE_MIN = await message.answer(text='Введите минимальный балл:')
    await FSMAdmin_addTask.next()

async def add_score_min(message : types.Message, state: FSMContext):
    global SCORE_MAX
    if message.text.isdigit():
        async with state.proxy() as data:
            data['score_min'] = message.text
            await FSMAdmin_addTask.score_min.set()
        SCORE_MAX = await message.answer(text='Введите максимальный балл:')
        await message.answer(text='Максимальный балл может быть не больше 20!')
        await FSMAdmin_addTask.next()
    else:
        await message.answer('Введите целое число')

async def add_score_max(message : types.Message, state: FSMContext):
    global DESCRIP
    if message.text.isdigit():
        async with state.proxy() as data:
            data['score_max'] = message.text
            await FSMAdmin_addTask.score_max.set()
        DESCRIP = await message.answer(text='Введите описание задания:')
        await FSMAdmin_addTask.next()
    else:
        await message.answer('Введите целое число')

async def add_description(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['descrip'] = message.text
        await FSMAdmin_addTask.descrip.set()
    await message.answer(text='Данные успешно сохранены\nЧтобы вернуться в главное меню нажмите /start')
    async with state.proxy() as data:
        data['date'] = date.today()
    await task_db.sql_add_command(state)
    await state.finish()

async def cancel_command(message : types.Message, state: FSMContext):
    'Отмена машинного состояние по команде /cancel'
    current_state = await state.get_state()
    if current_state is None:
        return
    else:
        await state.finish()
        if "NAME" in globals():
            await NAME.delete()
        if 'SCORE_MIN' in globals():
            await SCORE_MIN.delete()
        if 'SCORE_MAX' in globals():
            await SCORE_MAX.delete()
        if 'DESCRIP' in globals():
            await DESCRIP.delete()
        await message.answer('✅ <b>Вы отменили команду</b>', parse_mode='html')


"""
============= Машинное состояние - удаление заданий ============
"""

class FSMAdmin_DeleteTasks(StatesGroup):
    string = State()

async def admin_delete_task(message : types.Message):
    string = task_db.all_tasks()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберете номер задания для удаления:\n{string}',
                           reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'<b>Внимание!</b> при удаление задания нельзя будет получить статистику!',
                           parse_mode='html'
                           )
    time.sleep(1)
    await FSMAdmin_DeleteTasks.string.set()


async def delete_task(message: types.Message, state: FSMContext):
    s = message.text
    nums = re.findall(r'\d+', s)
    nums = [int(i) for i in nums]
    await task_db.sql_delete_task_command(message, nums[0])
    await state.finish()

"""
============= Машинное состояние - удаление последних записей ============
"""

class FSMAdmin_DeleteNote(StatesGroup):
    string = State()


async def delete_task_note(message : types.Message):
    string = task_db.all_tasks()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Выберете номер задание:\n{string}',
                           reply_markup=types.ReplyKeyboardRemove())
    await FSMAdmin_DeleteNote.string.set()

async def delete_note(message: types.Message, state: FSMContext):

    s = message.text
    nums = re.findall(r'\d+', s)
    nums = [int(i) for i in nums]
    await resalt_db.sql_delete_note_command(message, nums[0])
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    #Команды админа
    dp.register_message_handler(admin_command, commands=['admin'])

    #Добавление заданий
    dp.register_message_handler(show_tasks, commands=['show_tasks'], state='*')
    dp.register_message_handler(save_numTasks, state=FSMAdmin_choiceTask.string)
    dp.register_message_handler(cancel_command, commands=['cancel'], state='*')
    dp.register_message_handler(add_command, commands=['add'], state='*')
    dp.register_message_handler(add_name, state=FSMAdmin_addTask.name)
    dp.register_message_handler(add_score_min, state=FSMAdmin_addTask.score_min)
    dp.register_message_handler(add_score_max, state=FSMAdmin_addTask.score_max)
    dp.register_message_handler(add_description, state=FSMAdmin_addTask.descrip)

    # Удаление заданий
    dp.register_message_handler(admin_delete_task, commands=['delete_task'])
    dp.register_message_handler(delete_task, state=FSMAdmin_DeleteTasks.string)

    # Удаление записей
    dp.register_message_handler(delete_task_note, commands=['delete_res'], state='*')
    dp.register_message_handler(delete_note, state=FSMAdmin_DeleteNote.string)