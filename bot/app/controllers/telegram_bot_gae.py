#
# Event Info Bot - Bot service software for Telegram and Twitter to provide user with
#                  reminders of event date and info on request
#
# Copyright (C) 2019 Tiktaalik (Rodrigo Gambra-Middleton)
#                    Address your enquiries to: info@tiktaalik.dev
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""
    This module handles the Telegram bot when deployed to the Google App Engine platform (or similar). This variant
    relies on the platform providing an outward-facing web server that forwards requests to an internal web server
    where these requests are captured using the Flask framework, which then handles them to the Telegram CommandHandler
    library. If your server doesn't provide its own web server choose the alternative telegram_bot.py module. That
    option is controlled by setting the use_app_engine variable to False in the config.py module.
"""
from bot.app.controllers.logger import *
from queue import Queue
from threading import Thread
from bot.app.views.l10n import locales, remove_tildes
from telegram import Bot, Update, error
import bot.app.config as config
import bot.app.secrets as secrets
from bot.app.controllers import calculations
from bot.app.launcher import params, set_remote_params
from telegram.ext import Dispatcher, CommandHandler


# Set version
__version__ = (1, 0, 0)

# Start logger
logger = logging.getLogger(__name__)

# Shorten locale path
lang = locales[config.bot_locale]
lang_tgm = lang['Telegram']['commands']
lang_commands = lang['calculations']['commands']
lang_log_msg = lang['log_msgs']
lang_site_msg = lang['site_msgs']

# Telegram only accepts English characters so check if any of the calculations commands for this locale have an
# alternate spelling in Telegram commands and then copy all other commands to lang_tgm
alternate_commands = set(filter(lambda command: command in lang_commands, lang_tgm))
for item in lang_commands:
    if item not in lang_tgm:
        lang_tgm[item] = lang_commands[item]

    # Log debugging info
    logger.debug(msg='\n\nitem is: {0}'.format(item))
    logger.debug(msg='\n\nlang_tgm[item] is: {0}'.format(lang_tgm[item]))

# Log debugging info
logger.debug(msg='\n\nalternate_commands is: {0}'.format(list(alternate_commands)))
logger.debug(msg='\n\nlang_tgm is: {0}'.format(lang_tgm))

# Log informative messages about the current server setup
logger.info(msg=lang_log_msg['server_softw'].format(config.server_software))
logger.info(msg=lang_log_msg['working_dir'].format(config.working_dir))
logger.info(msg=lang_log_msg['use_app_eng'].format(config.use_app_engine))
logger.info(msg=lang_log_msg['app_eng_server'].format(config.app_engine_server))
logger.info(msg=lang_log_msg['rev_proxy'].format(config.reverse_proxy_port))

# Set global variables
tgm_token = secrets.telegram_token

# Create bot, update queue and dispatcher instances
telegram_bot = Bot(tgm_token)
tgm_update_queue = Queue()
tgm_dispatcher = Dispatcher(telegram_bot, tgm_update_queue)


# Beginning of function definitions #


def start_handler(bot_instance, update):
    """
    This function handles the 'start' command, replying with a greeting message that presents the user with a brief
    description of the purpose of this bot.

    :param bot_instance: This is the bot object previously initiated that will communicate with Telegram servers
    :type bot_instance: telegram.Bot
    :param update: This is the Telegram update that contains the command and the message data received by the bot (e.g.
    user who sent it, chat ID, etc.)
    :type update: telegram.Update
    :return: No usable data is returned by this function
    :rtype: None
    """

    # Shorten variable name
    chat_id = update.message.chat.id

    # Send 'description' reply to user
    bot_instance.send_message(chat_id=chat_id, text=lang_tgm['start']['reply'])


def help_me_handler(bot_instance, update):
    """
    This function handles the 'help' command, replying with a message that lists the instructions and all available
    user commands.

    :param bot_instance: This is the bot object previously initiated that will communicate with Telegram servers
    :type bot_instance: telegram.Bot
    :param update: This is the Telegram update that contains the command and the message data received by the bot (e.g.
    user who sent it, chat ID, etc.)
    :type update: telegram.Update
    :return: No usable data is returned by this function
    :rtype: None
    """

    # Shorten variable name
    chat_id = update.message.chat.id

    # Send 'help' (instructions) reply to user
    bot_instance.send_message(chat_id=chat_id, text=lang_tgm['help']['reply'])


def set_webhook_handler():
    """
    This function communicates with Telegram servers to inform them of the URL that will be used as a webhook where they
    should send all updates intended for this bot.

    :return: No usable data is returned by this function
    :rtype: True
    """

    # Shorten variable names
    webhook_url = params['tgm_webhook']
    cert_file = params['cert_file']

    # Log useful info
    logger.info(msg='webhook_url is: {0}'.format(webhook_url))
    logger.info(msg='cert_file is: {0}'.format(cert_file))

    # Try to set a webhook
    try:
        hook = telegram_bot.setWebhook(url=webhook_url, certificate=cert_file)

    except error.BadRequest as e:
        # If it fails to set a webhook log the exception
        logger.exception(msg=lang_log_msg['exception_occurred'].format(e))

        # Make sure the appropriate values have been set for the remote (GAE) runtime variables
        set_remote_params(gae=True)

        # Try setting the webhook again
        set_webhook_handler()

    else:
        # If setting the webhook succeeded, log the result and exit
        logger.info(msg=lang_log_msg['webhook_result'].format(hook))

        return True


def webhook_updater(request_data):
    """
    This function loads the request data into the Updater object and links the update with the bot instance.

    :param request_data: This is the actual HTTP request data as provided by the web server
    :type request_data: flask.request
    :return: No usable data is returned by this function
    :rtype: str
    """

    # Process the HTTP request data to convert it to JSON text and then to a Telegram update format
    update = Update.de_json(request_data.get_json(force=True), bot=telegram_bot)

    # Load update in the queue and exit
    tgm_update_queue.put(item=update)

    return 'OK'


def webhook_handler(bot_instance, update):
    """
    This function handles all commands that request date/time calculations, detecting what information was requested by
    the user, getting data from the calculations module and then sending it back to the user as a chat message.

    :param bot_instance: This is the bot object previously initiated that will communicate with Telegram servers
    :type bot_instance: telegram.Bot
    :param update: This is the Telegram update that contains the command and the message data received by the bot (e.g.
    user who sent it, chat ID, etc.)
    :type update: telegram.Update
    :return: No usable data is returned by this function
    :rtype: str
    """

    # Shorten variable names
    chat_id = update.message.chat.id
    user_request = update.message.text

    # Log debugging messages
    logger.debug(msg=lang_log_msg['wh_chat_id'].format(chat_id))
    logger.debug(msg=lang_log_msg['wh_user_req'].format(user_request))

    # As Telegram commands may be different due to their lack of support for non-English characters, we have to
    # translate the command again to one that the calculations module is actually able to understand
    # First remove the '/' sign from the text message
    user_command = user_request.split(sep='/', maxsplit=1)[1]

    # Get the dictionary key whose value matches the user command in the list of available commands
    user_command_key = list(filter(lambda item_key: lang_tgm[item_key] == user_command, lang_commands))[0]

    # Normalise the text by removing tildes and converting all letters to lowercase
    normalised_command = remove_tildes(word=lang_commands[user_command_key])

    # Get the calculation info related to the user command to prepare a reply
    reply = calculations.get_date(normalised_command)

    # Log debugging info for the reply
    logger.debug(msg=lang_log_msg['wh_reply'].format(reply))

    # Send reply to user and exit
    bot_instance.sendMessage(chat_id=chat_id, text=reply)

    return 'OK'


def check_token_details_handler():
    """
    This is a convenience function intended for easily checking whether this bot is able to correctly communicate with
    Telegram servers when setting it up. It asks their server for a brief summary of your bot information associated to
    the token provided.

    :return: No usable data is returned by this function
    :rtype: None
    """

    # Return token info to display it in the web browser
    return telegram_bot.get_me().to_json()


# End of functions definitions #

# Define handlers. ToDo: Try to turn this into one single command
start_command_handler = CommandHandler(lang_tgm['start']['name'], start_handler)
help_command_handler = CommandHandler(lang_tgm['help']['name'], help_me_handler)
date_command_handler = CommandHandler(lang_tgm['date'], webhook_handler)
summary_command_handler = CommandHandler(lang_tgm['summary'], webhook_handler)
years_command_handler = CommandHandler(lang_tgm['years'], webhook_handler)
months_command_handler = CommandHandler(lang_tgm['months'], webhook_handler)
days_command_handler = CommandHandler(lang_tgm['days'], webhook_handler)
hours_command_handler = CommandHandler(lang_tgm['hours'], webhook_handler)
minutes_command_handler = CommandHandler(lang_tgm['minutes'], webhook_handler)
seconds_command_handler = CommandHandler(lang_tgm['seconds'], webhook_handler)

# Register command handlers with the dispatcher service
tgm_dispatcher.add_handler(start_command_handler)
tgm_dispatcher.add_handler(help_command_handler)
tgm_dispatcher.add_handler(summary_command_handler)
tgm_dispatcher.add_handler(years_command_handler)
tgm_dispatcher.add_handler(months_command_handler)
tgm_dispatcher.add_handler(days_command_handler)
tgm_dispatcher.add_handler(hours_command_handler)
tgm_dispatcher.add_handler(minutes_command_handler)
tgm_dispatcher.add_handler(seconds_command_handler)
tgm_dispatcher.add_handler(date_command_handler)
logger.info(msg=lang_log_msg['tgm_handlers_added'])

# Create and start a threaded process to process updates
thread = Thread(target=tgm_dispatcher.start, name='tgm_dispatcher')
thread.start()
