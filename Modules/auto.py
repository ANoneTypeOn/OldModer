import json
import random
import re
import time

import aiostream.stream
import requests
from psycopg import Cursor
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant

import Modules.botglobals as botglobals
import Modules.misc as misc
import Modules.templates as templates
from Modules.admins import Restrictions
from Modules.keyboards import Inlines as InlineKeyboards


async def leave(client: Client, msg: Message, chatsCursor: Cursor) -> bool:
    if msg.chat.username in misc.whitelist or msg.chat.id in misc.whitelistids:
        return False

    chat_id = msg.chat.id
    admins = []
    async for i in client.iter_chat_members(chat_id, filter='administrators'):  # граббинг админов
        admins.append(i.user.id)

    users = []
    async for i in client.iter_chat_members(chat_id, filter='all'):  # граббинг максимального количества юзверей
        users.append(i.user.id)

    chat = await client.get_chat(chat_id)
    await client.leave_chat(chat_id)

    chatsCursor.execute('INSERT INTO chats VALUES(%s, %s, %s, %s) ON CONFLICT (chatid) DO UPDATE SET users = %s, admins = %s;', (chat.title, chat.id, users, admins, users, admins))
    return True


class Flood:
    @staticmethod
    async def main(client: Client, msg: Message, maxmsgs: int, mutemins: int, userCursor: Cursor) -> [bool, None]:
        """Увеличение счетчика сообщений в БД, и одновременная проверка для бана"""
        uid = msg.from_user.id
        chatid = msg.chat.id
        try:
            participant = await client.get_chat_member(chatid, uid)
        except UserNotParticipant:
            return

        if participant.status in misc.adminstatus:
            return

        userCursor.execute('''SELECT * FROM flood WHERE uid = %s AND chatid = %s''', (uid, chatid,))
        data = userCursor.fetchall()
        if len(data) >= maxmsgs:
            times = await misc.timestamper(str(mutemins) + 'm')
            await msg.reply(f'Превышен максимум по флуду, мут на {times[1]} {times[2]}')
            if isinstance(await Restrictions.Mute.tempgiven(client, msg, uid, chatid, times[0]), int):
                return True

        userCursor.execute('''INSERT INTO flood VALUES(%s, %s, %s);''', (chatid, uid, int(time.time()),))


    @staticmethod
    async def clear(userCursor):
        """Очищает в БД все записи флуда старше чем заданное значение"""
        timestamp = int(time.time())
        userCursor.execute('DELETE FROM flood WHERE timestamp < %s;', (timestamp,))


class Spam:
    @staticmethod
    async def checkmsg(client: Client, msg: Message, userCursor: Cursor) -> None:
        """Проверка на спам сообщения"""
        uid = msg.from_user.id
        chatid = msg.chat.id
        try:
            participant = await client.get_chat_member(chatid, uid)
        except UserNotParticipant:
            return

        if participant.status in misc.adminstatus:
            return

        spamlist = userCursor.execute('''SELECT spamwords FROM settings WHERE chatid = %s;''', (chatid,))
        for i in spamlist:
            if re.search(re.compile(f'\s{i}\s'), msg.text) is not None:
                await client.ban_chat_member(chatid, uid)
                await msg.reply(str(templates.Logs.Auto.blacklist_message).format(i, uid, '**TODO**'))
                return

    @staticmethod
    async def checkuser(client: Client, msg: Message, userCursor: Cursor) -> None:
        """Проверка профиля пользователя на всякое дерьмо"""
        uid = msg.from_user.id
        chatid = msg.chat.id
        try:
            participant = await client.get_chat_member(chatid, uid)
        except UserNotParticipant:
            return

        if participant.status in misc.adminstatus:
            return

        spamlist = userCursor.execute('''SELECT spamwords FROM settings WHERE chatid = %s;''', (chatid,))
        for i in spamlist:
            async for field in (await misc.profile_gen(msg)):
                if re.search(re.compile(f'\s{i}\s'), field) is not None:
                    await client.ban_chat_member(chatid, uid)
                    await msg.reply(str(templates.Logs.Auto.blacklist_profile).format(i, uid, '**TODO**'))
                    return


class Captcha:
    @staticmethod
    async def generate_comb() -> list[str]:
        """Генерация комбинации слов для капчи"""
        datas = random.sample(misc.Captcha.dataset, misc.Captcha.ccount)
        datas.sort(reverse=True)
        return random.sample(datas, len(datas))

    @staticmethod
    async def onepm(client: Client, msg: Message, rowid: int, captchaCursor: Cursor) -> bool:  # TODO: сделать двух и трехэтапные варианты
        """Отправка капчи с одним этапом"""
        captchaCursor.execute('''SELECT ids FROM redirect WHERE rowid = %s;''', (rowid,))
        checkt = captchaCursor.fetchone()[0][1]
        if msg.from_user.id != checkt:
            await msg.reply('Эта капча не для тебя')
            return False

        words = await Captcha.generate_comb()
        answer = random.choice(words)

        captchaCursor.execute('''DELETE FROM redirect WHERE rowid = %s RETURNING ids, msgid;''', (rowid,))
        ids, msgids, = captchaCursor.fetchone()
        await client.delete_messages(ids[0], msgids)

        timeexp = int(time.time() + 450)
        captchaCursor.execute('''INSERT INTO first_stage VALUES(%s, %s, %s, %s) ON CONFLICT (ids) DO UPDATE SET answer = %s, timeexp = %s RETURNING rowid;''', (ids, 1, answer, timeexp, answer, timeexp))

        keyboard = await InlineKeyboards.Captcha.generate_captcha(words, captchaCursor.fetchone()[0], 1)

        msgid = (await msg.reply(str(templates.Captcha.onepm).format(answer), reply_markup=keyboard)).message_id
        captchaCursor.execute('UPDATE first_stage SET msgid = %s WHERE rowid = %s;', (msgid, rowid))  # TODO: поправить! Сделай это, блять в первом запросе
        return True

    @staticmethod
    async def onepmcheck(client: Client, msg: Message, data: list[str], captchaCursor: Cursor) -> [bool, None]:
        """Проверка ответа на однофазную капчу"""
        data.extend(data[2].split('_'))
        del data[2]  # Да, del удаляет и переменные, и значения на позиции в списках, и т.д, питон
        word = data[3]
        cid = data[2]

        captchaCursor.execute('DELETE FROM first_stage WHERE rowid = %s RETURNING answer, ids;', (cid,))
        fetch = captchaCursor.fetchone()
        if fetch is None:
            return

        answer, ids = fetch

        if type(answer) is bytes:
            answer = answer.decode()  # Ошибки сыпятся, заебали логи загрязнять

        elif type(answer) is str:
            pass

        if word == answer:
            await Captcha.success(client, msg, ids)
        else:
            await Captcha.fail(client, msg, ids)
            return False

    @staticmethod
    async def redirect(client: Client, msg: Message, botusername: str, captchaCursor: Cursor) -> bool:
        """Генерация переадресации в ЛС боту"""
        if msg.from_user.username is not None:
            formater = msg.from_user.username

        elif msg.from_user.last_name is not None:
            formater = msg.from_user.first_name + ' ' + msg.from_user.last_name

        else:
            formater = msg.from_user.first_name

        await client.restrict_chat_member(msg.chat.id, msg.from_user.id, botglobals.Permissions.muted)
        timeexp = int(time.time() + 300)
        captchaCursor.execute(f'''INSERT INTO redirect VALUES(%s, %s, %s) ON CONFLICT (ids) DO UPDATE SET timeexp = %s RETURNING rowid;''', ([msg.chat.id, msg.from_user.id], [1, 1], timeexp, timeexp))
        rowid = captchaCursor.fetchone()[0]
        keyboard = await InlineKeyboards.Captcha.generate_main(rowid, botusername)

        msgid = (await msg.reply(str(templates.Captcha.main).format(formater), parse_mode='md', reply_markup=keyboard)).message_id
        captchaCursor.execute('UPDATE redirect SET msgid = %s WHERE rowid = %s;', ([msg.message_id, msgid], rowid))  # TODO: поправить! Сделай это, блять в первом запросе
        return True

    @staticmethod
    async def success(client: Client, msg: Message, ids: list[int]):
        await client.restrict_chat_member(ids[0], ids[1], botglobals.Permissions.nolinks, until_date=int(time.time() + 86400))
        await msg.delete(True)
        await client.send_message(ids[1], templates.Captcha.success)

    @staticmethod
    async def fail(client: Client, msg: Message, ids: list[int]):
        await client.ban_chat_member(ids[0], ids[1])
        await msg.delete(True)
        await client.send_message(ids[1], templates.Captcha.failure_wrong)

    @staticmethod
    async def clear(client: Client, captchaCursor: Cursor):
        captchaCursor.execute('DELETE FROM redirect WHERE timeexp < %s RETURNING ids, msgid;', (int(time.time()),))
        datas = aiostream.stream.iterate(captchaCursor.fetchall())
        async for ids in datas:
            chat_id = ids[0][0]
            await client.ban_chat_member(chat_id, ids[0][1])
            await client.delete_messages(chat_id, list(ids[1]))

        captchaCursor.execute('DELETE FROM first_stage WHERE timeexp < %s RETURNING ids, msgid;', (int(time.time()),))
        datas = aiostream.stream.iterate(captchaCursor.fetchall())
        async for ids in datas:
            chat_id = ids[0][0]
            await client.ban_chat_member(chat_id, ids[0][1])
            await client.delete_messages(chat_id, ids[1])



class AIantispam:
    @staticmethod
    async def intellivoid(userid: int) -> [str, bool]:
        """Получение и обработка данных от Intellivoid Coffeehouse API, содержит досье на юзверей, которые подпадали под их бота, включая язык, причину блокировки (если имеется), и уровень доверия"""
        data = json.loads(requests.post('https://api.intellivoid.net/spamprotection/v1/lookup', {'query': userid}).text)
        if data['success']:
            if data['results']['attributes']['is_blacklisted']:
                return data['results']['attributes']['blacklist_reason']

        return False

    # TODO: аналог траста

    @staticmethod
    async def combot(userid: int) -> bool:
        """Получение и обработка данных от CAS API, содержит время блокировки, сообщения (и их отловленное количество) за которые юзер забанен, и статус блокировки"""
        data = json.loads(requests.get(f'https://api.cas.chat/check?user_id={userid}').text)
        return data['ok']

# TODO: логгирование сообщений и иная поебота
