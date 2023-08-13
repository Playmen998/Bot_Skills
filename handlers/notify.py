from create_bot import bot, dp
from aiogram import  types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class FSMAdmin_notify(StatesGroup):
    name_notify = State()


markup_notify = InlineKeyboardMarkup()

kb_notify1 = InlineKeyboardButton('Каждый день', callback_data='every_day')
kb_notify2 = InlineKeyboardButton('Каждый будний день', callback_data='every_weekday')
kb_notify3 = InlineKeyboardButton('Каждые выходные', callback_data='every_weekend')
kb_notify4 = InlineKeyboardButton('Каждую минуту', callback_data='every_minute')
kb_notify5 = InlineKeyboardButton('Каждые две минуты', callback_data='every_two_minute')
kb_notify6 = InlineKeyboardButton('Отменить все уведомления', callback_data='finish')
"Инлайн клавиатура для выбора периода для уведомлений"
markup_notify.add(kb_notify1).add(kb_notify2).add(kb_notify3).add(kb_notify4).add(kb_notify5).add(kb_notify6)


async def start_notify(message : types.Message):
    "Сообщения, которое будет отправлять уведомление"
    await bot.send_message(chat_id=message.from_user.id,
                           text='Напишите сообщения для уведомления',
                           reply_markup=types.ReplyKeyboardRemove()
                           )

    await FSMAdmin_notify.name_notify.set()


async def choose_notify_period(message : types.Message, state: FSMContext):
    "Выбираем периоды, как часто будут приходить уведомления"
    global TEXT_ANSWER, SELECT_PERIOD
    async with state.proxy() as data:
        TEXT_ANSWER = message.text
    SELECT_PERIOD = await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите один из вариантов повтора',
                           reply_markup=markup_notify
                           )
    await state.finish()

"Создание планировщика"
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
scheduler.start()

def delete_job(name):
    "Удаляет таски планировщика"
    scheduler.remove_job(f'{name}')

"""
У каждого колбэка есть свой id, которые принимают хэндлеры ниже
После обработки хэндлера создается временная задача
функция answer отправляет нужное сообщение
"""
async def callback_notify_every_day(callback : types.CallbackQuery):
    await callback.answer()
    scheduler.add_job(answer_notify_every_day, CronTrigger.from_crontab('0 12 * * *'), args=(dp,TEXT_ANSWER), id='every_day')
    await callback.message.answer(
        text=f"Уведомление будет приходить каждый день\nЧтобы вернуться в главное меню нажмите: /start")
async def answer_notify_every_day(callback : types.CallbackQuery, TEXT_ANSWER):
    await callback.message.answer(text= f'{TEXT_ANSWER}')


async def callback_notify_every_weekday(callback : types.CallbackQuery):
    await callback.answer()
    scheduler.add_job(answer_notify_every_day, CronTrigger.from_crontab('0 * * * 1-5'), args=(dp,TEXT_ANSWER), id='every_weekday')
    await callback.message.answer(
        text=f"Уведомление будет приходить каждый будний день\nЧтобы вернуться в главное меню нажмите: /start")
    await SELECT_PERIOD.delete()
async def answer_notify_every_weekday(callback : types.CallbackQuery, TEXT_ANSWER):
    await callback.message.answer(text= f'{TEXT_ANSWER}')


async def callback_notify_every_weekend(callback : types.CallbackQuery):
    await callback.answer()
    scheduler.add_job(answer_notify_every_day, CronTrigger.from_crontab('0 0 * * 6,0'), args=(callback,TEXT_ANSWER), id='every_weekend')
    await callback.message.answer(
        text=f"Уведомление будет приходить каждые выходные дни\nЧтобы вернуться в главное меню нажмите: /start")
    await SELECT_PERIOD.delete()
async def answer_notify_every_weekend(callback : types.CallbackQuery, TEXT_ANSWER):
    await callback.message.answer(text= f'{TEXT_ANSWER}')


async def callback_notify_every_minute(callback : types.CallbackQuery):
    await callback.answer()
    scheduler.add_job(answer_notify_every_minute, CronTrigger.from_crontab('* * * * *'), args=(callback,TEXT_ANSWER), id='every_minute')
    await callback.message.answer(
        text=f"Уведомление будет приходить каждую минуту\nЧтобы вернуться в главное меню нажмите: /start")
    await SELECT_PERIOD.delete()
async def answer_notify_every_minute(callback : types.CallbackQuery, TEXT_ANSWER):
    await callback.message.answer(text= f'{TEXT_ANSWER}')


async def callback_notify_every_two_minute(callback : types.CallbackQuery):
    await callback.answer()
    scheduler.add_job(answer_notify_every_two_minute, CronTrigger.from_crontab('*/2 * * * *'), args=(callback,TEXT_ANSWER), id='every_two_minute')
    await callback.message.answer(
        text=f"Уведомление будет приходить каждые две минуты\nЧтобы вернуться в главное меню нажмите: /start")
    await SELECT_PERIOD.delete()
async def answer_notify_every_two_minute(callback : types.CallbackQuery, TEXT_ANSWER):
    await callback.message.answer(text= f'{TEXT_ANSWER}')

async def callback_notify_finish(callback : types.CallbackQuery):
    "Отменяет все планировщики"
    await callback.answer()
    await SELECT_PERIOD.delete()
    try:
        scheduler.add_job(delete_job('every_day'), 'interval', seconds=1)
    except:
        try:
            scheduler.add_job(delete_job('every_weekday'), 'interval', seconds=1)
        except:
            try:
                scheduler.add_job(delete_job('every_weekend'), 'interval', seconds=1)
            except:
                try:
                    scheduler.add_job(delete_job('every_minute'), 'interval', seconds=1)
                except:
                    try:
                        scheduler.add_job(delete_job('every_two_minute'), 'interval', seconds=1)
                        await callback.message.answer(
                        text=f"Все уведомления выключены\nЧтобы вернуться в главное меню нажмите: /start")
                    except:
                        await callback.message.answer(
                        text=f"Все уведомления выключены\nЧтобы вернуться в главное меню нажмите: /start")


def register_handlers_notify(dp: Dispatcher):
    dp.register_message_handler(start_notify, commands=['notify'], state='*')
    dp.register_message_handler(choose_notify_period, state=FSMAdmin_notify.name_notify)

    dp.register_callback_query_handler(callback_notify_every_day, text = 'every_day')
    dp.register_callback_query_handler(answer_notify_every_day, text='every_day')

    dp.register_callback_query_handler(callback_notify_every_weekday, text='every_weekday')
    dp.register_callback_query_handler(answer_notify_every_weekday, text='every_weekday')

    dp.register_callback_query_handler(callback_notify_every_weekend, text='every_weekend')
    dp.register_callback_query_handler(answer_notify_every_weekend, text='every_weekend')

    dp.register_callback_query_handler(callback_notify_every_minute, text='every_minute')
    dp.register_callback_query_handler(answer_notify_every_minute, text='every_minute')

    dp.register_callback_query_handler(callback_notify_every_two_minute, text='every_two_minute')
    dp.register_callback_query_handler(answer_notify_every_two_minute, text='every_two_minute')

    dp.register_callback_query_handler(callback_notify_finish, text='finish')




