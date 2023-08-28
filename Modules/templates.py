class Inlines:
    basic = 'Выберите нужный вам раздел'

    class Admin:
        restrictions = """**Ограничение пользователей**
В боте реализованы функции временных и перманентных ограничений, а также их снятие. 


Реализованные на данный момент:

Бан:
/ban (user_id / ответ на сообщение пользователя). Перманентный бан пользователя

/tban (xy. x это любое число больше нуля, y это обозначение временного промежутка (s (секунда), m (минута), h (час), d (день), mon (месяц), y (год)) (user_id / ответ на сообщение пользователя). Временный бан пользователя

/unban (user_id / ответ на сообщение пользователя). Снятие бана

Мут (только если юзер в чате):
/mute (user_id / ответ на сообщение пользователя). Перманентный мут пользователя
/tmute (xy, где "x" это любое число больше нуля, "y" это обозначение временного промежутка (s (секунда), m (минута), h (час), d (день), mon (месяц), y (год)) (user_id / ответ на сообщение пользователя)
/unban (user_id / ответ на сообщение пользователя). Снятие ограничений в правах

Другие:
/kick (user_id / ответ на сообщение пользователя). Кик пользователя из чата
/attack - включение глобального режима "атакуют", при заходе нового пользователя в чат его автоматически блокирует на день
/offattack - отключение глобального режима "атакуют"
"""

        flood = """**Антифлуд**
На данный момент антифлуд реализован частично, без возможности смены настроек. В будущем будут введены настройки, и раздел пополнится

Антифлуд работает на данный момент лишь ограничением количеств сообщений в секунду. По умолчанию это 5 сообщений в секунду, в случае обнаружения флуда происходит мут на 5 минут
"""

        spam = """**Антиспам**
На данный момент Антиспам работает частично. В будущем будут обновлен
"""

        words_bl = """**Запрет слов**
На данный момент не работает
"""

        ai_integration = """**Интеграция систем антиспама**
Интеграция с системами антиспама на данный момент реализована в виде принудительных проверок по CAS (Combot Antispam), и Intellivoid Antispam (Coffeehouse).
"""

        logging = """**Логгирование**
Логгирование действий происходит в два потока. В специально созданный телеграм-канал, и в файл на сервере бота для сохранности данных

Логгируются **ВСЕ** (почти) действия администраторов, в будущем будут логгирорваться также автоматические действия
"""

        connections = """**Подключения**
В разработке
"""

        auto = """**Автоматические действия**
В боте есть антифлуд, он мутит пользователя на 5 минут за 6 сообщений в 5 секунд.


"""

        settings = """**Настройки**
В разработке
"""

        debug = 'gas'

    class Users:
        votes = """**Голосования**
В боте реализовано два типа голосований, голосование за бан и за мут. 

/voteban в ответ на сообщение - голосование за бан
/votemute в ответ на сообщение - голосование за мут

В обоих случаях применяется формула для расчитывания времени наказания:
(Базовое сконфигурированное время + дополнительно сконфигурированное время) * количество чистых голосов "за". Но если \
чистых голосов больше трех пользователя банит навсегда


В будущем будут добавлены ограничивающие правила и продвинутая логика
"""

        reports = """**Репорты**
Репорты предупреждают доступных администраторов о потенциальном нарушителе. Все работает так же как и везде
"""

        karma = """**Карма**
Развлекательная функция для пользователей. Карму можно увеличить/уменьшить поставив соответствующий знак (+/-) в начале сообщения
"""

        antispam = """**Меры против спама**
В разработке
"""

    class Auto:
        antiflood = """**Антифлуд и его алгоритм**
Статью напишем после нормального написания бота :D
"""
        antispam = """**Антиспам и его алгоритм**
Будет написано **после** деплоя))
"""

        chats = """**О блокировке сторонних чатов**
Данный бот написан https://github.com/ANoneTypeOn

И бот не любит, когда его тоскают в левые чаты
"""

class Logs:
# TODO: генератор для автоматической генерации шаблона
    class AdminActions:
        pban = """`{0}` забанен администратором `{1}` в чате `{2}` ({5}).

    Дата-время: `{3}`
    timestamp: `{4}`"""

        tban = """`{0}` забанен администратором `{1}` в чате `{2}` ({7}) на {3} {4}.
    Дата-время: `{5}`
    timestamp: `{6}`"""

        unban = """`{0}` разбанен администратором `{1}` в чате `{2}` ({5}).

    Дата-время: `{3}`
    timestamp: `{4}`"""

        pmute = """`{0}` замучен администратором `{1}` в чате `{2}` ({5}).

    Дата-время: `{3}`
    timestamp: `{4}`"""

        tmute = """`{0}` замучен администратором `{1}` в чате `{2}` ({7}) на {3} {4}.

    Дата-время: `{5}`
    timestamp: `{6}`"""

        unmute = """`{0}` размучен администратором `{1}` в чате `{2}` ({5}).

    Дата-время: `{3}`
    timestamp: `{4}`"""

        kick = """`{0}` кикнут администратором `{1}` в чате `{2}` ({5}).

    Дата-время: `{3}`
    timestamp: `{4}`"""

        purge = """Админ `{0}` почистил сообщения в чате {1} ({6}) с {2} по {3}

    Дата-время: `{4}`
    timestamp: `{5}`"""

    class Polls:
        start = """В чате `{0}` ({3}) было начато голосование за {1} `{2}`"""

        fail = """Голосование за {0} `{1}` в чате `{2}` ({3}) прошло неудачно"""

        success = """Голосование за {0} `{1}` в чате `{2}` ({5}) прошло успешно, пользователь наказан на {3} {4}"""

    class Auto:
        ddos = """Режим "Атакуют!!!" включен в чате `{0}` ({4}) администратором `{1}`.

    Дата-время: `{2}` 
    timestamp: `{3}`"""

        stopddos = """Режим "Атакуют!!!" выключен в чате `{0}` ({4}) администратором `{1}`.

    Дата-время: `{2}` 
    timestamp: `{3}`"""

        ddos_joined = """`{0}` забанен на день в чате `{1}` ({4}), т.к зашел во время атаки. 

    Дата-время: `{2}` 
    timestamp: `{3}`"""

        unauthorized_chat = """`{0}` попытался затащить бота в чат `{1}` ({2}).

    Дата-время: `{3}` 
    timestamp: `{4}`"""

        flood = """Пользователь `{0}` был замучен на 5 минут за флуд в чате `{1}` ({2})."""

        blacklist_message = """В сообщении обнаружено запрещенное слово ({0}), `{1}` забанен. С запрещенными словами можно ознакомиться в `{2}`"""

        blacklist_profile = """В профиле обнаружено запрещенное слово ({0}), {1} забанен. С запрещенными словами можно ознакомиться в {2}"""

class Karma:
    increase = """Пользователь {0} повысил карму {1} до {2}."""

    decrease = """Пользователь {0} понизил карму {1} до {2}."""

    maximum = """У {0} максимальная карма, увы("""

class Votes:
    voteban = """Голосование за бан {0}"""

    votemute = """Голосование за мут {0}"""

class Captcha:
    main = """Добро пожаловать, {0}, в известный тебе чат. 

Новичкам в течении 24 часов запрещено отправлять стикеры, медиа и ссылки.
Это сообщение будет удалено через 7,5 минут, рекомендуем переслать это сообщение в избранное на всякий случай. 

**ВНИМАНИЕ! Нажимая на кнопку ниже вы соглашаетесь, что прочитали правила**"""

    onepm = """Капча это процесс проверки пользователя на бота, это нужно чтобы предотвратить спам и иные зловредные действия в чате.

Чтобы пройти капчу просто нажми на слово "{0}". Этого (наверное) будет достаточно"""

    twopm = """Капча это процесс проверки пользователя на "бота" (в нашем случае это автоматизированный алгоритм, который \
нацелен в первую очередь на продвижение товаров/услуг/профилей, или на зловредные действия с чатом), в нашем случае это \
нужно чтобы предотвратить спам и иные зловредные действия в чате.

Чтобы пройти капчу просто нажми на слово "{0}", а потом на слово "{1}". Этого (наверное) будет достаточно"""

    threepm = """Капча это процесс проверки пользователя на "бота" (в нашем случае это автоматизированный алгоритм, который \
нацелен в первую очередь на продвижение товаров/услуг/профилей, или на зловредные действия с чатом), в нашем случае это \
нужно чтобы предотвратить спам и иные зловредные действия в чате.

Чтобы пройти капчу просто нажми на слово "{0}", потом на слово "{1}", ну и наконец на слово "{2}". Этого (наверное) будет достаточно"""

    success = """Поздравляю, капча пройдена! Вы можете спокойно зайти в чат и наслаждаться общением"""

    failure_time = """Истекло время на прохождение капчи. Приятно было повидаться"""

    failure_wrong = """Ответ не верный. Приятно было повидаться"""

# TODO: решить, куда вставлять двухфакторные и трехфакторные капчи

class Misc:
    start = """Приветствую! Я бот, помогающий модераторам в их работе, предоставляя автоматизацию рутины.

На данный момент бот на стадии тестирования, готов не весь функционал, и возможны сбои.

Для ознакомления с доступным функционалом напишите /help в любом чате со мной"""

    norights = "Недостаточно прав, увы (или нет)"

    noddos = "Режим атаки не включен в этом чате, зачем выключать то что не включено?"

    not_known_error = "Неизвестная ошибка. Данные записаны в лог, об ошибке сообщено разработчику"