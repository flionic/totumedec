import os
import logging
import telegram
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

print('TOTUM E-declaration Bot — © Bionic Inc 2017')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

msg_start = '*Оберіть необхідний розділ:*'
msg_contacts = '''
*Зворотній зв’язок*
_тел. для довідок:_ [+380685578758](call://+380685578758)
http://totum.com.ua/
'''


def set_cmd():
    dispatcher.add_handler(CommandHandler('start', cmd_start))
    dispatcher.add_handler(CommandHandler('start_test', cmd_start_t))
    dispatcher.add_handler(MessageHandler(Filters.text, cmd_start))


def cmd_start(bot, update):
    main_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("Загальна інформація", callback_data='m1_1')],
        [InlineKeyboardButton("Об’єкти декларування", callback_data='m1_2')],
        [InlineKeyboardButton("Суттєві зміни у майновому стані", callback_data='m1_3')],
        [InlineKeyboardButton("Відповідальність", callback_data='m1_4')]
    ])
    update.message.reply_text(msg_start, reply_markup=main_menu, parse_mode="Markdown")
    bot.send_message(chat_id=update.message.chat_id, text=msg_contacts, parse_mode="Markdown")


def cmd_start_t(bot, update):
    reply_keyboard = [
        ['Загальна інформація'],
        ['Об’єкти декларування'],
        ['Суттєві зміни у майновому стані'],
        ['Відповідальність']
    ]
    bot.send_message(chat_id=update.message.chat_id, text=msg_contacts, parse_mode="Markdown")
    bot.send_message(chat_id=update.message.chat_id, text=msg_start, parse_mode="Markdown",
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


try:
    updater = Updater(token=os.environ.get('token'))
    dispatcher = updater.dispatcher
except ValueError:
    print('Error, token was not found')
except telegram.error.InvalidToken:
    print('Update error: Invalid token')
else:
    print('Start polling')
    set_cmd()
    updater.start_polling()
