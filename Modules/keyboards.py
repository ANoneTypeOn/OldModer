from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random

class Inlines:
    class Help:
        basic = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Для администрации', 'help_admin')
            ],  # Первый ряд
            [
                InlineKeyboardButton('Для обычных пользователей', 'help_users')
            ],  # Второй ряд
            [
                InlineKeyboardButton('Об автоматических действиях', 'help_auto')
            ]
        ])

        admin = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Ограничения пользователей', 'help_admin_restrictions')
            ],  # 1 ряд
            [
                InlineKeyboardButton('Антифлуд', 'help_admin_flood'),
                InlineKeyboardButton('Антиспам', 'help_admin_spam'),
            ],  # 2 ряд
            [
                InlineKeyboardButton('Запрет слов', 'help_admin_words'),
            ],  # 3 ряд
            [
                InlineKeyboardButton('Интеграция с системами антиспама', 'help_admin_ai_integrations'),
            ],  # 4 ряд
            [
                InlineKeyboardButton('Логгирование', 'help_admin_logging'),
                InlineKeyboardButton('Подключения', 'help_admin_connection')
            ],  # 5 ряд
            [
                InlineKeyboardButton('Автоматические действия', 'help_admin_auto'),
            ],  # 6 ряд
            [
                InlineKeyboardButton('Настройки', 'help_admin_settings')
            ]
        ])

        users = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Голосования', 'help_users_votes'),
                InlineKeyboardButton('Репорты', 'help_users_reports'),
            ],
            [
                InlineKeyboardButton('О карме', 'help_users_karma'),
            ],
            [
                InlineKeyboardButton('О мерах против спама', 'help_users_antispam'),
            ],
        ])

        auto = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Антифлуд и его алгоритм', 'help_auto_antiflood'),
            ],
            [
                InlineKeyboardButton('Антиспам и его алгоритм', 'help_auto_antispam'),
            ],
            [
                InlineKeyboardButton('О блокировке сторонних чатов', 'help_auto_thirdparty_chats'),
            ],
        ])

        backbutton = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('На главную', 'help_main')
            ]
        ])

    class Captcha:
        @staticmethod
        async def generate_main(identity: int, botusername: str) -> InlineKeyboardMarkup:
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton('Пройти капчу', url=f'https://t.me/{botusername}?start={identity}')
                ]
            ])

        @staticmethod
        async def generate_captcha(dataset: list[str], cid: int, stage_count: int) -> InlineKeyboardMarkup:
            """Генерация инлайна для капчи"""
            ready = []
            row = []
            for word in dataset:
                if len(row) >= 2:
                    ready.append(list(row))
                    row.clear()

                if not random.getrandbits(4):  # 1 и иные integer у нас тоже булеан (1 = True, все остальное False), а еще not просто реверсирует булеан
                    row.append(InlineKeyboardButton('-', f'captcha_{stage_count}_{cid}_tu'))

                row.append(InlineKeyboardButton(word, f'captcha_{stage_count}_{cid}_{word}'))

            if ready is not []:
                ready.append(list(row))

            return InlineKeyboardMarkup(ready)

    class Votes:
        @staticmethod
        async def votegen(rowid: int):
            return InlineKeyboardMarkup([
                [InlineKeyboardButton('За', f'vote_+_{rowid}')],
                [InlineKeyboardButton('Против', f'vote_-_{rowid}')]
            ])
