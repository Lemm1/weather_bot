#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Telegram bot for determine current weather at certain city.
For determine weather using OpenWeatherMap API.
Wrapper telegram bot is python-telegram-bot (https://github.com/python-telegram-bot)
"""
import logging
import os

import pyowm

from telegram.ext import CommandHandler, Updater


TOKEN = "1307202527:AAHHqwfSTs-hPyKMyFrAhCZDJCIzLlU13Ic"
PORT = int(os.environ.get('PORT', '8443'))
MEASURING_SYSTEMS = {"SI": { "name":"International System of Units", "temperature":"celsius", "speed":"meters_sec" },
                     "customary": { "name": "United States customary units", "temperature":"fahrenheit", "speed":"miles_hour" }}
MEASURING_SYSTEM = MEASURING_SYSTEMS["SI"]



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Welcome, to get instructions on how to use bot type /help')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(f'''Your measuring system is set to {MEASURING_SYSTEM["Name"]}
Available measuring systems:
    SI - International System of Units, uses celsius and meters per second 
    customary - United States customary units, uses fahrenheits and miles per hour
To change measuring system type /measuring SI or /measuring customary

To check weather just type /weather and location for example /weather Lviv''')


def set_measuring(bot, update, args):
    measuring_system = "".join(str(x) for x in args)
    if measuring_system in MEASURING_SYSTEMS:
        global MEASURING_SYSTEM
        MEASURING_SYSTEM = MEASURING_SYSTEMS[measuring_system]
        update.message.reply_text(f'Changed your measuring system to {MEASURING_SYSTEM["Name"]}')
    else:
        update.message.reply_text("Cannot find measuring system. Did you spell it right?")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def weather(bot, update, args):
    """Define weather at certain location"""
    owm = pyowm.OWM('e81cde1ad29454eb6358e91ec760b09f')
    try:
        text_location = "".join(str(x) for x in args)
        w = owm.weather_manager().weather_at_place(text_location).weather
        humidity = w.humidity
        wind = w.wind(unit=MEASURING_SYSTEM["speed"])
        temp = w.temperature(unit=MEASURING_SYSTEM["temperature"])
        logger.info(f'''
        Temperature at {text_location}: {temp}
Wind at {text_location}: {wind}
Humidity at {text_location}: {humidity}
        ''')
        convert_temp = temp.get('temp')
        convert_wind = wind.get('speed')
        convert_humidity = humidity
        update.message.reply_text(f'''Temperature, {MEASURING_SYSTEM["temperature"]}: {str(convert_temp)}
Wind speed, {MEASURING_SYSTEM["speed"]}: {str(convert_wind)}
Humidity, %: {str(convert_humidity)}
''')
    except:
        update.message.reply_text("Cannot find location you requested. Did you spell it right?")


def polling_bot(updater):
    logger.info("Start polling")
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


def webhook_bot(updater):
    logger.info("Starting webhook")
    # start the bot with webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    # set webhook to our heroku app url
    updater.bot.set_webhook("https://weather-bot-122.herokuapp.com/" + TOKEN)

    updater.idle()


def main(use_webhooks):
    logger.info("starting bot")
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN, use_context=False)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("weather", weather, pass_args=True))
    dp.add_handler(CommandHandler("measuring", set_measuring, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    if use_webhooks:
        webhook_bot(updater)
    else:
        polling_bot(updater)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--use_webhooks', required=False, help='Use webhooks')
    args = parser.parse_args()
    main(use_webhooks=args.use_webhooks)
