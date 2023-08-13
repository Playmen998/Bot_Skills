import sqlite3 as sq
from create_bot import bot

def sql_start():
    global base, cur
    base = sq.connect('task.db')
    cur = base.cursor()
    if base:
        print("Data base connected OK!")
    base.execute("""CREATE TABLE IF NOT EXISTS task(id INTEGER PRIMARY KEY AUTOINCREMENT 
                                                    , name TEXT
                                                    , min score INTEGER
                                                    , max score INTEGER
                                                    , descrip VARCHAR
                                                    , data DATE)""") #тут мб надо удалить праймери кей
    base.commit()

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO task (name, min, max, descrip, data)VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

"""
==========Команды для выбора заданий==========
"""
def all_tasks():
    'Задания для выбора (admin)'
    string = ''
    for ret, i in cur.execute(f"""select distinct name, id from task""").fetchall():
        string += f'Задание №{i}: {ret}\n'
    return string

def sort_tasks(count_list):
    'Задания для обработки (в note)'
    str_count = ''
    for i in count_list:
        str_count += str(i) + ','
    name = cur.execute(f"""select distinct name, max from task where id in ({str_count[:-1]})""").fetchall()
    id = cur.execute(f"""select distinct id from task where id in ({str_count[:-1]})""").fetchall()
    return name, id


"""
--------Команда для удаления задания--------
"""

async def sql_delete_task_command(message, nums):
    ret = cur.execute(f"""select * from task where id = {nums}""").fetchall()
    cur.execute(f"""DELETE from task where id = {nums}""")
    base.commit()
    await bot.send_message(message.from_user.id,
                           text=f"""Вы удалили задание №{ret[0][0]}\nЗадание: {ret[0][1]}""")

"""
==========Команды для получения описания заданий==========
"""
def sql_et_descrip_task(nums):
    name = cur.execute(f"""select id, name, descrip, min, max from task where id in ({nums[0]})""").fetchall()
    return name