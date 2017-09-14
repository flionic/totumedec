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
    else None + '%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
print('Copyrights © ⏤ E-declaration Bot for Totum by Bionic Inc 2017')

callback_chat = os.environ.get('callback_chat_id')
hello = 'Я – бот-помічник з питань електронного декларування для публічних осіб.'
contacts = f"_Tел. для довідок:_ [+380685578758](call://+380685578758)\nhttp://totum.com.ua/\n\n"

ctrl_keys = [
    InlineKeyboardButton("Зворотній зв’язок", callback_data='CB'),
    InlineKeyboardButton("Поділитися з друзями", switch_inline_query=hello)
]
menu_key = [InlineKeyboardButton(" - НА ГОЛОВНУ - ", callback_data='M0')]
main_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("Загальна інформація", callback_data='M1')],
    [InlineKeyboardButton("Об’єкти декларування", callback_data='M2')],
    [InlineKeyboardButton("Суттєві зміни у майновому стані", callback_data='t3')],
    [InlineKeyboardButton("Відповідальність", callback_data='t4')],
    ctrl_keys
])
menu_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton("Подання декларації", callback_data='t1_1')],
    [InlineKeyboardButton("Суб’єкти декларування", callback_data='t1_2')],
    [InlineKeyboardButton("Відповідальне становище", callback_data='t1_3')],
    [InlineKeyboardButton("Високий рівень корупційних ризиків", callback_data='t1_4')],
    [InlineKeyboardButton("Строк декларування", callback_data='t1_5')],
    [InlineKeyboardButton("Члени сім’ї", callback_data='t1_6')],
    [InlineKeyboardButton("Членство в організаціях", callback_data='t1_7')],
    ctrl_keys, menu_key
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
    ctrl_keys, menu_key
])


def cmd_start(bot, update):
    user = update.message.from_user
    logging.info(f"User @{user.username} ({user.first_name} {user.last_name}) used /start command "
                 f"from chat {update.message.chat_id}")
    bot.send_message(chat_id=callback_chat,
                     text=f"@{user.username} – {user.first_name} {user.last_name}\nнатиснув /start")
    bot.send_message(chat_id=update.message.chat_id, parse_mode="Markdown",
                     text=f"Вітаю! {hello}")
    cmd_menu(bot, update)


def cmd_menu(bot, update):
    update.message.reply_text(f"{contacts}*Оберіть необхідний розділ:*", reply_markup=main_menu, parse_mode="Markdown")


def buttons(bot, update):
    query = update.callback_query
    section = {'M0': ['Головна', main_menu],
               'M1': ['Загальна інформація', menu_1],
               'M2': ['Об’єкти декларування', menu_2]}
    if query.data in section:
        bot.edit_message_text(
            text=f"{contacts}Розділ: *{section[query.data][0]}*", reply_markup=section[query.data][1],
            chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode="Markdown")
    elif query.data == 'CB':
        req_cont = telegram.ReplyKeyboardMarkup(
            [[telegram.KeyboardButton(text="Залишити контакт", request_contact=True)]])
        bot.send_message(chat_id=query.message.chat_id, parse_mode="Markdown", reply_markup=req_cont,
                         text="Натисніть на кнопку і підтвердіть відправку, щоб ми передзвонили Вам")
    else:
        data = sqlite3.connect('data.sql')
        c = data.cursor()
        t = (query.data,)
        for row in c.execute("SELECT title, text FROM menu_texts WHERE name=?", t):
            bot.send_message(chat_id=query.message.chat_id, parse_mode="Markdown", text=f"*{row[0]}*\n\n{row[1]}")
            bot.send_message(text=contacts, reply_markup=InlineKeyboardMarkup([ctrl_keys, menu_key]),
                             chat_id=query.message.chat_id, parse_mode="Markdown")
        data.commit()
        data.close()


def cmd_callback(bot, update):
    user = update.message.contact
    logging.info(f'Callback request from @{update.message.from_user.username}, '
                 f'{user.first_name} {user.last_name}, {user.phone_number}')
    bot.send_message(chat_id=callback_chat,
                     text=f'Отримано контактні дані:\n'
                          f'{user.first_name} {user.last_name} – @{update.message.from_user.username}\n'
                          f'{user.phone_number}')
    cmd_menu(bot, update)
    bot.send_message(chat_id=update.message.chat_id, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(),
                     text=f"Дякуємо за звернення, *{user.first_name}*, ми зв'яжемося з Вами найближчим часом.")


def error(bot, update, error):
    logger.warn('%s - "%s"' % (error, update))


def main():
    # Create EventHandler and trying to pass it bot's token.
    try:
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

        # log all errors
        dp.add_error_handler(error)

        # Start Bot
        logger.info("Start bot")
        updater.start_polling()


if __name__ == '__main__':
    main()
