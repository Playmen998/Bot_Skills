from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb1 = KeyboardButton('/note')
kb2 = KeyboardButton('/stat')
kb3 = KeyboardButton('/goal')
kb4 = KeyboardButton('/admin')
"Команда /start"
kb.add(kb1, kb2).add(kb3,kb4)


adminKB = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
adminKB1 = KeyboardButton('/add')
adminKB2 = KeyboardButton('/delete_task')
adminKB3 = KeyboardButton('/delete_res')
adminKB4 = KeyboardButton('/show_tasks')
"Команды админа"
adminKB.add(adminKB4, adminKB1).add(adminKB2, adminKB3)


statKB = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
statKB1 = KeyboardButton('/show_chart')
statKB2 = KeyboardButton('/show_table')
"Показать данные график или таблица"
statKB.add(statKB1, statKB2)

tableKB = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
tableKB1 = KeyboardButton('/all_dateT')
tableKB2 = KeyboardButton('/choose_dateT')
"Показать таблицу"
tableKB.add(tableKB1, tableKB2)



chartKB = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
chartKB1 = KeyboardButton('/all_dateC')
chartKB2 = KeyboardButton('/choose_dateC')
"Показать график"
chartKB.add(chartKB1, chartKB2)