import telebot
from telebot import custom_filters
import global_variables as g

def set_tel_bot():

    bot = telebot.TeleBot(g.keys["telegram_api"])

    @bot.message_handler(chat_id=g.keys["telegram_user"], commands=['start'])
    def send_welcome(message):
        g.client.add_aditional(16)
        g.client.controler()
        bot.reply_to(message, "Okay, heating started!")

    bot.add_custom_filter(custom_filters.ChatFilter())

    bot.infinity_polling(timeout=70, long_polling_timeout = 60)

