from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message
from time import time
from datetime import datetime
from configparser import ConfigParser
import psycopg  # psycopg 3
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import Modules.misc as misc
import Modules.admins as admin
import Modules.users as users
import Modules.auto as auto
import Modules.templates as templates
import Modules.keyboards as keyboards

# Конфиг
config = ConfigParser()
config.read('config.ini')

api_id = config.getint('api', 'id')
api_hash = config.get('api', 'hash')
token = config.get('api', 'token')
logging_channel = config.getint('logging', 'channel')

dbrole = config.get('db', 'role')
# Базы данных
db_conn = psycopg.connect(dbname='mainbot', host='/tmp', port='5432', user=dbrole, autocommit=True)
cursor = db_conn.cursor()

def createdb():
    cursor.execute('CREATE TABLE IF NOT EXISTS chats(chatname TEXT, chatid BIGINT PRIMARY KEY, users BIGINT[], admins BIGINT[]);')  # "INEGER[]" в PostgreSQL это списки без ограничений, классная херня
    cursor.execute('CREATE TABLE IF NOT EXISTS settings(chatid BIGINT, spamwords TEXT[], mute BOOLEAN, votetime INTEGER);')

    cursor.execute('CREATE TABLE IF NOT EXISTS attackers(chatid BIGINT, uid BIGINT, timestamp INTEGER);')

    cursor.execute('CREATE TABLE IF NOT EXISTS karma(uid BIGINT, karma SMALLINT);')
    cursor.execute('CREATE TABLE IF NOT EXISTS flood(chatid BIGINT, uid BIGINT, timestamp INTEGER);')
    cursor.execute('CREATE TABLE IF NOT EXISTS profile(uid BIGINT PRIMARY KEY, nicknames TEXT[], usernames TEXT[], was_muted BOOLEAN, was_banned BOOLEAN);')

    cursor.execute('''CREATE TABLE IF NOT EXISTS polls(ids BIGINT[2], msgid INTEGER, timeexp INTEGER, type SMALLINT, yes BIGINT[], no BIGINT[] DEFAULT '{}', rowid INTEGER GENERATED ALWAYS AS IDENTITY);''')

    cursor.execute('CREATE TABLE IF NOT EXISTS redirect(ids BIGINT[2] PRIMARY KEY, msgid INTEGER[2], timeexp INTEGER, rowid INTEGER GENERATED ALWAYS AS IDENTITY);')  # ids INTEGER[2] PRIMARY KEY сделано для того, чтобы не засорять таблицу доп. данными, и избежать конфликтов
    cursor.execute('CREATE TABLE IF NOT EXISTS first_stage(ids BIGINT[2] PRIMARY KEY, msgid INTEGER, answer TEXT, timeexp INTEGER, rowid INTEGER GENERATED ALWAYS AS IDENTITY);')


createdb()

under_attack = [False]
attack_message = [0]

logging.basicConfig(filename='bot.log', level=logging.ERROR)
client = Client(session_name='bot', api_id=api_id, api_hash=api_hash, bot_token=token, sleep_threshold=10)


@client.on_callback_query()
async def inlines(cli, callbackq):
    uid = int(callbackq.from_user.id)  # Юзверь ID
    data = str(callbackq.data).split('_', 2)
    msg = callbackq.message

    first_part = data[0]
    second_part = data[1]
    list_len = len(data)

    if list_len == 2:
        if first_part == 'help':
            match second_part:
                case 'main':
                    await client.edit_message_text(uid, callbackq.message.message_id, templates.Inlines.basic, reply_markup=keyboards.Inlines.Help.basic)
                    return

                case 'admin':
                    await client.edit_message_reply_markup(uid, callbackq.message.message_id, reply_markup=keyboards.Inlines.Help.admin)
                    return

                case 'users':
                    await client.edit_message_reply_markup(uid, callbackq.message.message_id, reply_markup=keyboards.Inlines.Help.users)
                    return

                case 'auto':
                    await client.edit_message_reply_markup(uid, callbackq.message.message_id, reply_markup=keyboards.Inlines.Help.auto)
                    return

                case _:
                    return

    third_part = data[2]

    match first_part:
        case 'captcha':
            match second_part:
                case '1':
                    await auto.Captcha.onepmcheck(client, msg, data, cursor)
                    return

                case '2':
                    pass

                case _:
                    return

        case 'vote':
            await users.Votes.vote(uid, int(third_part), second_part, cursor)
            return

        case 'help':
            match second_part:
                case 'admin':
                    match third_part:
                        case 'restrictions':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.restrictions, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'flood':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.flood, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'spam':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.spam, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'words':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.words_bl, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'ai_integrations':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.ai_integration, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'logging':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.logging, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'connection':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.connections, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'auto':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.auto, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'settings':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Admin.settings, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case _:
                            return

                case 'users':
                    match third_part:
                        case 'votes':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Users.votes, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'reports':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Users.reports, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'karma':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Users.karma, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'antispam':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Users.antispam, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case _:
                            return

                case 'auto':
                    match third_part:
                        case 'antispam':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Auto.antispam, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'antiflood':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Auto.antiflood, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case 'thirdparty_chats':
                            await client.edit_message_text(uid, callbackq.message.message_id, text=templates.Inlines.Auto.chats, reply_markup=keyboards.Inlines.Help.backbutton)
                            return

                        case _:
                            return
                case _:
                    return


@client.on_message(filters.command('start') & filters.private)
async def startmsg(cli, msg):
    if str(msg.chat.id).startswith('-'):
        return

    if len(msg.command) > 1:
        await auto.Captcha.onepm(client, msg, msg.command[1], cursor)
        return

    await client.send_message(msg.chat.id, text=templates.Misc.start)


@client.on_message(filters.command('help'))
async def helpmsg(cli, msg):
    await client.send_message(msg.chat.id, text=templates.Inlines.basic, reply_markup=keyboards.Inlines.Help.basic)


@client.on_message(filters.command('ban'))
async def ban(cli, msg):
    chat_id = msg.chat.id
    try:
        sender = await client.get_chat_member(chat_id, msg.from_user.id)  # Проверка на права
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    uid = await admin.Restrictions.Ban.permanent(client, msg, chat_id)
    if uid is None:
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.pban).format(uid, msg.from_user.id, msg.chat.id, datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)
    logging.info(log)
    await client.send_message(logging_channel, log)


@client.on_message(filters.command('tban'))
async def tempban(cli, msg):
    chat_id = msg.chat.id
    try:
        sender = await client.get_chat_member(chat_id, msg.from_user.id)  # Проверка на права
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    uid = await admin.Restrictions.Ban.temp(client, msg, chat_id)
    if uid is None:
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.tban).format(uid[2], msg.from_user.id, msg.chat.id, uid[0], uid[1], datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)
    logging.info(log)
    await client.send_message(logging_channel, log)


@client.on_message(filters.command('unban'))
async def unban(cli, msg):
    chat_id = msg.chat.id
    try:
        sender = await client.get_chat_member(chat_id, msg.from_user.id)  # Проверка на права
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    uid = await admin.Restrictions.Ban.remove(client, msg, chat_id)
    if uid is None:
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.unban).format(uid, msg.from_user.id, msg.chat.id, datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)
    logging.info(log)
    await client.send_message(logging_channel, log)


@client.on_message(filters.command('mute'))
async def mute(cli, msg):
    chat_id = msg.chat.id
    try:
        sender = await client.get_chat_member(chat_id, msg.from_user.id)  # Проверка на права
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    uid = await admin.Restrictions.Mute.permanent(client, msg, chat_id)
    if uid is None:
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.pmute).format(uid, msg.from_user.id, msg.chat.id, datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)
    logging.info(log)
    await client.send_message(logging_channel, log)


@client.on_message(filters.command('tmute'))
async def tempmute(cli, msg):
    chat_id = msg.chat.id
    try:
        sender = await client.get_chat_member(chat_id, msg.from_user.id)  # Проверка на права
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    uid = await admin.Restrictions.Mute.temp(client, msg, chat_id)
    if uid is None:
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.tmute).format(uid, msg.from_user.id, msg.chat.id, uid[0], uid[1], datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)
    logging.info(log)
    await client.send_message(logging_channel, log)


@client.on_message(filters.command('unmute'))
async def unmute(cli, msg):
    chat_id = msg.chat.id
    try:
        sender = await client.get_chat_member(chat_id, msg.from_user.id)  # Проверка на права
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    uid = await admin.Restrictions.Mute.remove(client, msg, chat_id)
    if uid is None:
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.unmute).format(uid, msg.from_user.id, msg.chat.id, datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)
    logging.info(log)
    await client.send_message(logging_channel, log)


@client.on_message(filters.command('kick'))
async def kick(cli, msg):
    try:
        sender = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    except UserNotParticipant:
        return
    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    chat_id = msg.chat.id
    if not await admin.Restrictions.kick(client, msg, chat_id):
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.AdminActions.kick).format(msg.from_user.id, chat_id, datetime_now, datetime_now.timestamp(), msg.chat.title)

    await client.send_message(logging_channel, log)
    logging.info(log)


@client.on_message(filters.command('purge'))
async def purge(cli, msg):
    try:
        sender = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    except UserNotParticipant:
        return
    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    chat_id = msg.chat.id
    data = await admin.purge(client, msg, chat_id)
    if data[0]:
        datetime_now = datetime.now()
        log = str(templates.Logs.AdminActions.purge).format(msg.from_user.id, chat_id, data[1],
                                                                                data[2], datetime_now, datetime_now.timestamp(), msg.chat.title)

        await client.send_message(logging_channel, log)
        logging.info(log)


@client.on_message(filters.group & filters.command('voteban'))
async def voteban(cli, msg):
    if msg.reply_to_message is None:
        return
    await users.Votes.voteban(msg, cursor)


@client.on_message(filters.group & filters.command('votemute'))
async def votemute(cli, msg):
    if msg.reply_to_message is None:
        return
    await users.Votes.votemute(msg, cursor)


@client.on_message(filters.command('pin'))
async def pin(cli, msg):
    try:
        sender = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    await client.pin_chat_message(msg.chat.id, msg.reply_to_message.message_id, True)


@client.on_message(filters.command('unpin'))
async def unpin(cli, msg):
    try:
        sender = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    except UserNotParticipant:
        return

    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    await client.unpin_chat_message(msg.chat.id, msg.reply_to_message.message_id)


@client.on_message(filters.command('attack'))
async def ddos(cli, msg):
    try:
        sender = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    except UserNotParticipant:
        return
    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.Auto.ddos).format(msg.chat.id, msg.from_user.id, datetime_now, datetime_now.timestamp(), msg.chat.title)

    logging.info(log)
    await client.send_message(logging_channel, log)

    lastmsg = (await client.send_message(msg.chat.id, log, disable_notification=True, disable_web_page_preview=True)).message_id
    await client.pin_chat_message(msg.chat.id, lastmsg)

    under_attack.clear()
    under_attack.append(True)
    attack_message.clear()
    attack_message.append(lastmsg)


@client.on_message(filters.command('offattack'))
async def deddos(cli, msg):
    try:
        sender = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    except UserNotParticipant:
        return
    if sender.status not in misc.adminstatus or sender.can_restrict_members is False:
        await msg.reply(templates.Misc.norights)
        return

    if under_attack[0] is False:
        await msg.reply(templates.Misc.noddos)
        return

    datetime_now = datetime.now()
    log = str(templates.Logs.Auto.stopddos).format(msg.chat.id, msg.from_user.id, datetime_now,
                                                                datetime_now.timestamp(), msg.chat.title)

    await client.unpin_chat_message(msg.chat.id, attack_message[0])
    await client.send_message(msg.chat.id, log, disable_notification=False,
                              disable_web_page_preview=True)

    logging.info(log)
    await client.send_message(logging_channel, log)


    under_attack.clear()
    under_attack.append(False)

    attack_message.clear()
    attack_message.append(0)


@client.on_message(filters.new_chat_members)
async def trigger(cli, msg):
    if under_attack[0]:
        await client.ban_chat_member(msg.chat.id, msg.from_user.id, int(time() + 86400))
        datetime_now = datetime.now()

        log = str(templates.Logs.Auto.ddos_joined).format(msg.from_user.id, msg.chat.id, datetime_now,
                                                                     datetime_now.timestamp(), msg.chat.title)
        logging.info(log)
        await client.send_message(logging_channel, log)

        cursor.execute('INSERT INTO attackers(%s, %s, %s);', (msg.chat.id, msg.from_user.id, int(datetime.now().timestamp()),))
        return

    await auto.Captcha.redirect(client, msg, (await client.get_me()).username, cursor)


@client.on_message(filters.group)
async def message(cli, msg):
    if await auto.Flood.main(client, msg, 6, 5, cursor):
        await msg.reply(str(templates.Logs.Auto.flood).format(msg.from_user.id, msg.chat.id, msg.chat.title))
        # TODO: добавить функцианал


# Это функция, которая вставляет в БД данные чатов не в белом списке, чаты Leader TV в нем
@client.on_chat_member_updated()
async def leave(cli, msg: Message):
    if msg.new_chat_members is not None:
        for new_user in msg.new_chat_members:
            if new_user != (await client.get_me()).id:
                return

            if await auto.leave(client, msg, cursor):
                datetime_now = datetime.now()
                log = str(templates.Logs.Auto.unauthorized_chat).format(msg.from_user.id, msg.chat.title, msg.chat.id,
                                                                        datetime_now, datetime_now.timestamp())
                logging.info(log)
                await client.send_message(logging_channel, log)
                return

scheduler = AsyncIOScheduler()

scheduler.add_job(auto.Flood.clear, 'interval', seconds=5, args=[cursor])
scheduler.add_job(auto.Captcha.clear, 'interval', seconds=3, args=[client, cursor])
scheduler.add_job(users.Votes.Database.clear, 'interval', seconds=5, args=[client, cursor, cursor])

scheduler.start()

client.run()

logging.shutdown()
logging.info('\n\n')
scheduler.shutdown()

chatsConn.close()
