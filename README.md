# test_fox

### Как запустить?
- клонируем репозиторий
- создаем в корне и заполняем .env файл, по примеру .env.example
- запускаем контейнеры:
 docker-compose up -d
- создаем и выполняем миграции и забиваем статусы в базу выполнив: 
sh create_migration.sh
- Готово, наш проект развернуть на нашем localhost и можно смотреть свагер.

Сделал сразу с Вебсервером, так мне было проще, да и под фронт в дальнейшем проще будет настроить.

**Необходимо спроектировать реляционную базу данных и написать API-сервис для небольшой тикетной системы**

Описание тикетной системы:

- Есть клиенты — пользователи Telegram. Клиент пишет боту в Telegram сообщение, в системе создается новый тикет.

### Автоматически создаем новый тикет, когда пользователь пише в чат боту, тикет создается в базе со статусом **Открыт**.

У тикета есть минимум такие статусы: **Открыт**, **В работе**, **Закрыт**. Новый тикет, связанный с клиентом, создается только при условии, что предыдущий закрыт.

### Если сотрудник закроет тикет, то следующее сообщение в чат от пользователя откроет новый тикет

- Есть сотрудник, работающий в тикетной системе. Он может:
    - смотреть список тикетов (должна быть возможно фильтрации по статусу, сотруднику, сортировки по времени создания\обновления),

    ### реализована сортировка по времени создания\обновления, "-" перед полем указывает направление сортировки, фильтрация статусу, сотруднику, добавлена пагинация

    - менять статус тикета.

    ### возможно менять статус(**Открыт** - id=1, **В работе** id=2, **Закрыт** id=3), устанавливать сотрудника на тикет.

    - получать сообщения от клиента в тикете и отправлять ответы в телеграмм.

    ### Бот сохраняет сообщение в базу и прикрепляет к тикету, когда сотрудник отправляет сообщение, то в базе автоматически создается сообщение и прикрепляется к тикету, а так же через requests отправляется сообщение в telegram чат. У сообщения, отправленного пользователем user_id is None т.к. в базе мы храним только сотрудников и т.к. у нас один chat_id на весь тикет, то если None, то это сообщение пользователя. Что уведомления отправлялись необходимо назначить пользователя и поменять статус на **В работе**. Отправлять может только тот, кто указан у ticket в user_id.


**Framework:** `FastAPI`

В качестве БД используется `PostgreSQL`

---

**⭐️ Дополнительные задания:**

- Должен быть реализован процесс аутентификации сотрудника в системе;

    ### Реализовал кастомную аутентификацию через один аксесc jwt токен, можно конечно было бы через куки сессии + аксесс токен, что бы часто не разлогиниваться, но так проще. Регистрируемся и входим под своими учетными данными, получаем аксесс токен и указываем его в заголовках при обращении к API.

- Сотрудник должен получать сообщения от клиента “в прямом эфире”, без обновления страницы. Как это можно сделать? Попробуйте реализовать;

    ### Реализовал через вебсокеты, авторизация идет в самой сессии в формате: фронт устанавливает соединение ws://localhost/api/v1/ticket/ws/{ticket_id},а затем отправляет строку "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDE3MDEyODB9.Zns3XdyRH4jW9Cl6hxAWB3bWyZQmsL-Jp0M6dwKqi4s", мы обрезаем токен и проверяем его актуальность, если все хорошо, то можно продолжить работу в сокете.

- У клиента и сотрудника должна быть возможность отправки и получения файлов в чате;

    ### Файлы, отправленные пользователем и сотрудником сохраняются на сервере и прикрепляются к тикету, можно получить отфильтрованный список файлов тикета. Если установлена сессия, то после сохранения файла от пользователя на сервере будет отправляться в сессию сообщение, что был загружен файл с id=file_id. Его можно перехватить фронтом и загрузить файл сделав запрос на API на загрузку файла по его id. Сотрудник же прикрепляет файлы отдельной ручкой через API, файлы тут же уходят пользователю в чат telegram.

- Реализовать правила по работе с тикетом например: автоматически ставить определенного сотрудника на тикет, если тикет от конкретного клиента. Попробуйте сделать эту систему правил кастомной, чтобы сотрудник мог добавлять правила “на ходу”.

    ### Сотрудник может сделав запрос на POST /api/v1/scheduler/ и передав telegram_chat_id=1234567 пользователя установить правило, которое будет применено при создании тикета пользователем и если его telegram_chat_id=1234567, то ему автоматически назначается сотрудник и сотруднику останется изменить статус на **В работе**, что бы работать с тикетом. Так же правило можно удалить, так же отправив telegram_chat_id на DELETE /api/v1/scheduler/.