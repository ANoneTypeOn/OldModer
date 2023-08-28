from pyrogram.types import Message
from pyrogram import Client
from time import time
from aiostream import stream
from psycopg import Cursor

from Modules.misc import vector
from Modules import keyboards
from Modules import botglobals
from Modules import templates

class Karma:
    class Formulas:
        @staticmethod
        async def plus(main_karma: int, target_karma: int) -> int:
            """Увеличение кармы"""
            modificator = main_karma // target_karma
            return target_karma + modificator

        @staticmethod
        async def minus(main_karma: int, target_karma: int) -> int:
            """Уменьшение кармы"""
            modificator = main_karma // target_karma
            return target_karma - modificator

    @classmethod
    async def main(cls, msg: Message, usersCursor: Cursor) -> [bool, int, None]:
        """Главная функция кармы. True это успех, False это отсутствие реплая"""
        # if msg.reply_to_message is not None:
        # TODO: перенести в основную функцию

        userid = msg.from_user.id
        text = str(msg.text)
        boolvector = await vector(text)
        if boolvector is None:
            return None

        usersCursor.execute('SELECT karma FROM karma WHERE uid = %s;', (userid,))
        selfkarma, = usersCursor.fetchone()
        usersCursor.execute('SELECT karma FROM karma WHERE uid = %s;', (msg.reply_to_message.from_user.id,))
        replykarma, = usersCursor.fetchone()

        if replykarma >= 32756 or replykarma <= -32757:
            await msg.reply(str(templates.Karma.maximum).format(msg.reply_to_message.from_user.username))
            return False

        if boolvector:
            returnkarma = await cls.Formulas.plus(selfkarma, replykarma)
            await msg.reply(str(templates.Karma.increase).format(msg.from_user.username, msg.reply_to_message.from_user.username, returnkarma))
            usersCursor.execute('UPDATE karma SET karma = %s WHERE uid = %s;', (returnkarma, msg.reply_to_message.from_user.id,))
        else:
            returnkarma = await cls.Formulas.minus(selfkarma, replykarma)
            await msg.reply(str(templates.Karma.decrease).format(msg.from_user.username, msg.reply_to_message.from_user.username, returnkarma))
            usersCursor.execute('UPDATE karma SET karma = %s WHERE uid = %s;', (returnkarma, msg.reply_to_message.from_user.id,))

        return True

    @staticmethod
    async def addrecord(userid: int, usersCursor: Cursor) -> None:
        """Добавление записей в таблицу кармы. При конфликте ничего не сделает"""
        usersCursor.execute('INSERT INTO karma VALUES(%s, 0) ON CONFLICT DO NOTHING;', (userid,))


class Votes:
    class Database:
        @staticmethod
        async def clear(client: Client, pollCursor, chatsCursor: Cursor) -> [bool, None]:
            pollCursor.execute('DELETE FROM polls WHERE timeexp <= %s RETURNING *;', (int(time()),))
            datas = pollCursor.fetchall()
            if len(datas) == 0:
                return

            # ([chat_id, votingfor], msg.message_id, int(time()), 2|1, [yes], [no)
            async for i in stream.iterate(datas):
                count = len(i[4]) - len(i[5])
                if count <= 0:
                    return False

                # chatsCursor.execute('SELECT votetime FROM settings WHERE chatid = %s;', (i[0],))
                basictime = 3600  # Час
                configtime = 1800
                if count > 3:
                    ftime = 0
                else:
                    ftime = (basictime + configtime) * count

                chat_id = i[0][0]
                votingfor = i[0][1]

                await client.edit_message_reply_markup(chat_id, i[2])
                if i[3] == 1:
                    await client.ban_chat_member(chat_id, votingfor, ftime)
                else:
                    await client.restrict_chat_member(chat_id, votingfor, botglobals.Permissions.muted, ftime)

    @staticmethod
    async def voteban(msg: Message, pollsCursor: Cursor) -> bool:
        """Голосование за бан, формула: базовое время + доп. конфиг. время * количество чистых голосов за"""
        votingfor = msg.reply_to_message.from_user.id
        voteinitiator = msg.from_user.id
        chat_id = msg.chat.id

        pollsCursor.execute(F'''SELECT rowid FROM polls WHERE ids = ARRAY{str([chat_id, votingfor])};''')
        if pollsCursor.fetchone() is not None:
            return False

        pollsCursor.execute('''INSERT INTO polls VALUES (%s, %s, %s, %s, %s) RETURNING rowid;''', ([chat_id, votingfor], msg.message_id, int(time()), 2, [voteinitiator],))
        rowid = pollsCursor.fetchone()[0]
        keyboard = await keyboards.Inlines.Votes.votegen(rowid)

        msgid = (await msg.reply(str(templates.Votes.voteban).format(msg.reply_to_message.from_user.id), reply_markup=keyboard)).message_id
        pollsCursor.execute('''UPDATE polls SET msgid = %s WHERE rowid = %s;''', (msgid, rowid,))
        return True

    @staticmethod
    async def votemute(msg: Message, pollsCursor: Cursor) -> int:
        """Голосование за мут, формула: базовое конфигурированное время + доп. конфиг. время * количество чистых голосов за"""
        votingfor = msg.reply_to_message.from_user.id
        voteinitiator = msg.from_user.id
        chat_id = msg.chat.id

        pollsCursor.execute('''INSERT INTO polls VALUES (%s, %s, %s, %s, %s) RETURNING rowid;''', ([chat_id, votingfor], msg.message_id, int(time()), 2, [voteinitiator],))
        rowid = pollsCursor.fetchone()[0]
        keyboard = await keyboards.Inlines.Votes.votegen(rowid)

        msgid = (await msg.reply(str(templates.Votes.votemute).format(msg.reply_to_message.from_user.id), reply_markup=keyboard)).message_id
        pollsCursor.execute('''UPDATE polls SET msgid = %s WHERE rowid = %s;''', (msgid, rowid,))
        return rowid

    @staticmethod
    async def vote(user_id: int, pollid: int, svector: str, pollsCursor: Cursor) -> bool:
        """Отдача голоса за/против в голосовании"""
        pollsCursor.execute('''SELECT rowid FROM polls WHERE rowid = %s AND %s = ANY (yes || no);''', (pollid, user_id,))
        if pollsCursor.fetchone() is not None:
            return False

        bvector = await vector(svector)

        if bvector:
            pollsCursor.execute('UPDATE polls SET yes = array_append(yes, %s) WHERE rowid = %s;', (user_id, pollid,))
        else:
            pollsCursor.execute('UPDATE polls SET no = array_append(no, %s) WHERE rowid = %s;', (user_id, pollid,))
        return True
