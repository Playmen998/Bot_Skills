from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, note, stat, notify
from DataBase import task_db, resalt_db


async def on_startup(_):
    print('Бот запущен')
    task_db.sql_start()
    resalt_db.sql_start()



if __name__ == "__main__":
    "Запуск хэндлеров"
    admin.register_handlers_admin(dp)
    note.register_handlers_note(dp)
    stat.register_handlers_stat(dp)
    notify.register_handlers_notify(dp)
    client.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)