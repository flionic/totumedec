"""
Copyrights ©
Licensed by GNU GPL v3.0
Created date: 13 September 2017, 00:37
Project: E-declaration Bot
Created for: Totum
Created by: Bionic Inc
Official site: https://lisha.pro
"""
# -*- coding: utf-8 -*-
import os
import logging
import telegram
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

print('Copyrights © ⏤ E-declaration Bot for Totum by Bionic Inc 2017')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Main messages
msg_start = '*Оберіть необхідний розділ:*'
msg_contacts = '''
*Зворотній зв’язок*
_тел. для довідок:_ [+380685578758](call://+380685578758)
http://totum.com.ua/
'''


def cmd_start(bot, update):
    # Inline MainMenu
    main_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("Загальна інформація", callback_data='m1_1')],
        [InlineKeyboardButton("Об’єкти декларування", callback_data='m1_2')],
        [InlineKeyboardButton("Суттєві зміни у майновому стані", callback_data='m1_3')],
        [InlineKeyboardButton("Відповідальність", callback_data='m1_4')]
    ])
    update.message.reply_text(msg_start, reply_markup=main_menu, parse_mode="Markdown")
    bot.send_message(chat_id=update.message.chat_id, text=msg_contacts, parse_mode="Markdown")


def cmd_start_t(bot, update):
    # KeyboardMarkup MainMenu
    reply_keyboard = [
        ['Загальна інформація'],
        ['Об’єкти декларування'],
        ['Суттєві зміни у майновому стані'],
        ['Відповідальність']
    ]
    bot.send_message(chat_id=update.message.chat_id, text=msg_contacts + '\n\n' + msg_start, parse_mode="Markdown",
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


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
        dp.add_handler(CommandHandler('start_test', cmd_start_t))
        dp.add_handler(MessageHandler(Filters.text, cmd_start))

        # log all errors
        dp.add_error_handler(error)

        # Start Bot
        logger.info("Start bot")
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == '__main__':
    main()
