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
import os
import logging
import sqlite3
import telegram
from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if os.environ.get('test_mode')
    else '%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
print('Copyrights © ⏤ E-declaration Bot for Totum by Bionic Inc 2017')

callback_chat = os.environ.get('callback_chat_id')
msg_hello = 'бот-помічник з питань електронного декларування для публічних осіб.'
msg_contacts = f"_Tел. для довідок:_ [+380685578758](call://+380685578758)\nhttp://totum.com.ua/\n\n"
msg_getSection = "*Оберіть необхідний розділ:*"

keys_ctrl = [
    InlineKeyboardButton("️☎️ Зворотній зв’язок", callback_data='CB'),
    InlineKeyboardButton("ℹ️ Поділитися з друзями", switch_inline_query=f"– Це {msg_hello} Спробуй зараз!")
]
keys_main = [InlineKeyboardButton(" ↩️ НА ГОЛОВНУ ↩️ ", callback_data='M0')]
menu_main = InlineKeyboardMarkup([
    [InlineKeyboardButton("📁 Загальна інформація", callback_data='M1')],
    [InlineKeyboardButton("📁 Об’єкти декларування", callback_data='M2')],
    [InlineKeyboardButton("📄 Суттєві зміни у майновому стані", callback_data='t3')],
    [InlineKeyboardButton("📄 Відповідальність", callback_data='t4')],
    keys_ctrl
])
menu_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton("Подання декларації", callback_data='t1_1')],
    [InlineKeyboardButton("Суб’єкти декларування", callback_data='t1_2')],
    [InlineKeyboardButton("Відповідальне становище", callback_data='t1_3')],
    [InlineKeyboardButton("Високий рівень корупційних ризиків", callback_data='t1_4')],
    [InlineKeyboardButton("Строк декларування", callback_data='t1_5')],
    [InlineKeyboardButton("Члени сім’ї", callback_data='t1_6')],
    [InlineKeyboardButton("Членство в організаціях", callback_data='t1_7')],
    keys_ctrl, keys_main
])
menu_2 = InlineKeyboardMarkup([
    [InlineKeyboardButton("Нерухоме майно", callback_data='t2_1')],
    [InlineKeyboardButton("Об’єкти незавершеного будівництва", callback_data='t2_2')],
    [InlineKeyboardButton("Цінне рухоме майно", callback_data='t2_3'),
     InlineKeyboardButton("Транспортні засоби", callback_data='t2_4')],
    [InlineKeyboardButton("Цінні папери ", callback_data='t2_5'),
     InlineKeyboardButton("Нематеріальні активи", callback_data='t2_6')],
    [InlineKeyboardButton("Корпоративні права", callback_data='t2_7'),
     InlineKeyboardButton("Доходи", callback_data='t2_8')],
    [InlineKeyboardButton("Подарунки", callback_data='t2_9'),
     InlineKeyboardButton("Грошові активи", callback_data='t2_10')],
    [InlineKeyboardButton("Фінансові зобов’язання", callback_data='t2_11'),
     InlineKeyboardButton("Видатки та правочини", callback_data='t2_12')],
    [InlineKeyboardButton("Робота за сумісництвом", callback_data='t2_13')],
    keys_ctrl, keys_main
])


def cmd_start(bot, update):
    user = user_info(update)
    logging.info(f"User{user[1]} used /start command from chat {update.message.chat_id}")
    bot.send_message(text=f"{user[1]}\nнатиснув start", chat_id=callback_chat)  # Msg to callback chat
    bot.send_message(chat_id=update.message.chat_id, parse_mode="Markdown", text=f"Вітаю, {user[0]}! Я – {msg_hello}")
    cmd_menu(bot, update)


def cmd_menu(bot, update):
    update.message.reply_text(f"{msg_getSection}", reply_markup=menu_main, parse_mode="Markdown")  # Menu
    bot.send_message(chat_id=update.message.chat_id, parse_mode="Markdown", text=f"{msg_contacts}")  # Contacts


def buttons(bot, update):
    query = update.callback_query
    section = {'M0': ['Головна', menu_main],
               'M1': ['Загальна інформація', menu_1],
               'M2': ['Об’єкти декларування', menu_2]}  # Menu subsections
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)  # Delete old menu
    if query.data in section:  # picked section of menu
        bot.send_message(
            text=f"📂 Розділ: *{section[query.data][0]}*", reply_markup=section[query.data][1],
            chat_id=query.message.chat_id, parse_mode="Markdown")  # Menu keys
    elif query.data == 'CB':  # picked callback
        if query.message.chat.type == 'private':  # message for private
            bot.send_photo(chat_id=query.message.chat_id, photo=open('doc/help_callback.png', 'rb'))  # photo-help
            req_cont = telegram.ReplyKeyboardMarkup(
                [[telegram.KeyboardButton(text="Натисніть СЮДИ, щоб залишити свій контакт\n\n⭕️⭕️⭕️",
                                          request_contact=True)]])
            bot.send_message(chat_id=query.message.chat_id, parse_mode="Markdown", reply_markup=req_cont,
                             text='1. Натисніть на велику кнопку знизу.\n'
                                  '2. Підтвердіть відправку кнопкою "OK".\n\nОчікую натискання ⤵️')  # Help message
        else:  # message for others
            bot.send_message(chat_id=query.message.chat_id, reply_markup=menu_main,
                             text=f'Для цієї дії, будь ласка, зверніться до мене в особисті повідомлення.\n'
                                  f'https://t.me/{bot.username}')
    else:  # picked text
        data = sqlite3.connect('data.sql')
        c = data.cursor()
        t = (query.data,)
        for row in c.execute("SELECT title, text FROM menu_texts WHERE name=?", t):
            bot.send_message(chat_id=query.message.chat_id, parse_mode="Markdown",
                             text=f"*{row[0]}*\n\n{row[1]}")  # print text
            bot.send_message(chat_id=query.message.chat_id, parse_mode="Markdown", text=msg_getSection,
                             reply_markup=InlineKeyboardMarkup([keys_ctrl, keys_main]))  # Menu keys
            bot.send_message(text=msg_contacts, chat_id=query.message.chat_id, parse_mode="Markdown")  # Contacts
        data.commit()
        data.close()


def cmd_callback(bot, update):
    user = user_info(update)
    user_phone = update.message.contact.phone_number
    logging.info(f'Callback request from: {user[1]} {user_phone}')
    bot.send_message(chat_id=callback_chat, parse_mode="Markdown",  # Msg to callback chat
                     text=f'❗Отримано контактні дані:\n\n{user[1]}' +
                          f'\n[+{user_phone}](call://+{user_phone})')
    bot.send_message(chat_id=update.message.chat_id, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(),
                     text=f"Дякуємо за звернення, *{user[0]}*, ми зв'яжемося з Вами найближчим часом.")
    cmd_menu(bot, update)


def user_info(update):
    user = update.message.from_user
    user.username = f' - @{user.username.replace("_", "&#95;")}' if user.username is not None else ''
    user.last_name = f' {user.last_name}' if user.last_name is not None else ''
    return [user.first_name, user.first_name + user.last_name + user.username]


def error(bot, update, error):  # extended logger
    if update:  # Avoid duplications
        logger.warning('%s' % error)


def main():
    try:  # Create EventHandler
        updater = Updater(token=os.environ.get('token'))
        dp = updater.dispatcher
    except ValueError:
        logger.error("Token was not found")
    except telegram.error.InvalidToken:
        logger.exception("Token is invalid")
    else:
        # Add bot handlers
        dp.add_handler(CommandHandler('start', cmd_start))
        dp.add_handler(MessageHandler(Filters.text, cmd_menu))
        dp.add_handler(MessageHandler(Filters.contact, cmd_callback))
        dp.add_handler(CallbackQueryHandler(buttons))

        # Extend logging
        dp.add_error_handler(error)

        # Start Bot
        logger.info("Start bot")
        updater.start_polling()


if __name__ == '__main__':
    main()
