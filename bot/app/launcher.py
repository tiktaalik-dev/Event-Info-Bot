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
This module is the hub that launches each one of the bots that you enabled in the config.py module, using appropriate
settings for either a local development environment or a production server.
"""


# [START gae_python37_app]
from bot.app.controllers.logger import *
import dns.resolver
import bot.app.config as config
from bot.app.views.l10n import locales

# Start logger
logger = logging.getLogger(__name__)

# Shorten locale path
lang = locales[config.bot_locale]
lang_tgm = lang['Telegram']['commands']
lang_log_msg = lang['log_msgs']

# Set a local collector variable for configuration data
params = {'domain': '', 'port': config.reverse_proxy_port, 'cert_path': '', 'private_key_path': '',
          'cert_file': '', 'key_file': '', 'tgm_url': config.bot_tgm_url, 'tgm_webhook_str': config.bot_tgm_webhook_str}


def set_remote_params(gae=False):
    """
    This function sets several server parameters to values that are required to run your bots in a production server
    (either a generic server or an instance in the Google App Engine platform).

    :param gae: Set this parameter to True if your bot will run in Google App Engine platform
    :type gae: bool
    """
    if gae:
        params['port'] = '443'
    params['domain'] = config.bot_domain
    params['cert_path'] = config.remote_certificate
    params['private_key_path'] = config.remote_private_key
    params['cert_file'] = open(file=params['cert_path'], mode='rb')
    params['key_file'] = open(file=params['private_key_path'], mode='rb')
    params['tgm_webhook'] = params['tgm_webhook_str'].format(params['domain'], params['port'], params['tgm_url'])
    logger.info(msg=lang_log_msg['bot_domain'].format(params['domain']))
    logger.info(msg=lang_log_msg['wh_url'].format(params['tgm_webhook']))
    logger.info(msg=lang_log_msg['remote_server_values'])


def set_local_params():
    """
    This function sets several server parameters to values that are appropriate to run your bots in a local development
    environment server.
    """
    params['domain'] = config.local_public_ip_address
    params['cert_path'] = config.local_certificate
    params['private_key_path'] = config.local_private_key
    params['cert_file'] = open(file=params['cert_path'], mode='rb')
    params['key_file'] = open(file=params['private_key_path'], mode='rb')
    params['tgm_webhook'] = params['tgm_webhook_str'].format(params['domain'], params['port'], params['tgm_url'])
    logger.info(msg=lang_log_msg['bot_domain'].format(params['domain']))
    logger.info(msg=lang_log_msg['wh_url'].format(params['tgm_webhook']))
    logger.info(msg=lang_log_msg['local_server_values'])


def get_params():
    """
    This function gets the current settings for the server parameters and returns them.

    :return: The current server parameters
    :rtype: dict
    """

    return params


# Check if this bot is intended to run on Google's App Engine platform and set the right parameters
if config.use_app_engine:
    # If it's a local server, set the paths to point to local certificate and private key
    # Also set the local domain to point to the current public ip address
    if config.app_engine_server:
        set_remote_params(gae=True)
    else:
        set_local_params()

    # And then start the GAE bot as a local Flask application
    from bot.app.controllers import gae_flask_router

    eventbot = gae_flask_router.event_bot

else:
    # Check if the current public ip address is in the A or AAAA DNS records for this domain
    # If it isn't, then this is a local server

    resolver = dns.resolver.Resolver()
    query_a = resolver.query(config.bot_domain, 'A')
    query_aaaa = resolver.query(config.bot_domain, 'AAAA')
    dns_records = [str(query_data) for query_data in query_a]
    dns_records += [str(query_data) for query_data in query_aaaa]

    # Activate the bot platforms this app wil run
    if config.serve_tgm:
        from bot.app.controllers import telegram_bot as tgm

        # Send the params dictionary to the tgm script
        tgm.params = params

        # If it's a local server, set the paths to point to local certificate and private key
        # Also set the local domain to point to the current public ip address
        # And then start the regular bot as a local server
        if config.local_public_ip_address not in dns_records:
            set_local_params()
            tgm.start_updater(domain=params['domain'], port=params['port'], tgm_url=params['tgm_url'],
                              tgm_webhook=params['tgm_webhook'], certificate=params['cert_path'],
                              private_key=params['private_key_path'], run_locally=True)

        # Otherwise set the path to the remote certificate and private key
        # Also set the local domain to point to the remote domain name
        # And then start the regular bot as a remote server
        else:
            set_remote_params()
            tgm.start_updater(domain=params['domain'], port=params['port'], tgm_url=params['tgm_url'],
                              tgm_webhook=params['tgm_webhook'], run_locally=False)

    if config.serve_twitter:

        # Start the GAE bot as a local Flask application
        from bot.app.controllers import gae_flask_router

        eventbot = gae_flask_router.event_bot
