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
    This module handles the Telegram bot when deployed to a regular server. This variant implements its own web server
    to process the webhook requests. If you intend to deply your bot to the Google App Engine platform then you should
    choose the alternative telegram_bot_gae.py module. That option is controlled by setting the use_app_engine variable
    to True in the config.py module.
"""

from bot.app.controllers.logger import *
import bot.app.config as config
import bot.app.secrets as secrets
from bot.app.controllers import calculations
from app.views.l10n import locales, remove_tildes
from telegram.ext import Updater
from telegram.ext import CommandHandler


# Set version
__version__ = (1, 0, 0)

# Start logger
logger = logging.getLogger(__name__)

# Get secret token
tgm_token = secrets.telegram_token

# Shorten locale path
lang = locales[config.bot_locale]
lang_tgm = lang['Telegram']['commands']
lang_commands = lang['calculations']['commands']
lang_log_msg = lang['log_msgs']

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
logging.info(msg=lang_log_msg['server_softw'].format(config.server_software))
logging.info(msg=lang_log_msg['working_dir'].format(config.working_dir))
logging.info(msg=lang_log_msg['use_app_eng'].format(config.use_app_engine))
logging.info(msg=lang_log_msg['app_eng_server'].format(config.app_engine_server))
logging.info(msg=lang_log_msg['rev_proxy'].format(config.reverse_proxy_port))

# Set default value for params variable
params = None

# Define Updater, bot and dispatcher objects
updater = Updater(token=tgm_token, use_context=True)
bot = updater.bot
dispatcher = updater.dispatcher


# Beginning of function definitions #

# Define handler functions
# Handler function for the /start command
def start_handler(update, context):
    """
    This function handles the 'start' command, replying with a greeting message that presents the user with a brief
    description of the purpose of this bot.

    :param update: This is the Telegram update that contains the command and the message data received by the bot
    (e.g. user who sent it, chat ID, etc.)
    :type update: telegram.Update
    :param context: This is the context bot object that will communicate with Telegram servers
    :type context: context
    :return: No usable data is returned by this function
    :rtype: None
    """

    # Send 'description' reply to user
    context.bot.send_message(chat_id=update.message.chat_id, text=lang_tgm['start']['name'])


def help_me_handler(bot_instance, update):  # ToDo: Check if this should be rewritten to use context instead
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


def webhook_handler(update, context):  # ToDo: Check if the 'context' parameter is actually necessary
    """
    This function handles all commands that request date/time calculations, detecting what information was requested by
    the user, getting data from the calculations module and then sending it back to the user as a chat message.

    :param update: This is the Telegram update that contains the command and the message data received by the bot
    (e.g. user who sent it, chat ID, etc.)
    :type update: telegram.Update
    :param context: This is the context bot object that will communicate with Telegram servers
    :type context: context
    :return: No usable data is returned by this function
    :rtype: str
    """

    # Shorten variable names
    chat_id = update.message.chat.id
    user_request = update.message.text

    # Log debugging messages
    logging.debug(msg=lang_log_msg['wh_chat_id'].format(chat_id))
    logging.debug(msg=lang_log_msg['wh_user_req'].format(user_request))

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
    logging.info(msg=lang_log_msg['wh_reply'].format(reply))

    # Send reply to user and exit
    updater.bot.sendMessage(chat_id=chat_id, text=reply)

    return 'OK'


def start_updater(domain, port, tgm_url, tgm_webhook, certificate=None, private_key=None, run_locally=True):
    """
    This function starts an internal server (linked to the updater object) that receives information from Telegram
    at the webhook URL. This server registers the webhook URL with Telegram servers automatically, therefore it should
    be used on its own. Do not use it along with the standalone function that only registers the webhook!

    :param domain: This is the domain where this web server will listen for requests
    :type domain: str
    :param port: This is the port where this web server will listen for requests
    :type port: str
    :param tgm_url: This is the part of the URL (excluding domain name) where this web server will listen for webhook
    requests
    :type tgm_url: str
    :param tgm_webhook: This is the URL where the webhook will be set (including domain name) that will be informed to
    Telegram servers
    :type tgm_webhook: str
    :param certificate: This is the path to the public certificate file that will be uploaded to Telegram servers
    :type certificate: str
    :param private_key: This is the path to the private key file that will be used to validate the requests sent by
    Telegram servers to the webhook URL
    :type private_key: str
    :param run_locally: This indicates whether this will run in a local development server or not
    :type run_locally: bool
    :return: No usable data is returned by this function
    :rtype: None
    """

    # Log that the web server has been started
    logging.info(msg=lang_log_msg['start_wh_server'])

    # Check whether this bot is running in a local development environment and start web server with appropriate values
    if run_locally:
        updater.start_webhook(listen=domain, port=port, cert=certificate, key=private_key, url_path=tgm_url,
                              webhook_url=tgm_webhook)
    else:
        updater.start_webhook(listen="0.0.0.0", port=port, url_path=tgm_url, webhook_url=tgm_webhook)

    # Set the server to wait idly for new updates
    updater.idle()


def set_webhook_now(tgm_webhook, cert_file):
    """
    This is a standalone function that may be used on its own to register a webhook URL with Telegram servers. It can
    be used only if the internal server is not used!

    :param tgm_webhook: This is the URL that will be used for setting a webhook and needs to be informed to Telegram
    servers
    :type tgm_webhook: str
    :param cert_file: This is the path to the public certificate file that will be uploaded to Telegram servers
    :type cert_file: str
    :return: No usable data is returned by this function
    :rtype: None
    """

    # Set the webhook by informing Telegram servers of the URL and upload the public certificate
    updater.bot.set_webhook(url=tgm_webhook, certificate=cert_file)

    # Set the server to wait idly for new updates
    updater.idle()


# End of functions definitions #

# Telegram only accepts English characters so check if any of the calculations commands for this locale have an
# alternate spelling for Telegram and then copy all other commands to lang_tgm
# common_commands = set(filter(lambda command: command not in lang_tgm, lang_commands))
# for item in common_commands:  # ToDo: Fix this!!! It's different from the GAE version!
#     lang_tgm[item] = lang_commands[item]

# Define command handlers for every command and link them to handler functions
start_handler = CommandHandler(lang_tgm['start']['name'], start_handler())
help_handler = CommandHandler(lang_tgm['help']['name'], help_me_handler)
date_handler = CommandHandler(lang_tgm['date'], webhook_handler)
summary_handler = CommandHandler(lang_tgm['summary'], webhook_handler)
years_handler = CommandHandler(lang_tgm['years'], webhook_handler)
months_handler = CommandHandler(lang_tgm['months'], webhook_handler)
days_handler = CommandHandler(lang_tgm['days'], webhook_handler)
hours_handler = CommandHandler(lang_tgm['hours'], webhook_handler)
minutes_handler = CommandHandler(lang_tgm['minutes'], webhook_handler)
seconds_handler = CommandHandler(lang_tgm['seconds'], webhook_handler)

# Register command handlers with the dispatcher service
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(date_handler)
dispatcher.add_handler(summary_handler)
dispatcher.add_handler(years_handler)
dispatcher.add_handler(months_handler)
dispatcher.add_handler(days_handler)
dispatcher.add_handler(hours_handler)
dispatcher.add_handler(minutes_handler)
dispatcher.add_handler(seconds_handler)
logging.info(msg=lang_log_msg['handlers_added'])

