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
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from  telegram import InputContactMessageContent
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, Filters

print('Copyrights © ⏤ E-declaration Bot for Totum by Bionic Inc 2017')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Main messages
msg_start = "Вітаю! Я – бот-помічник з питань електронного декларування для публічних осіб."
msg_getSection = "*Оберіть необхідний розділ:*"
msg_contacts = """
_тел. для довідок:_ [+380685578758](call://+380685578758)
http://totum.com.ua/
"""
msg_callback = f"Дякуємо за звернення, *%s*, ми зв'яжемося з Вами найближчим часом."

menu = {
    'M1': {'name': 'Загальна інформація', 'keys': InlineKeyboardMarkup([
        [InlineKeyboardButton("Подання декларації", callback_data='t1_1')],
        [InlineKeyboardButton("Суб’єкти декларування", callback_data='t1_2')],
        [InlineKeyboardButton("Відповідальне становище", callback_data='t1_3')],
        [InlineKeyboardButton("Високий рівень корупційних ризиків", callback_data='t1_4')],
        [InlineKeyboardButton("Строк декларування", callback_data='t1_5')],
        [InlineKeyboardButton("Члени сім’ї", callback_data='t1_6')],
        [InlineKeyboardButton("Членство в організаціях", callback_data='t1_7')]])},
    'M2': {'name': 'Об’єкти декларування', 'keys': InlineKeyboardMarkup([
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
        [InlineKeyboardButton("Робота за сумісництвом", callback_data='t2_13')]])},
    'M3': {'name': 'Суттєві зміни у майновому стані'},
    'M4': {'name': 'Відповідальність'}
}

main_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton(menu['M1']['name'], callback_data='M1')],
    [InlineKeyboardButton(menu['M2']['name'], callback_data='M2')],
    [InlineKeyboardButton(menu['M3']['name'], callback_data='M3')],
    [InlineKeyboardButton(menu['M4']['name'], callback_data='M4')]
])


def cmd_start(bot, update):
    user = update.message.from_user
    logging.info(f"User @{user.username} ({user.first_name} {user.last_name}) used /start command "
                 f"from chat {update.message.chat_id}")
    bot.send_message(chat_id=update.message.chat_id, text=msg_start, parse_mode="Markdown")
    cmd_menu(bot, update)


def cmd_menu(bot, update):
    # Inline MainMenu
    update.message.reply_text(msg_getSection, reply_markup=main_menu, parse_mode="Markdown")
    contact_kb = telegram.ReplyKeyboardMarkup(
        [[telegram.KeyboardButton(text="Головна")], [telegram.KeyboardButton(text="Зворотній зв'язок", request_contact=True)]])
    bot.send_message(chat_id=update.message.chat_id, text=msg_contacts, parse_mode="Markdown",
                     reply_markup=contact_kb)


def cmd_menu_t(bot, update):  # 2 variant
    # KeyboardMarkup MainMenu
    reply_keyboard = [[menu['M1']['name']], [menu['M2']['name']], [menu['M3']['name']], [menu['M4']['name']]]
    bot.send_message(chat_id=update.message.chat_id, text=f'{msg_contacts}\n\n{msg_getSection}', parse_mode="Markdown",
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def button(bot, update):
    query = update.callback_query
    if query.data in menu and 'keys' in menu[query.data]:
        bot.edit_message_text(text="Розділ: %s" % menu[query.data]['name'], reply_markup=menu[query.data]['keys'],
                              chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text(text="Розділ: %s" % msg_getSection, reply_markup=main_menu,
                              chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode="Markdown")


def cmd_callback(bot, update):
    user = update.message.contact
    logging.info(f'Callback request from @{update.message.from_user.username}, '
                 f'{user.first_name} {user.last_name}, {user.phone_number}')
    bot.send_message(chat_id=update.message.chat_id, parse_mode="Markdown", text=msg_callback % user.first_name)


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
        dp.add_handler(MessageHandler(Filters.text, cmd_menu))
        dp.add_handler(CommandHandler('start_test', cmd_menu_t))
        dp.add_handler(MessageHandler(Filters.contact, cmd_callback))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))

        # log all errors
        dp.add_error_handler(error)

        # Start Bot
        logger.info("Start bot")
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # ! updater.idle()


if __name__ == '__main__':
    main()
