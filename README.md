# Описание проекта
**Bot_Skills** - это бот, который помогает отследить результаты своего развития тех или иных навыков.  
Главные возможности:  
✅ Отслеживать прогресс профессиональных навыков как hard, так и soft skills  
🖊 Добавлять и изменять навыки/цели, которые вы развиваете  
📊 Получить подробную статистику за любое время в виде графика или таблицы  
📝 Редактировать и изменять свои записи  
⏱ Отправлять уведомления  

**Как пользоваться ботом:**
1. Создать задание по команде /add 
   - Указать название задания
   - Ввести минимальный и максимальный балл
   - Дать описание задачи
2. Выбрать задание для отслеживания по команде /show_tasks
3. Чтобы отслеживать свой ежедневный прогресс введите команду /note
4. Получить подробную статистику по команде /stat

- Есть возможность удалять задания и последние записанные результаты в команде /admin
- Чтобы отменить любую команду введите /cancel 
- Чтобы получить описание целей нажмите команду /descrip

Также в боте реализован функционал отправка уведомлений, через команду /notify  
Присутствует возможность отправлять сообщения с разной частотой

Для визуализации проекта была создана карта пользователя в Miro, которую можно посмотреть по ссылке:
[miro.com](https://miro.com/app/board/uXjVMzi_tmw=/?share_link_id=733989460090)

# Цели проекта
Создать функционал бота, который:
+ Добавляет новые цели
+ Есть возможность удалять записи
+ Отслеживает прогресс
+ Отправка уведомлений с напоминанием

# Используемые технологии
*aiogram*, *sqlite3*, *apscheduler*, *pandas*, *matplotlib*, *re*

