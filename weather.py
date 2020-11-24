#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Telegram bot for determine current weather at certain city.
For determine weather using OpenWeatherMap API.
Wrapper telegram bot is python-telegram-bot (https://github.com/python-telegram-bot)
"""

from telegram import ParseMode, MessageEntity, ChatAction, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext
import logging
import pyowm


TOKEN = "1307202527:AAHHqwfSTs-hPyKMyFrAhCZDJCIzLlU13Ic"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Welcome, to get instructions on how to use bot type /help')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Just type, for example, /weather Lviv')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def weather(bot, update, args):
    """Define weather at certain location"""
    owm = pyowm.OWM('e81cde1ad29454eb6358e91ec760b09f')
    try:
        text_location = "".join(str(x) for x in args)
        observation = owm.weather_manager().weather_at_place(text_location)
        w = observation.weather
        humidity = w.humidity
        wind = w.wind(unit='meters_sec')
        temp = w.temperature(unit='celsius')
        print(temp)
        print(wind)
        convert_temp = temp.get('temp')
        convert_wind = wind.get('speed')
        convert_humidity = humidity
        text_temp = str(convert_temp)
        text_wind = str(convert_wind)
        text_humidity = str(convert_humidity)
        update.message.reply_text("Temperature, celsius: {}".format(text_temp))
        update.message.reply_text("Wind speed, m/s: {}".format(text_wind))
        update.message.reply_text("Humidity, %: {}".format(text_humidity))
    except:
        update.message.reply_text("Cannot find location you requested. Did you spell it right?")


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN, use_context=False)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("weather", weather, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
