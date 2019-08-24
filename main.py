#!/usr/bin/env python
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
This module is the first and main script from your app. It activates the Google Cloud Debugger (if it was enabled in the
config.py module) and starts a web server that's included in the Flask framework in case your bot is deployed to a
generic server that doesn't provide its own web server (Google App Engine platform does provide both an outward-facing
web server that acts as a proxy, and an internal web server that deliver HTTP requests to your Flask application).
Control of the application is then transferred to the launcher.py module.
"""


from bot.app.controllers.logger import *
import bot.app.launcher as launcher
import bot.app.config as config

# Start logger
logger = logging.getLogger(__name__)

# If enabled in the application config file, try to load the Google Cloud Debugger
if config.gae_debugger:
    try:
        import googleclouddebugger
        googleclouddebugger.enable()
    except ImportError:
        pass

# Start the Event Info Bot application
app = launcher.eventbot


# This is used when running locally only. When deploying to Google App Engine, a webserver process such as Gunicorn
# will serve the app. This can be configured by adding an `entrypoint` to app.yaml.
if (__name__ == '__main__' and config.use_app_engine) and not config.app_engine_server:
    bot_params = launcher.get_params()
    app.run(host='0.0.0.0', port=bot_params['port'], ssl_context=(bot_params['cert_path'],
                                                                  bot_params['private_key_path']), debug=config.debug)

