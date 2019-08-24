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
    This module provides a common set of functions to create and manage a logger for all the other modules that import
    this code.
"""

import logging
import bot.app.config as config

# Start a logger for this module and grab its name
logger = logging.getLogger(__name__)


def set_default_level(level=logging.INFO):
    """
    Use this function to set the default logging level and the message's format. If not specified it will be set at
    the INFO level.

    :param level: Specify what logging level should be default. Choose between the standard logging level classes (e.g.
    logging.INFO, or logging.DEBUG)
    :type level: logging.INFO or logging.DEBUG
    :return: No return message for this function
    :rtype: None
    """
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - func:%(funcName)s - line:%(lineno)d - '
                                            '%(levelname)s - %(message)s')
    return


def set_logger_level(new_level=logging.DEBUG):
    """
    Use this function to set a new logging level at runtime. As it is imported by modules, it will only modify the
    level for the module where it's called on.

    :param new_level: Pass a logging class to indicate the desired level
    :type new_level: logging.INFO or logging.DEBUG
    :return: No return message for this function
    :rtype: None
    """
    logger.setLevel(level=new_level)

    return


def set_logger_name_to_module_name(module_name):
    """
    Use this name to specify a logger name.

    :param module_name: Desired name
    :type module_name: str
    :return: No return message for this function
    :rtype: None
    """
    logger.name = module_name

    return


# If this program is run in a local development server, the default logging will be set at 'debug' level, whereas in
# production it will follow the variable set in the config file to enable the debug level or not. If the variable equals
# False then the default logging level will be 'info'
if __name__ == '__main__':
    set_default_level(level=logging.DEBUG)
else:
    if config.debug:
        set_default_level(level=logging.DEBUG)
    else:
        set_default_level(level=logging.INFO)
