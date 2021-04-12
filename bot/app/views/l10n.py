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
This module holds al the predefined strings and their official localisations for different languages (to date, only
Australian English and Chilean Spanish). You can add your own language by copying either set of string and then
translating them yourself. You're also welcome to send them in to collaborate in the project and I will credit you
accordingly :-) However, in case you update your app to a newer version you risk loosing your hard work so I strongly
recommend that you make a copy of this file and rename it to 'l10n_production.py' as this file import all the contents
of that file and overwrite the strings in this file with those ones. As the production file is not distributed by me,
any changes you make in that file will not be affected by upgrading your app.
"""


import unicodedata

# Set version
__version__ = (1, 0, 0)

locales = {
    'en-AU': {
        'calculations': {
            'thousands_separator': ',',
            'base_string': '¡Only{0} {1} left!',
            'base_string_verb_suffix': '',
            'base_string_verb_suffix_null': '',
            '1_second': '1 second',
            'x_seconds': '{0} seconds',
            '1_minute': '1 minute',
            'x_minutes': '{0} minutes',
            '1_hour': '1 hour',
            'x_hours': '{0} hours',
            '1_day': '1 day',
            'x_days': '{0} days',
            '1_month': '1 month',
            'x_months': '{0} months',
            '1_year': '1 year',
            'x_years': '{0} years',
            'ymd': '{0}, {1} and {2}',
            'format_date_base_string': 'The event should happen on {0} of {1} of {2}, '
                                       'at {3:02d}:{4:02d}:{5:02d} hr',
            'event_date_met': 'The event should have already happened!',
            'month_names': {
                'January': 'January',
                'February': 'February',
                'March': 'March',
                'April': 'April',
                'May': 'May',
                'June': 'June',
                'July': 'July',
                'August': 'August',
                'September': 'September',
                'October': 'October',
                'November': 'November',
                'December': 'December'
            },
            'commands': {
                'date': 'date',
                'summary': 'summary',
                'years': 'years',
                'months': 'months',
                'days': 'days',
                'hours': 'hours',
                'minutes': 'minutes',
                'seconds': 'seconds'
            }
        },
        'log_msgs': {
            'server_softw': 'server_software is: {0}',
            'working_dir': 'current working directory is: {0}',
            'use_app_eng': 'use_app_engine is: {0}',
            'app_eng_server': 'app_engine_server is: {0}',
            'rev_proxy': 'reverse_proxy_port is: {0}',
            'wh_chat_id': 'webhook_handler.chat_id is: {0}',
            'wh_user_req': 'webhook_handler.user_request is: {0}',
            'wh_reply': 'webhook_handler.reply is: {0}',
            'tgm_handlers_added': 'Just finished adding handlers to dispatcher!',
            'start_wh_server': 'Starting server webhooking routine!',
            'bot_domain': 'bot_domain is: {0}',
            'wh_url': 'tgm_webhook is: {0}',
            'remote_server_values': 'Just executed if statement and set the remote server values',
            'local_server_values': 'Just executed if statement and set the local server values',
            'webhook_result': 'Result of setting the webhook is: {0}',
            'exception_occurred': 'The following exception occurred: {0}',
            'job_done': 'Work done. Replies sent',
            'mentions_list': 'This is the list of mentions: \n{0}',
            'followed_user': 'Just followed this user: {0}',
            'followed_everyone': 'Just followed back everyone who follows bot {0}',
            'liked_tweet': 'Just liked the tweet. id:{0}',
            'replying_tweet': 'Replying to tweet id:{0}',
            'replied_with': 'Replied with this:\n{0}',
            'like_failed': 'Just failed when trying to like the tweet id:{0} because of this reason:'
                           '\n{1}',
            'tweet_failed': 'Just failed when trying to send tweet id:{0} because of this reason:'
                           '\n{1}'
        },
        'site_msgs': {
            'main_page': 'Hello World!',
            'set_debug_level_page': 'Logging level is now temporarily set at DEBUG',
            'set_info_level_page': 'Logging level is now temporarily set at INFO',
            'set_wh_page_success': 'Webhook setup succeeded!',
            'set_wh_page_fail': 'Webhook setup failed!',
            'job_done': 'Work done. Replies sent and/or tweets liked',
            'no_mentions': 'There were no mentions that required replying to...',
            'mentions_ids': 'Got the mentions list (check log for details). These are the tweets ids:'
                            '\n{0}',
            'mentions_list': 'This is the list of mentions just retrieved from the server:'
                            '\n{0}'
        },
        'Telegram': {  # NOTE: Command names only allow characters from the English alphabet! (e.g. no accent marks)
            'commands': {
                'start': {
                    'name': 'start',  # '/start' should not be translated because it's a standard Telegram command!
                    'reply': 'Hi! Welcome to the Event Date Countdown Bot, your loyal assistant ready to remind you '
                             'the date when the much anticipated event will happen! Not only can I tell you the date, '
                             'but also I can automatically calculate the exact amount of years, months, days, hours, '
                             'minutes, and seconds left to wait for the event date to arrive. To display the list of '
                             'available commands at any time just type the following command: /help'
                },
                'help': {
                    'name': 'help',  # '/start' should not be translated because it's a standard Telegram command!
                    'reply': 'Hi! Just type one of the following commands to find out when the event will happen:'
                             '\n/start        To display again the welcome message'
                             '\n/help        To display again this list of commands'
                             "\n/date        To learn when the event will happen"
                             "\n/years         To learn how many years are left before the event happens"
                             "\n/months        To learn how many months are left before the event happens"
                             "\n/days         To learn how many days are left before the event happens"
                             "\n/hours        To learn how many hours are left before the event happens"
                             "\n/minutes      To learn how many minutes are left before the event happens"
                             "\n/seconds     To learn how many seconds are left before the event happens"
                             "\n/summary          To learn how many years, months and seconds are left before "
                             "the event happens"
                }
            }
        },
        'Twitter': {
            'default_reply': "Hey!. Sorry but I didn't understand your message 😅. Right now I can only reply if "
                             'you include any of the following keywords:'
                             '\nsummary ➡️ Years, months, and days'
                             '\ndate ➡️ When is the event due'
                             '\n\nIt can also be:'
                             '\nyears, months, days, hours, minutes, seconds ➡️ Self-explanatory.',
            'hourly_reminder': "Hi there, just a reminder that there's one hour less to go right now till the event "
                               'date comes around 😉. To be accurate: {0}',
            'minutes_reminder': "Hi there, just a reminder that we're on the final minutes before the event date comes "
                                'around 😉. To be accurate: {0}',
            'seconds_reminder': "Hi there, just a reminder that we're on the final seconds before the event date comes "
                                'around 😉. To be accurate: {0}',
            'daily_summary_reminder': 'Hi there, just a reminder that another day has passed, so the event date is '
                                      'getting closer 😉. To be accurate: {0}',
            'daily_days_reminder': 'Hi there, just a reminder that as another day has passed, you add another mark in '
                                   'your calendars 😉. To be accurate: {0}',
            'daily_months_reminder': 'Hi there, just a reminder that another month has gone with the wind so you can '
                                     'now do a short happy dance because the event is getting closer 😉. To be '
                                     'accurate: {0}'
        }
    },
    'es-CL': {
        'calculations': {
            'thousands_separator': '.',
            'base_string': '¡Queda{0} {1}!',
            'base_string_verb_suffix': 'n',
            'base_string_verb_suffix_null': '',
            '1_second': '1 segundo ⌚',
            'x_seconds': '{0} segundos ⌚',
            '1_minute': '1 minuto ⏰',
            'x_minutes': '{0} minutos ⏰',
            '1_hour': '1 hora ⌛',
            'x_hours': '{0} horas ⌛',
            '1_day': '1 día 📅',
            'x_days': '{0} días 📅',
            '1_month': '1 mes 📅',
            'x_months': '{0} meses 📅',
            '1_year': '1 año 📅',
            'x_years': '{0} años 📅',
            'ymd': '{0}, {1} y {2}',
            'format_date_base_string': 'El evento debiera ocurrir el {0} de {1} de {2}, '
                                       'a las {3:02d}:{4:02d}:{5:02d} hrs. 🎯',
            'event_date_met': 'El evento ya debiera haber ocurrido',
            'month_names': {
                'January': 'Enero',
                'February': 'Febrero',
                'March': 'Marzo',
                'April': 'Abril',
                'May': 'Mayo',
                'June': 'Junio',
                'July': 'Julio',
                'August': 'Agosto',
                'September': 'Septiembre',
                'October': 'Octubre',
                'November': 'Noviembre',
                'December': 'Diciembre'
            },
            'commands': {
                'date': 'fecha',
                'summary': 'resumen',
                'years': 'años',
                'months': 'meses',
                'days': 'días',
                'hours': 'horas',
                'minutes': 'minutos',
                'seconds': 'segundos'
            }
        },
        'log_msgs': {
            'server_softw': 'server_software es: {0}',
            'working_dir': 'current working directory es: {0}',
            'use_app_eng': 'use_app_engine es: {0}',
            'app_eng_server': 'app_engine_server es: {0}',
            'rev_proxy': 'reverse_proxy_port es: {0}',
            'wh_chat_id': 'webhook_handler.chat_id es: {0}',
            'wh_user_req': 'webhook_handler.user_request es: {0}',
            'wh_reply': 'webhook_handler.reply es: {0}',
            'tgm_handlers_added': 'Acabo de terminar de agregar manejadores al despachador',
            'start_wh_server': 'Comenzando la rutina del servidor que recibe solicitudes en el webhook',
            'bot_domain': 'bot_domain es: {0}',
            'wh_url': 'tgm_webhook es: {0}',
            'remote_server_values': 'Acabo de establecer los valores para un servidor remoto',
            'local_server_values': 'Acabo de establecer los valores para un servidor local',
            'webhook_result': 'El resultado de establecer el webhook es: {0}',
            'exception_occurred': 'Ocurrió la siguiente excepción: {0}',
            'job_done': 'Trabajo realizado. Envié las respuestas',
            'mentions_list': 'Esta es la lista de menciones: \n{0}',
            'followed_user': 'Acabo de seguir a este usuario: {0}',
            'followed_everyone': 'Acabo de seguir a todos los que siguen al bot {0}',
            'liked_tweet': 'Puse "Me gusta" al tweet. id:{0}',
            'replying_tweet': 'Respondiendo el tweet id:{0}',
            'replied_with': 'Respondí esto:\n{0}',
            'like_failed': 'Fallé al intentar poner "Me gusta" al tweet id:{0} debido a esta razón:'
                           '\n{1}',
            'tweet_failed': 'Fallé al intentar enviar el tweet id:{0} debido a esta razón:'
                           '\n{1}'
        },
        'site_msgs': {
            'main_page': '¡Hola Mundo!',
            'set_debug_level_page': 'El nivel de "Logging" fue fijado temporalmente en DEBUG ahora',
            'set_info_level_page': 'El nivel de "Logging" fue fijado temporalmente en INFO ahora',
            'set_wh_page_success': '¡Webhook configurado exitosamente!',
            'set_wh_page_fail': '¡Webhook falló en ser configurado!',
            'job_done': 'Trabajo realizado. Envié las respuestas y/o le puse "Me gusta" a los tweets',
            'no_mentions': 'No había menciones que responder...',
            'mentions_ids': 'Obtuve la lista de menciones (ver detalles en el log). Estas son las ids de los tweets:'
                            '\n{0}',
            'mentions_list': 'Esta es la lista de menciones que acabo de recibir desde el servidor:'
                            '\n{0}'
        },
        'Telegram': {  # OJO: Los nombres de comandos solo aceptan caracteres del alfabeto Inglés! (Sin 'ñ' ni acentos)
            'commands': {
                'start': {
                    'name': 'start',  # ¡'/start' no debe ser traducido ya que es un comando estándar de Telegram!
                    'reply': '¡Hola! Bienvenido al Bot de cuenta regresiva para el evento, tu fiel informante que te '
                             'recordará cuándo finalmente ocurrirá el tan esperado evento. No solo puedo recordarte la '
                             'fecha estimada para el evento, sino también calcular automáticamente cúantos años, '
                             'meses, días, horas, minutos y segundos exactos restan para ese maravilloso día. Para ver '
                             'una lista de los comandos disponibles en cualquier momento, simplemente tipea el '
                             'comando: /ayuda'
                },
                'help': {
                    'name': 'ayuda',  # ¡'/start' no debe ser traducido ya que es un comando estándar de Telegram!
                    'reply': '¡Hola! Si quieres saber cuándo ocurrirá el evento solo tienes que tipear alguno de los '
                             'siguientes comandos:'
                             '\n/start   Te repetiré el Mensaje de Bienvenida'                                                                           
                             '\n/ayuda   Te repetiré esta lista de comandos'
                             '\n/fecha    Te diré la fecha en que se va'
                             '\n/anhos   Te diré cuántos años más faltan'
                             '\n/meses  Te diré cuántos meses más faltan'
                             '\n/dias    Te diré cuántos días más faltan'
                             '\n/horas   Te diré cuántas horas más faltan'
                             '\n/minutos Te diré cuántos minutos más faltan'
                             '\n/segundos Te diré cuántos segundos más faltan'
                             '\n/resumen     Te diré cuántos años, meses y días faltan'
                },
                'years': 'anhos',
                'days': 'dias'

            }
        },
        'Twitter': {
            'default_reply': '¡Hola!. Perdón pero no entendí tu mensaje 😅. Por el momento solo puedo responder si '
                             'incluyes alguna de las siguientes palabras claves:'
                             '\nresumen ➡️ Años, meses y días'
                             '\nfecha ➡️ Cuándo es el evento'
                             '\n\nTambién puede ser:'
                             '\naños, meses, días, horas, minutos, segundos ➡️ Lo que dice c/u.',
            'hourly_reminder': '¡Hola!, solo un recordatorio de que ya falta una hora menos para que llegue el día '
                               'del evento 😉. Para ser exacto: {0}',
            'minutes_reminder': '¡Hola!, solo un recordatorio de que estamos en los últimos minutos para que llegue el '
                                'día del evento 😉. Para ser exacto: {0}',
            'seconds_reminder': '¡Hola!, solo un recordatorio de que estamos en los últimos segundos para que llegue '
                                'el día del evento 😉. Para ser exacto: {0}',
            'daily_summary_reminder': '¡Hola!, solo un recordatorio de que acaba de empezar un nuevo día, así es que '
                                      'el evento está un poco más cerca 😉. Para ser exacto: {0}',
            'daily_days_reminder': '¡Hola!, solo un recordatorio de que se acaba de ir otro día, así es que ya puedes '
                                   'hacer una marca más en tu calendario que lleva la cuenta regresiva para el '
                                   'evento 😉. Para ser exacto: {0}',
            'daily_months_reminder': '¡Hola!, solo un recordatorio de que otro mes se acaba de ir volando así es que '
                                     'ya puedes hacer un pequeño baile feliz porque el evento está acercándose 😉. '
                                     'Para ser exacto: {0}'
        }
    }
}


# For non-English languages, like Spanish, people tend to forget writing accents. So, use this function to normalise
# words to ensure that both accented and non-accented words trigger the right commands (especially in Twitter)
def remove_tildes(word):
    return str(unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore'), 'utf-8')


# Import the localisation strings from a file that contains the text to be used in production.
# Please note: This will overwrite the default contents from the locale variable above!
try:
    from bot.app.views.l10n_production import *
except ImportError:
    pass

