from time import time
from pyrogram.types import Message
from aiostream import stream
from _collections_abc import AsyncIterable

whitelist = []    # username-ы чатов в белом списке, указывать без "@" в начале 
whitelistids = [] # id чатов в белом списке
adminstatus = ['creator', 'administrator']  # для проверки статуса ользователя по телеграмму

# TODO: переписать в генератор, это сильно ускорит код
async def profile_gen(msg: Message) -> AsyncIterable:
    """Возвращает список с нужными параметрами"""
    user = msg.from_user
    return stream.iterate([user.username, user.status, user.first_name, user.last_name])

async def timestamper(data: str) -> [list, None]:
    """Переводит строки вида "yx" в словари, содержащие готовый timestamp для отправки телеге, и данные для генерации сообщения.
    Где y это любое положительное число от 0, а x это одно из обозначений временного отрезка (секунда (s), минута (min), и т.д)"""
    match len(data):
        case 2:
            multiplicator = int(data[0])
            timetype = data[1]

        case 3:
            multiplicator = int(data[0] + data[1])
            timetype = data[2]

        case _:
            return

    match timetype:
        case 's':
            seconds = 1
            timetypes = ['секунд', 'секунда', 'секунды', 'секунды', 'секунды', 'секунд', 'секунд', 'секунд', 'секунд',
                         'секунд']

        case 'm':
            seconds = 60
            timetypes = ['минут', 'минута', 'минуты', 'минуты', 'минуты', 'минут', 'минут', 'минут', 'минут', 'минут']

        case 'h':
            seconds = 3600
            timetypes = ['часов', 'час', 'часа', 'часа', 'часа', 'часов', 'часов', 'часов', 'часов', 'часов']

        case 'd':
            seconds = 86400
            timetypes = ['дней', 'день', 'дня', 'дня', 'дня', 'дней', 'дней', 'дней', 'дней', 'дней']

        case 'mon':
            seconds = 2628003  # 2628002,88 не очень жрется, пусть и будет пару секунд поверх, но это не критично
            timetypes = ['месяцев', 'месяц', 'месяца', 'месяца', 'месяца', 'месяцев', 'месяцев', 'месяцев', 'месяцев',
                         'месяцев']

        case 'y':
            seconds = 31536000
            timetypes = ['лет', 'год', 'года', 'года', 'года', 'лет', 'лет', 'лет', 'лет', 'лет']

        case _:
            return

    return int(time() + (seconds * multiplicator)), timetypes[int(str(multiplicator)[-1])], multiplicator


class Captcha:
    datas = [
        "игра", "пляски", "ебань", "лидер", "телевидение", "актер", "монтаж", "ассемблер", "мегабайт", "словарь", "интернет",
        "интерес", "шоу", "криптовалюта", "хейтер", "ИИ", "блокчейн", "сервер", "контр", "мера", "лохотрон", "невидимка",
        "глобальность", "игроки", "монстр", "дополнение", "истребление", "мало", "три", "семь", "минус", "аппл", "макрософт",
        "тесл", "отсылка", "образование", "это", "ложь", "вопрос", "подмога"
             ]    # Список слов, которые могут быть использованы в капче

    dataset = tuple(set(datas))  # set для предотвращения дубликатов
    ccount = len(dataset) // 6

async def vector(text: str) -> [bool, None]:
    """Передача вектора в виде булеана"""
    if text.startswith('+'):
        return True

    elif text.startswith('-'):
        return False

    else:
        return None
