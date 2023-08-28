from Modules.misc import timestamper
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant
from Modules import botglobals


class Restrictions:
    @staticmethod
    async def kick(client: Client, msg: Message, chat_id: int) -> [int, None]:
        """Кик юзера"""
        if msg.reply_to_message is not None:
            uid = msg.reply_to_message.from_user.id
        else:
            templist = str(msg.text).split(' ')
            templist.__delitem__(0)

            tempuid = templist[0]
            if tempuid.startswith('@'):
                uid = tempuid.removeprefix('@')
            else:
                try:
                    uid = int(tempuid)
                except ValueError:
                    await msg.reply('Тут нету необходимых мне данных. Вообще!')
                    return
        try:
            udata = await client.get_chat_member(chat_id, uid)
        except ValueError:
            await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
            return

        except UserNotParticipant:
            return

        # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя, поэтому как есть
        if udata.promoted_by is not None:
            await msg.reply(
                "Админа банить? Не, чувак, так не пойдет")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
            return

        if udata.status == 'kicked' or udata.status == 'left':
            await msg.reply('Пользователь уже вне чата, увы')
            return

        await client.ban_chat_member(chat_id, uid)
        await client.unban_chat_member(chat_id, uid)  # TODO: обновить форматирование шаблонов
        await client.send_message(chat_id, 'Кикнут!')
        return uid

    class Ban:
        @staticmethod
        async def permanent(client: Client, msg: Message, chat_id: int) -> [int, None]:
            """Перманентный бан"""
            # Получение id пользователя для последующего выполнения действия
            if msg.reply_to_message is not None:
                uid = msg.reply_to_message.from_user.id
            else:
                templist = str(msg.text).split(' ')
                templist.__delitem__(0)

                tempuid = templist[0]
                if tempuid.startswith('@'):
                    uid = tempuid.removeprefix('@')
                else:
                    try:
                        uid = int(tempuid)
                    except ValueError:
                        await msg.reply(
                            'Тут нету ни юзернейма, ни ID юзера, ни ответа на сообщение юзера. Перечитайте документацию')
                        return
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

                # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя (даже если бы они были на 3.9), поэтому как есть
            if udata.promoted_by is not None:
                await msg.reply(
                    "Админа банить? Не, чувак, так не пойдет")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
                return

            if udata.status == 'kicked' or udata.status == 'left':
                await msg.reply('Пользователь уже забанен')
                return

            await client.ban_chat_member(chat_id, uid)
            await client.send_message(chat_id, 'ЗАБАНЕН!')
            return uid

        @staticmethod
        async def temp(client: Client, msg: Message, chat_id: int) -> [int, None]:
            """Временный бан"""
            # Получение id пользователя для последующего выполнения действия
            templist = str(msg.text).split(' ')
            templist.__delitem__(0)
            until = await timestamper(templist[0])

            if msg.reply_to_message is not None:
                uid = msg.reply_to_message.from_user.id
            else:
                tempuid = templist[1]
                if tempuid.startswith('@'):
                    uid = tempuid.removeprefix('@')
                else:
                    try:
                        uid = int(tempuid)
                    except ValueError:
                        await msg.reply(
                            'Тут нету ни юзернейма, ни ID юзера, ни ответа на сообщение юзера. Перечитайте документацию')
                        return
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

                # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя (даже если бы они были на 3.9), поэтому как есть
            if udata.promoted_by is not None:
                await msg.reply(
                    "Админа банить? Не, чувак, так не пойдет")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
                return

            if udata.status == 'kicked':
                await msg.reply('Пользователь уже забанен')
                return

            if await client.ban_chat_member(chat_id, uid, until[0]):
                await client.send_message(chat_id, f'Пользователь забанен на {until[2]} {until[1]}!')
                return [until[2], until[1], uid]
            return

        @staticmethod
        async def remove(client: Client, msg: Message, chat_id: int) -> [int, None]:
            """Разбан юзера"""
            if msg.reply_to_message is not None:
                uid = msg.reply_to_message.from_user.id
            else:
                templist = str(msg.text).split(' ')
                templist.__delitem__(0)

                tempuid = templist[0]
                if tempuid.startswith('@'):
                    uid = tempuid.removeprefix('@')
                else:
                    try:
                        uid = int(tempuid)
                    except ValueError:
                        await msg.reply(
                            'Тут нету ни юзернейма, ни ID юзера, ни ответа на сообщение юзера. Перечитайте документацию')
                        return
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

            if udata.status != 'kicked':
                await msg.reply('Пользователь не забанен')
                return

            if await client.unban_chat_member(chat_id, uid):
                await msg.reply('Пользователь успешно разбанен')
                return uid
            return

    class Mute:
        @staticmethod
        async def permanent(client: Client, msg: Message, chat_id: int) -> [int, None]:
            """Перманентный мут"""
            # Получение id пользователя для последующего выполнения действия
            if msg.reply_to_message is not None:
                uid = msg.reply_to_message.from_user.id
            else:
                templist = str(msg.text).split(' ')
                templist.__delitem__(0)

                tempuid = templist[0]
                if tempuid.startswith('@'):
                    uid = tempuid.removeprefix('@')
                else:
                    try:
                        uid = int(tempuid)
                    except ValueError:
                        await msg.reply(
                            'Тут нету ни юзернейма, ни ID юзера, ни ответа на сообщение юзера. Перечитайте документацию')
                        return
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

                # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя (даже если бы они были на 3.9), поэтому как есть
            if udata.promoted_by is not None:
                await msg.reply(
                    "Админа мутить? Не, не умею(")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
                return

            if udata.status == 'kicked' or udata.status == 'left':
                await msg.reply('Пользователь уже не в чате, поверх поставить ничего не могу')
                return

            await client.restrict_chat_member(chat_id, uid, botglobals.Permissions.muted)
            await client.send_message(chat_id, 'ЗАМУЧЕН!')
            return uid

        @staticmethod
        async def temp(client: Client, msg: Message, chat_id: int) -> [int, None]:
            """Временный мут"""
            templist = str(msg.text).split(' ')
            templist.__delitem__(0)
            until = await timestamper(templist[0])

            if msg.reply_to_message is not None:
                uid = msg.reply_to_message.from_user.id
            else:
                tempuid = templist[1]
                if tempuid.startswith('@'):
                    uid = tempuid.removeprefix('@')
                else:
                    try:
                        uid = int(tempuid)
                    except ValueError:
                        await msg.reply(
                            'Тут нету ни юзернейма, ни ID юзера, ни ответа на сообщение юзера. Перечитайте документацию')
                        return
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

                # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя (даже если бы они были на 3.9), поэтому как есть
            if udata.promoted_by is not None:
                await msg.reply(
                    "Админа мутить? Не, не умею(")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
                return

            if udata.status == 'kicked' or udata.status == 'left':
                await msg.reply('Пользователь уже не в чате, поверх поставить ничего не могу')
                return

            await client.restrict_chat_member(chat_id, uid, botglobals.Permissions.muted, until[0])
            await client.send_message(chat_id, f'Пользователь замучен на {until[2]} {until[1]}!')
            return uid

        @staticmethod
        async def tempgiven(client: Client, msg: Message, uid: int, chat_id: int, until: int) -> [int, None]:
            """Временный мут, но с заранее переданным временем"""
            # Получение id пользователя для последующего выполнения действия
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

                # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя (даже если бы они были на 3.9), поэтому как есть
            if udata.promoted_by is not None:
                await msg.reply(
                    "Админа мутить? Не, не умею(")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
                return

            if udata.status == 'kicked' or udata.status == 'left':
                await msg.reply('Пользователь уже не в чате, поверх поставить ничего не могу')
                return

            await client.restrict_chat_member(chat_id, uid, botglobals.Permissions.muted, until)
            return uid

        @staticmethod
        async def remove(client: Client, msg: Message, chat_id: int) -> [int, None]:
            """Разбан юзера"""
            if msg.reply_to_message is not None:
                uid = msg.reply_to_message.from_user.id
            else:
                templist = str(msg.text).split(' ')
                templist.__delitem__(0)

                tempuid = templist[0]
                if tempuid.startswith('@'):
                    uid = tempuid.removeprefix('@')
                else:
                    try:
                        uid = int(tempuid)
                    except ValueError:
                        await msg.reply(
                            'Тут нету ни юзернейма, ни ID юзера, ни ответа на сообщение юзера. Перечитайте документацию')
                        return
            try:
                udata = await client.get_chat_member(chat_id, uid)
            except ValueError:
                await msg.reply('По всей видимости я получил ID канала, или чата... Не важно')
                return

            except UserNotParticipant:
                return

                # На счет таких блоков из if'ов я выскажусь так: свитчами это сделать нельзя (даже если бы они были на 3.9), поэтому как есть

            if udata.promoted_by is not None:
                await msg.reply(
                    "Так это же админ...")  # Проверка на админа, я не люблю такие бесячие мелочи как возможность "забанить" админа
                return

            if udata.status == 'kicked' or udata.status == 'left':
                await msg.reply('Пользователь не в чате')
                return

            await client.restrict_chat_member(chat_id, uid, botglobals.Permissions.basic)
            await client.send_message(chat_id, f'Пользователь размучен!')
            return uid

async def purge(client: Client, msg: Message, chat_id: int) -> [bool, None]:
    """Очистка сообщений с сообщения админа по реплайнутое"""
    if msg.reply_to_message is None:
        await msg.reply('Ответь на сообщение, которое будет стоп-краном')
        return

    start = msg.message_id
    stop = msg.reply_to_message.message_id
    output = await client.delete_messages(chat_id, range(stop, start + 1))
    return [output, stop, start]

# class Settings:
#     async def

# TODO: настройки, и иная шваль
