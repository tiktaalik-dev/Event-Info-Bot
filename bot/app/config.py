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
This module holds all the settings you can use to customise your bot. You can decide what platforms (Telegram, Twitter,
others) you want that your bot serves to your users, as well as deciding if your bot will run on Google App Engine
platform or a generic server. However, bear in mind that the Twitter bot is designed to run only in GAE right now,
whereas the Telegram bot can run in both GAE or a generic server, but the setting for GAE is common to both bots.
Therefore, if you need both Twitter and Telegram then you would need to run both in GAE or run two bots independently
(i.e. a Telegram bot on a generic server and a Twitter bot in GAE, though that would be kind of inefficient and
illogical).
"""


import os
import urllib.request
import bot.app.secrets as secrets
from datetime import datetime

# Enable debug level logging. If False, the default logging level will be info
debug = False

# Enable the services this bot will serve
serve_tgm = True  # Set to True if you want to enable the Telegram bot
serve_twitter = True  # Set to True if you want to enable the Twitter bot
twitter_bot_name = 'bot_pinera'  # Please note that it doesn't include the '@' symbol from the Twitter handle!
twitter_interval = 10  # The interval (in minutes) between connections to the Twitter API server

# Set the 'debug' flag for Google App Engine debugger (normally it should be set to False)
gae_debugger = False

# Set here the date of the event you want to provide a countdown to.
# Parameters are: (year, month, day, hour, minute, second)
event_date = datetime(2022, 3, 13, 12, 0, 0)

# Set here custom properties of your bot server
bot_locale = 'es-CL'  # Check the available locale options in the file bot/app/l10n.py
bot_domain = secrets.bot_domain
bot_tgm_url = 'telegram/hook/{0}'.format(secrets.telegram_token)
bot_tgm_webhook_str = 'https://{0}:{1}/{2}'  # You shouldn't change this without understanding the code first!

# Don't modify this unless you want to use a different provider. This variable identifies the public IP address
local_public_ip_address = urllib.request.urlopen('https://ident.me').read().decode('utf8')

# This variables detect server settings that are important to set a webhook URL. You shouldn't change them!
server_software = os.getenv('SERVER_SOFTWARE', '').lower()
reverse_proxy_port = int(os.environ.get('PORT', '8443'))

# Set here whether you'll run your bot in the Google App Engine platform
use_app_engine = True
app_engine_server = (server_software.startswith('google app engine') or server_software.startswith('gae') or
                     server_software.startswith('gunicorn'))  # Only modify the names of the servers here, if needed!

# Set here the paths to certificate and private key files needed for SSL (required for webhooks). Must be in PEM format!
working_dir = os.getcwd()
local_certificate = '{0}/SSL-certs/bot-local-public.pem'.format(working_dir)
local_private_key = '{0}/SSL-certs/bot-local-private_key.pem'.format(working_dir)
remote_certificate = '{0}/SSL-certs/bot-remote-public.pem'.format(working_dir)
remote_private_key = '{0}/SSL-certs/bot-remote-private_key.pem'.format(working_dir)
