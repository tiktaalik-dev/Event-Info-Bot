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
This module holds the secret tokens and keys that Telegram and Twitter require that your bots use when communicating
with their servers. It also includes your domain name, which will be used to make the webhook URLs. You can fill in
their values here but in case you update your app to a newer version you risk loosing these settings so I strongly
recommend that you make a copy of this file and rename it to 'secrets_production.py' as this file import all the contents
of that file and overwrite the variables in this file with those ones. As the production file is not distributed by me,
any changes you make in that file will not be affected by upgrading your app.
"""


# Set 'secret' variables
telegram_token = ''
twitter_access_token = ''
twitter_access_token_secret = ''
twitter_consumer_key = ''
twitter_consumer_secret = ''
bot_domain = ''

# Try to import the 'production' version of this file and overwrite default values above
try:
    from bot.app.secrets_production import *
except ImportError:
    pass

