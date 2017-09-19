"""
Copyrights ©
Licensed by GNU GPL v3.0
Created date:       13 September 2017, 00:37
Project:            E-declaration Bot
Created for:        Totum
Created by:         Bionic Inc
Official site:      https://lisha.pro

Required Environment variables:
    token               # Telegram Bot Api Token
    admin_id            # For admin rules
    callback_chat_id    # Telegram chat id for callback info
Optional variables:
    test_mode = 1       # enable test mode
"""
# -*- coding: utf-8 -*-
import logging
from os import environ
from sqlite3 import connect, OperationalError
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.error import InvalidToken

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if environ.get('test_mode')
    else '%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
print('Copyrights © ⏤ E-declaration Bot for Totum by Bionic Inc 2017')

msg_contacts = f"📞 _Tел. для довідок:_ [+380685578758](call://+380685578758)\n💻 http://totum.com.ua/\n\n"
msg_hello = 'бот-помічник з питань електронного декларування для публічних осіб.'
md = ParseMode.MARKDOWN
chat_logs = environ.get('callback_chat_id')
keys_ctrl = [
    InlineKeyboardButton("️☎️ Зворотній зв’язок", callback_data='callback'),
    InlineKeyboardButton("ℹ️ Поділитися з друзями", switch_inline_query=f"– Це {msg_hello} Спробуй зараз!")
]
keys_main = [InlineKeyboardButton(" ↩️ НА ГОЛОВНУ ↩️ ", callback_data='main_menu')]


def cmd_start(bot, update):
    user = user_info(update)
    logging.info(f"User {user[1]} used /start command from chat {update.message.chat_id}")
    bot.send_message(text=f"{user[1]}\nнатиснув start", chat_id=chat_logs)  # Msg to callback chat
    bot.send_message(chat_id=update.message.chat_id, parse_mode=md, text=f"Вітаю, {user[0]}! Я – {msg_hello}")
    build_menu(bot, update)


def cmd_unknown(bot, update):
    del_menu(bot, update, 0)
    build_menu(bot, update, message='Мені дуже шкода, але я не розумію ваших повідомлень 😞')


def cmd_hidden(bot, update):
    bot.send_message(chat_id=update.message.chat_id, parse_mode=md,
                     text=f"© Разработчик Bionic Leha, September 2017. \nhttps://vk.com/farbio\nhttps://allpha.top\n"
                          f"[bionic.mods@gmail.com](mailto://bionic.mods@gmail.com)")


def callback_actions(bot, update):
    query = update.callback_query
    bot.edit_message_reply_markup(query.message.chat_id, message_id=query.message.message_id)
    msg = {'keys': InlineKeyboardMarkup([[InlineKeyboardButton(" ↩️ НА ГОЛОВНУ ↩️ ", callback_data='new_menu')]]),
           'text': '', 'id': query.message.chat_id}
    if "callback" == query.data:
        del_menu(bot, query)
        if query.message.chat.type == 'private':  # message for private
            bot.send_photo(msg['id'], reply_markup=msg['keys'], caption='🔎 Як відправити контакт?',
                           photo=open('doc/help_callback.png', 'rb'))  # photo-help
            msg['keys'] = ReplyKeyboardMarkup(
                [[KeyboardButton(text="Натисніть СЮДИ, щоб залишити свій контакт\n\n⭕️⭕️⭕️",
                                 request_contact=True)]])
            msg['text'] = '1. Натисніть на велику кнопку знизу.\n' \
                          '2. Підтвердіть відправку кнопкою "OK".\n\nОчікую натискання ⤵️'
        else:  # message for others
            msg['text'] = f'Для цієї дії, будь ласка, зверніться до мене в особисті повідомлення.\n' \
                          f'https://t.me/{bot.username}'
        bot.send_message(msg['id'], text=msg['text'], reply_markup=msg['keys'], parse_mode=md)  # Help message
    else:
        build_menu(bot, query, str(query.data))


def build_menu(bot, update, callback=None, message=''):
    tg = update.message
    try:
        data = connect('data.sql')
        c = data.cursor()
        c.execute("SELECT title, description FROM menu WHERE id=?", (callback,))
        doc = c.fetchone()
        msg = {'text': f"\n\n📂 Розділ: *{doc[0]}*" if doc else message + "\n\n🗃 *Оберіть необхідний розділ:*", 'keys': [],
               'reply_id': None, 'type': None, 'buttons': []}
        if doc and doc[1]:  # if description exist
            del_menu(bot, update)
            msg['reply_id'] = tg.message_id+2
            msg['text'] = "\n\n🗃 *Оберіть необхідний розділ:*"
            if doc[1].startswith('set_pic='):  # send photo if exist
                bot.send_photo(tg.chat_id, open('doc/' + doc[1].replace('set_pic=', ''), 'rb'), caption="🔎 " + doc[0])
            else:  # send document
                tg.reply_text(f"📄 *{doc[0]}*\n\n{doc[1]}", parse_mode=md)  # MSG Doc
        else:  # generate menu
            sql = "SELECT description NOTNULL, title, id FROM menu WHERE parent_id"
            sql = [sql + "=?", (callback,)] if doc is not None else [sql + " IS NULL", '']
            for row in c.execute(sql[0], sql[1]):
                msg['keys'].append(InlineKeyboardButton(("📄 " if row[0] else "📁 ") + row[1], callback_data=str(row[2])))
            data.close()
            n_cols = 2 if len(msg['keys']) > 7 else 1
            msg['keys'] = [msg['keys'][i:i + n_cols] for i in range(0, len(msg['keys']), n_cols)]
        msg['keys'].append(keys_ctrl)
        msg['keys'].append(keys_main) if doc else None
        if msg['reply_id'] or (callback == 'new_menu') or (callback is None):
            tg.reply_text(text=msg['text'], reply_markup=InlineKeyboardMarkup(msg['keys']), parse_mode=md)  # Menu
            tg.reply_text(f"{msg_contacts}", parse_mode=md)  # Contacts
        elif callback:
            bot.edit_message_text(msg['text'], tg.chat_id, tg.message_id, parse_mode=md,
                                  reply_markup=InlineKeyboardMarkup(msg['keys']))
    except OperationalError as msg:
        error(bot, update, f'Error with database ({msg})', name="sqlite3.OperationalError")


def callback_report(bot, update):
    del_menu(bot, update)
    user = user_info(update)
    user_phone = update.message.contact.phone_number
    logging.info(f'Callback request from: {user[1]} {user_phone}')
    bot.send_message(text=f'❗Отримано контактні дані:\n\n{user[1]}\n[+{user_phone}](call://+{user_phone})',
                     chat_id=chat_logs, parse_mode=md)  # Msg to callback chat)
    bot.send_message(chat_id=update.message.chat_id, parse_mode=md, reply_markup=ReplyKeyboardRemove(),
                     text=f"Дякуємо за звернення, *{user[0]}*. Ми зв'яжемося з Вами найближчим часом.")
    build_menu(bot, update)


def del_menu(bot, update, pl=1):
    try:
        if pl:
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id)
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id+1)
        else:
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id-1)
            bot.delete_message(update.message.chat_id, message_id=update.message.message_id-2)
    except Exception as excp:
        excp = excp


def user_info(update):
    user = update.message.from_user
    user.username = f' - @{user.username.replace("_", "&#95;")}' if user.username is not None else ''
    user.last_name = f' {user.last_name}' if user.last_name is not None else ''
    return [user.first_name, user.first_name + user.last_name + user.username]


def error(bot, update, error, name=None):  # extended logger
    if name:
        logging.getLogger(name).critical(error)
        bot.send_message(chat_id=update.message.chat_id, parse_mode=md, text='Упс! Виникла помилка',
                         reply_markup=InlineKeyboardMarkup([keys_main]))  # Menu
        bot.send_message(chat_id=chat_logs, parse_mode=md, text=f'⚠️ Произошла ошибка с *{name}*\n\n{error}')
    elif update:  # Avoid duplications
        logger.warning('%s' % error)


def main():
    try:  # Create EventHandler
        updater = Updater(environ.get('token'))
        dp = updater.dispatcher
    except InvalidToken:
        logger.critical("Token is invalid")
    except ValueError:
        logger.critical("Token not given. Please, setup environment variables or check settings.py")
    else:
        # Add bot handlers
        dp.add_handler(CommandHandler('start', cmd_start))
        dp.add_handler(CommandHandler(['bionic', 'dev'], cmd_hidden))
        dp.add_handler(MessageHandler(Filters.contact, callback_report))
        dp.add_handler(CallbackQueryHandler(callback_actions))
        dp.add_handler(MessageHandler(Filters.all, cmd_unknown))
        # Extend logging
        dp.add_error_handler(error)
        # Start Bot
        logger.info("Start bot on @%s" % updater.bot.username)
        updater.start_polling()


if __name__ == '__main__':
    main()
