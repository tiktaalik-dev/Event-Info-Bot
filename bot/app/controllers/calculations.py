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
    This module is the heart of the Event Info Bot. It calculates the time difference between current time and the
    event date, and then formats the result as a human-readable string that is returned to the calling process.
"""

import pytz
import calendar
from bot.app.controllers.logger import *
import bot.app.config as config
from datetime import datetime
from bot.app.views.l10n import locales, remove_tildes

# Start logger
logger = logging.getLogger(__name__)

# Shorten locale path
lang = locales[config.bot_locale]['calculations']
lang_commands = lang['commands']

# Set UTC timezone object
utc = pytz.utc


def get_now():
    """
    Gets the current date and time from the system and return it to caller.

    :return: Current time and date
    :rtype: datetime
    """

    # Get current time from server (it's local tie with no timezone!)
    server_local_time = datetime.now()

    # Localise it according to the time zone set for this server
    localised_now = config.server_timezone.localize(dt=server_local_time)

    # Convert localised_now to the UTC timezone to ease calculations
    utc_now = localised_now.astimezone(utc)

    # Return current server time set on the UTC timezone
    return utc_now


def get_timezone_date():
    """
    Localise the event date and time by adjusting it to account for the timezone differences between the location where
    the event will be held and where the sever is placed.

    :return: Date time object including a timezone mark
    :rtype: datetime
    """
    # Localise the event date and time to make sure the bot is aware of the time zones when performing calculations
    event_date = config.event_timezone.localize(dt=config.localtime_event_date)

    return event_date


def get_delta():
    """
    Calculate the date and time difference between the date set for the event and the current time and date.

    :return: Time difference between now and the event date
    :rtype: datetime.timedelta
    """

    # Get the event date (corrected by its timezone)
    event_date = get_timezone_date()

    return event_date - get_now()


def years_left():
    """
    Calculates how many years are left to reach the event date. The result only reflects full years.

    :return: Full years left to reach the event date
    :rtype: int
    """

    raw_difference = months_left() // 12

    return raw_difference


def year_fraction_left():
    """
    Calculates the remaining fraction of the last year before reaching the event date. It doesn't take into account the
    amount of full years between the event date and now. It returns the number of full months between the event month
     and the current one (e.g. the event is on the 7th month and now it's the 3rd month of the year--> difference is 4
     full months). This calculation is necessary when displaying a 'summary' string that list years, months and days.

    :return: Number of full months between event month and current month
    :rtype: int
    """

    # Get current time
    now = get_now()

    # Get the event date (corrected by its timezone)
    event_date = get_timezone_date()

    return (event_date.month - now.month) % 12


def months_left():
    """
    Calculates the number of total full months left between the event date and the current month. This function does
    take into account the amount of years left, converting them into months and adding them to the amount of months
    returned by the year_fraction_left() function.

    :return: Total full months between the event month and current month
    :rtype: int
    """

    # Get years left
    now = get_now()

    # Get the event date (corrected by its timezone)
    event_date = get_timezone_date()

    # Calculate how many years are left
    raw_years_left = event_date.year - now.year

    # Check whether the amount of years left are full years or not. If not, discount one or the amount of months left
    # reported will be off by 12 months
    # year_fraction = year_fraction_left()
    # if year_fraction != 0:
    #     raw_years_left -= 1

    return raw_years_left * 12 + year_fraction_left()


def days_left(relative=False):
    """
    Calculates the number of full days left between the event date and the current one. It accepts a 'relative'
    parameter that modifies the result to either return the total number of days (accounting for years and months left
    too) or only the number of days left within a single month (and accounting by the different lengths of each month
    throughout the year, i.e. 28, 29, 30, or 31).

    :param relative: Indicates whether the result asked should only return days within a month or in total. This
    parameter is necessary when displaying a 'summary' string that list years, months and days.
    :type relative: bool
    :return: If the 'relative' parameter was True, return the days left between the target (event) day and today but
    only within the current calendar month. If False, return the total days left between the event day and today
    :rtype: int
    """

    # Check whether the user requested days difference 'relative' to the current month or in total
    if relative:
        # Get current day from the system date
        now = get_now()
        today = now.day

        # Get the event date (corrected by its timezone)
        event_date = get_timezone_date()

        # Get the number of days that this month have in total
        days_this_month = calendar.monthlen(year=now.year, month=now.month)

        # Calculate the days difference by adding the day of the event with the amount of days left till the end of
        # this month
        delta = (event_date.day + (days_this_month - today)) % days_this_month
    else:
        # If the user only requested the total number of days, calculate it including years and months
        delta = get_delta().days

    return delta


def hours_left():
    """
    Calculate how many full hours are left from now till the hour set for the event.

    :return: Total hours from now till the event time
    :rtype: int
    """
    return seconds_left() // 3600


def minutes_left():
    """
    Calculate how many full hours are left from now till the hour set for the event.

    :return:
    """
    return seconds_left() // 60


def seconds_left():
    """
    Calculate the total amount of seconds left from now to the date and time of the event.

    :return: Total seconds left before the event occurs
    :rtype: int
    """
    delta = get_delta()
    return delta.days * 24 * 3600 + delta.seconds


def get_date(data_request):
    """
    Calculate the requested date and/or time difference requested by the user and then format the information as a
    human-readable string.

    :param data_request: The type of information requested
    :type data_request: str
    :return: The calculated time and/or date difference information
    :rtype: str
    """

    # Build a timestamp
    timestamp = get_now()

    # Localise timestamp to the event's timezone
    localised_timestamp = timestamp.astimezone(config.event_timezone)
    # if timestamp.minute < 10:
    #     timestamp_mins = '0{0}'.format(timestamp.minute)
    # else:
    #     timestamp_mins = timestamp.minute

    # Get the default strings that will be used to format the reply
    timestamp_prefix = localised_timestamp.strftime('%H:%M hr ➡ ')
    base_str = '{0}{1}'.format(timestamp_prefix, lang['base_string'])
    verb_suffix = lang['base_string_verb_suffix']
    null_suffix = lang['base_string_verb_suffix_null']

    # ### Beginning of internal functions ###
    def format_num(number):
        """
        Function that format numbers to use the appropriate character for grouping thousands and separating decimal
        digits, according to each locale. This is useful for non-English languages, such as Spanish, which don't follow
        the same conventions than English. Hence, as Python calculates arithmetic operations using English conventions,
        other languages require that the output string is modified.

        :param number: Number string that requires formatting accordingly to the locale
        :type number: str or int
        :return: A numeral formatted according to the rules of each locale
        :rtype: str
        """

        # Check if current locale is an English variation
        if config.bot_locale[0:1] == 'en':
            return '{:,}'.format(number)
        else:
            thousands_sep = lang['thousands_separator']
            return '{:,}'.format(number).replace(',', thousands_sep)

    def format_seconds():
        """
        Ask the seconds_left() function for the number of seconds left to the event and format its results as a
        human-readable string.

        :return: Human-readable information for the seconds left to the event
        :rtype: str
        """

        # Get the number of seconds left
        seconds = format_num(seconds_left())

        # Check whether the result is 0 or 1, and then return the appropriate string
        if seconds == '1':
            return lang['1_second'], null_suffix
        elif seconds == '0':
            return None

        # If the number is greater than 1, return plural noun by default
        return lang['x_seconds'].format(seconds), verb_suffix

    def format_minutes():
        """
        Ask the minutes_left() function for the number of minutes left to the event and format its results as a
        human-readable string.

        :return: Human-readable information for the minutes left to the event
        :rtype: str
        """

        # Get the number of minutes left
        minutes = format_num(minutes_left())

        # Check whether the result is 1, and then return the appropriate string
        if minutes == '1':
            return lang['1_minute'], null_suffix

        # If the number is greater than 1, return plural noun by default
        return lang['x_minutes'].format(minutes), verb_suffix

    def format_hours():
        """
        Ask the hours_left() function for the number of hours left to the event and format its results as a
        human-readable string.

        :return: Human-readable information for the hours left to the event
        :rtype: str
        """

        # Get the number of hours left
        hours = format_num(hours_left())

        # Check whether the result is 1, and then return the appropriate string
        if hours == '1':
            return lang['1_hour'], null_suffix

        # If the number is greater than 1, return plural noun by default
        return lang['x_hours'].format(hours), verb_suffix

    def format_days(relative=False):
        """
        Ask the days_left() function for the number of days left to the event and format its results as a
        human-readable string.

        :param relative: Indicates whether the result asked should only return days within a month or in total. This
        parameter is necessary when displaying a 'summary' string that list years, months and days.
        :type relative: bool
        :return: Human-readable information for the days left to the event
        :rtype: str
        """

        # Get the number of days left
        days = format_num(days_left(relative))

        # Check whether the result is 1, and then return the appropriate string
        if days == '1':
            return lang['1_day'], null_suffix

        # If the number is greater than 1, return plural noun by default
        return lang['x_days'].format(days), verb_suffix

    def format_months(fraction=False, edge_month=False):
        """
        Ask the months_left() function for the number of months left to the event and format its results as a
        human-readable string.

        :param fraction: Indicates whether the result asked should only return months as a fraction of a year or in
        total. This parameter is necessary when displaying a 'summary' string that list years, months and days
        :type fraction: bool
        :param edge_month: Whether the result must be subtracted one month or not
        :type edge_month: bool
        :return: Human-readable information for the days left to the event
        :rtype: str
        """

        # Get the number of months left, depending on whether the request is for total months or the fraction of a year.
        # Adjust the result for edge month if required
        if fraction:
            if edge_month:
                input_data = 11
            else:
                input_data = year_fraction_left()

            months = format_num(input_data)

        else:
            months = format_num(months_left())

        # Check whether the result is 1, and then return the appropriate string
        if months == '1':
            return lang['1_month'], null_suffix

        # If the number is greater than 1, return plural noun by default
        return lang['x_months'].format(months), verb_suffix

    def format_years(edge_year=False):
        """
        Ask the years_left() function for the number of years left to the event and format its results as a
        human-readable string.

        :param edge_year: Whether the result must be subtracted one year or not
        :type edge_year: bool
        :return: Human-readable information for the years left to the event
        :rtype: str
        """

        # Get the number of years left. Adjust for edge year if required
        if edge_year:
            years = format_num(years_left() - 1)
        else:
            years = format_num(years_left())

        # Check whether the result is 1, and then return the appropriate string
        if years == '1':
            return lang['1_year'], null_suffix

        # If the number is greater than 1, return plural noun by default
        return lang['x_years'].format(years), verb_suffix

    def format_ymd():
        """
        Ask the format_years(), format_months(), format_days() functions for the number of years, months and days left
        to the event and format its results as a human-readable string that summarises the time left to the event.

        :return: Human-readable summary information for the time left to the event
        :rtype: str
        """

        # Get the number of seconds left and use it to detect if the event date and time has already passed before
        # returning any summary string
        delta = get_delta()
        if delta.seconds < 1:
            return None

        # Check if event month and current month are the same one, and whether the current day is greater than the event
        # If that happens, we are on the edge between years and the output must be adjusted by subtracting one month
        # and one year. This will ensure displaying a human-friendly string
        now = get_now()

        # Get the event date (corrected by its timezone)
        event_date = get_timezone_date()

        if (event_date.month == now.month) and (event_date.day < now.day):
            years = format_years(edge_year=True)[0]
            months = format_months(fraction=True, edge_month=True)[0]
        else:
            years = format_years()[0]
            months = format_months(fraction=True)[0]

        # Get the number of years, months and days left
        ymd = {'years': years, 'months': months, 'days': format_days(relative=True)[0]}

        # If the number of seconds is greater than 1, return the default string
        return lang['ymd'].format(ymd['years'], ymd['months'], ymd['days']), verb_suffix

    def format_date():
        """
        Get the event date and return it formatted as a human-readable string.

        :return: Human-readable information for the event date
        :rtype: str
        """

        # Get the event date (corrected by its timezone)
        event_date = get_timezone_date()

        # Get the localised name for all months and assign each one to its calendar number
        month_locales = lang['month_names']
        month_names = {'1': month_locales['January'], '2': month_locales['February'], '3': month_locales['March'],
                       '4': month_locales['April'], '5': month_locales['May'], '6': month_locales['June'],
                       '7': month_locales['July'], '8': month_locales['August'], '9': month_locales['September'],
                       '10': month_locales['October'], '11': month_locales['November'], '12': month_locales['December']}

        # Return the date appropriately formatted
        return lang['format_date_base_string'].format(
            event_date.day, month_names[str(event_date.month)], event_date.year, event_date.hour, event_date.minute,
            event_date.second)

    # ### End of internal functions ###

    # Map of internal operations
    operations_map = {
        remove_tildes(word=lang_commands['date']): format_date(),
        remove_tildes(word=lang_commands['summary']): format_ymd(),
        remove_tildes(word=lang_commands['years']): format_years(),
        remove_tildes(word=lang_commands['months']): format_months(),
        remove_tildes(word=lang_commands['days']): format_days(),
        remove_tildes(word=lang_commands['hours']): format_hours(),
        remove_tildes(word=lang_commands['minutes']): format_minutes(),
        remove_tildes(word=lang_commands['seconds']): format_seconds()
    }

    # Execute operation requested
    operation_result = operations_map[data_request]

    # Return formatted string
    if operation_result is None:
        return lang['event_date_met']
    if data_request == lang_commands['date']:
        return operation_result
    else:
        return base_str.format(operation_result[1], operation_result[0])
