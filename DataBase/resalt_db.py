import sqlite3 as sq
from create_bot import bot

def sql_start():
    global base, cur
    base = sq.connect('task.db')
    cur = base.cursor()
    if base:
        print("Data base connected OK!")
    base.execute("""CREATE TABLE IF NOT EXISTS result(id INTEGER
                                                    , name TEXT
                                                    , score INTEGER
                                                    , data DATE)""")
    base.commit()

async def sql_add_command(data):
    'Добавляет баллы в БД'
    cur.execute('INSERT INTO result (id, name, score, data)VALUES (?, ?, ?, ?)', tuple(data.values()))
    base.commit()

async def sql_delete_note(state):
    'Удаляет последнюю запись из БД'
    async with state.proxy() as data:
        cur.execute('INSERT INTO task (name, min, max, data)VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()

def choose_table(data):
    result = cur.execute(f"""select * from result where data >= '{data["mindate"]}' and data <= '{data["maxdate"]}' and id in ({data['num']})""").fetchall()
    return result

def get_all_table(nums):
    result = cur.execute(f"""select * from result where id in {tuple(nums) * 2}""").fetchall()
    return result

def get_table_name(nums):
    result = cur.execute(f"""select * from result where id = {nums}""").fetchall()
    return result

def choose_chart(data):
    result = cur.execute(f"""select * from result where data >= '{data["mindate"]}' and data <= '{data["maxdate"]}' and id in {tuple(data['num'])*2}""").fetchall()
    return result

"""
--------Команда для удаления строк--------
"""

async def sql_delete_note_command(message, nums):
    ret = cur.execute(f"""select id, name from task where id = {nums}""").fetchall()
    cur.execute(f"""DELETE from result
where id = {nums}
and data = (
select data from result
where id = {nums}
order by data desc
limit 1)""")
    base.commit()
    await bot.send_message(message.from_user.id,
                           text=f"""Вы удалили последнюю запись №{ret[0][0]}\nЗадание: {ret[0][1]}""")