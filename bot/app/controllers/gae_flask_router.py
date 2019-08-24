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
    This module is the central hub that routes requests for those bots that don't implement their own web server or
    framework to process them (e.g. the python-telegram-bot library provides that functionality as an alternative).
    Specifically, if you intend to deploy this program to the Google App Engine platform (GAE), implementing your own
    internal web server would be tricky and wouldn't allow you to enable both Twitter and Telegram bots if you
    activate the web server provided by the python-telegram-bot library. Therefore, this module is meant to enable both
    Twitter and Telegram bots when deploying to GAE (or a similar platform that provides an internal web server) by
    using the Flask framework to capture requests and routing them to the bot modules.
"""
from bot.app.controllers.logger import *
from flask import Flask, request, jsonify
import bot.app.secrets as secrets
import bot.app.config as config
from bot.app.views.l10n import locales


# Start logger
logger = logging.getLogger(__name__)

# Shorten locale path
lang = locales[config.bot_locale]
lang_commands = lang['calculations']['commands']
lang_log_msg = lang['log_msgs']
lang_site_msg = lang['site_msgs']

# Set global variables
event_bot = Flask(__name__)
event_bot.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@event_bot.route('/', methods=['GET'])
def hello_router():
    """
    This is common for all kind of bots. It just displays a greeting for anyone who uses their web browser to visit
    your homepage. You can customise it to actually serve a more informative page about your bot (not my case, so I
    decided to not provide any kind of template).

    :return: Human-readable greeting that is displayed by web browsers in the Home page
    :rtype: str
    """

    # Return localised string to the web browser
    return lang_site_msg['main_page']


@event_bot.route('/runtime/logger/set-debug', methods=['GET'])
def set_debug_level_router():
    """
    This is common for all kind of bots. Use this route to activate the DEBUG logging level for all your bots so you
    can more easily track errors. It only accepts HTTP GET requests. It won't display log messages in your web browser
    to avoid that your users may read them. Read your logs in your server (e.g. using GAE's console).

    :return: An informative statement notifying you that the logging system has been set at the DEBUG level
    :rtype: str
    """

    # Set the logging system at the DEBUG level for this module
    logger.setLevel(level=logging.DEBUG)

    # Check whether each kind of bot is active before attempting to modify the logging level
    # Set the logging system at the DEBUG level for the Telegram bot
    if config.serve_tgm:
        tgm.logger.setLevel(level=logging.DEBUG)

    # Set the logging system at the DEBUG level for the Twitter bot
    if config.serve_twitter:
        tw_bot.logger.setLevel(level=logging.DEBUG)

    # Return a localised string to the web browser
    return lang_site_msg['set_debug_level_page']


@event_bot.route('/runtime/logger/set-info', methods=['GET'])
def set_info_level_router():
    """
    This is common for all kind of bots. Use this route to activate the INFO logging level for all your bots so you can
    more easily track errors. It only accepts HTTP GET requests. It won't display log messages in your web browser to
    avoid that your users may read them. Read your logs in your server (e.g. using GAE's console).

    :return: An informative statement notifying you that the logging system has been set at the INFO level
    :rtype: str
    """

    # Set the logging system at the INFO level for this module
    logger.setLevel(level=logging.INFO)

    # Check whether each kind of bot is active before attempting to modify the logging level
    # Set the logging system at the INFO level for the Telegram bot
    if config.serve_tgm:
        tgm.logger.setLevel(level=logging.INFO)

    # Set the logging system at the INFO level for the Twitter bot
    if config.serve_twitter:
        tw_bot.logger.setLevel(level=logging.INFO)

    # Return a localised string to the web browser
    return lang_site_msg['set_info_level_page']


# Activate routes needed for the Telegram bot (if bot is enabled in the config.py module)
if config.serve_tgm:

    # Import the Telegram bot module only if bot is activated in the config file
    import bot.app.controllers.telegram_bot_gae as tgm

    # Set routes for Telegram requests
    @event_bot.route('/telegram/set_webhook', methods=['GET', 'POST'])
    def set_webhook_router():
        """
        This route is specific for the Telegram bot. Use this route by visiting it with your web browser right after
        deploying your bot to the server for the first time (and afterwards, whenever you need to set a new webhook in
        the Telegram servers. It only accepts HTTP GET and POST requests. It won't display any details about your
        webhook in your web browser to avoid that your users may read them. Read those details following the
        instructions provided in the Telegram API documentation (see Telegram's website).

        :return: An informative statement notifying you that the webhook was either successfully set or that it failed
        :rtype: str
        """

        # Call the function that sets a new webhook
        hook = tgm.set_webhook_handler()

        # If the webhook was successfully set return a success message
        if hook:
            return lang_site_msg['set_wh_page_success']
        else:
            # Otherwise, return an error message
            return lang_site_msg['set_wh_page_fail']


    @event_bot.route('/telegram/hook/{0}'.format(secrets.telegram_token), methods=['POST'])
    def tgm_webhook_router():
        """
        This route is specific for the Telegram bot. This route is only visited by Telegram servers when delivering
        messages addressed to your bot. Therefore, it only accepts HTTP POST requests to receive information and
        doesn't display anything in a web browser.

        :return: Just an 'OK' placeholder in case the Telegram servers expect a delivery confirmation message
        :rtype: str
        """

        # Capture the request and hand it to the Telegram bot module
        tgm.webhook_updater(request_data=request)

        # Return a confirmation delivery message
        return 'OK'


    @event_bot.route('/telegram/hook/{0}/details'.format(secrets.telegram_token), methods=['GET'])
    def check_token_details_router():
        """
        This route is specific for the Telegram bot. Use this route by visiting it with your web browser to read details
        about your bot as provided by Telegram servers. It only accepts HTTP GET requests. Right now is not enabled
        because it has no extra security measures implemented to avoid prying eyes from your users (at least nothing
        beyond using your access token string in the URL, which only you should know).

        :return: Eventually, it should display details about your bot sourced from Telegram servers
        :rtype: str
        """
        pass
        # return tgm.check_token_details_handler()


# Activate routes needed for the Twitter bot (if bot is enabled in the config.py module)
if config.serve_twitter:

    # Import the Twitter bot module only if bot is activated in the config file
    import bot.app.controllers.twitter_bot as tw_bot

    # Authenticate your bot with Twitter servers and capture the API credentials to reuse them afterwards in
    # subsequent requests
    api = tw_bot.twitter_auth()

    # Set routes for Twitter requests
    @event_bot.route('/twitter/actions/{0}/whoami'.format(secrets.twitter_access_token), methods=['GET'])
    def twitter_whoami_router():
        """
        This route is specific for the Twitter bot. Use this route by visiting it with your web browser to read details
        about your bot as provided by Twitter servers. It only accepts HTTP GET requests. Right now is enabled
        but it has no extra security measures implemented to avoid prying eyes from your users (at least nothing
        beyond using your access token string in the URL, which only you should know).

        :return: It displays details about your bot sourced from Twitter servers
        :rtype: str
        """

        # Return details about your bot to display in the web browser
        return tw_bot.whoami(api=api)


    @event_bot.route('/twitter/actions/{0}/rate-limit-status'.format(secrets.twitter_access_token), methods=['GET'])
    def get_rate_limit_status_router():
        """
        This route is specific for the Twitter bot. Use this route by visiting it with your web browser to read details
        about the current consumption of API calls from your bot, as provided by Twitter servers. It only accepts HTTP
        GET requests. Right now is enabled but it has no extra security measures implemented to avoid prying eyes from
        your users (at least nothing beyond using your access token string in the URL, which only you should know).

        :return: It displays details about your consumption of API calls for your bot, as informed by Twitter servers
        :rtype: str
        """

        # Return details about your API calls for your bot to display them in the web browser
        return jsonify(tw_bot.rate_limit_status(api=api))


    @event_bot.route('/twitter/actions/{0}/follow-back'.format(secrets.twitter_access_token), methods=['GET'])
    def twitter_follow_back_router():
        """
        This route is specific for the Twitter bot. Use this route by visiting it with your web browser to manually
        make your bot follow every one of your followers back. It only accepts HTTP GET requests. Please note that
        as this bot is configured to like and follow users back whenever it replies to the latest mentions, this method
        is not really necessary and is only provided as a convenience feature in case of you may enable this bot for
        administering an existing Twitter account where you were manually replying to mentions.

        :return: An informative statement notifying you that the 'follow back' procedure either succeeded or failed
        :rtype: str
        """

        # Return a success message
        return tw_bot.follow_all_followers(api=api)


    @event_bot.route('/twitter/actions/{0}/like-mention-tweets'.format(secrets.twitter_access_token), methods=['GET'])
    def twitter_like_mention_tweets_router():
        """
        This route is specific for the Twitter bot. Use this route by visiting it with your web browser to manually
        make your bot like every tweet where it has been mentioned. It only accepts HTTP GET requests. Please note that
        as this bot is configured to like and follow users back whenever it replies to the latest mentions, this method
        is not really necessary and is only provided as a convenience feature in case of you may enable this bot for
        administering an existing Twitter account where you were manually replying to mentions.

        :return: An informative statement notifying you that the 'like all mentions' procedure either succeeded or
        failed
        :rtype: str
        """

        # Get latest mentions
        tweets = tw_bot.check_mentions(api=api)

        # Iterate over the list of mentions and 'like' those tweets
        for item in tweets:
            tw_bot.like_tweet(tweet=item)

        # Return a success message to display in the web browser
        return lang_site_msg['job_done']


    @event_bot.route('/twitter/actions/{0}/mentions-timeline'.format(secrets.twitter_access_token), methods=['GET'])
    def twitter_check_mention_tweets_router():
        """
        This route is specific for the Twitter bot. Use this route by visiting it with your web browser to manually
        inspect the latest tweets where your bot was mentioned. It only accepts HTTP GET requests. Please note that
        as this bot is configured to check mentions, like them and follow users back whenever it replies to the latest
        mentions, this method is not usually necessary and is only provided as a convenience feature in case of you may
        want to see what input is your bot receiving from Twitter servers. To ensure privacy. the full data is only
        displayed in your server logs, whereas in your web browser you'll only see the tweet IDs.

        :return: A list of the tweet IDs from the mentions provided by Twitter servers
        :rtype: str
        """

        # Get latest mentions
        mentions = tw_bot.check_mentions(api=api)

        # Log the full data for all mentions
        logger.info(msg=lang_log_msg['mentions_list'].format(mentions['tweets']))

        # Return a list of tweet IDs to display in the web browser
        return lang_site_msg['mentions_ids'].format(mentions['tweet_ids'])


    @event_bot.route('/twitter/actions/{0}/reply-mentions'.format(secrets.twitter_access_token), methods=['GET'])
    def twitter_reply_mention_tweets_router():
        """
        This route is specific for the Twitter bot and is the main interaction point with your bot. Use this route by
        visiting it with your web browser to manually make your bot reply to every tweet where it has been mentioned,
        like those tweets, and follow their authors. It only accepts HTTP GET requests. Please note that
        as Twitter doesn't provide webhooks for users of their Standard API, this bot is configured to manually execute
        this actions when triggering this route with an HTTP GET request. Therefore, you can automatise this process by
        simply creating a CRON job in your Linux/Unix server (haven't tested this program on any Windows server,
        sorry about that) that visits this URL every few minutes. The default time lapse is every 10 minutes, which
        should be safe to ensure that you don't go over your quota of free Twitter API calls. Just make sure to set
        the same number of minutes for both the CRON job and the 'twitter_interval' variable in the config.py module.

        :return: An informative statement notifying you that the 'reply to mentions' procedure either processed some
        tweets or it had no work to do
        :rtype: str
        """

        # First grab the TwitterCursor instance activated in the twitter_bot module
        cursor = tw_bot.tw_cursor

        # Then check if time difference between now and the last data update for the cursor is greater than twice the
        # value of config.twitter_interval
        if not cursor.is_it_recent():
            # If the cursor data isn't recent, then reload that info from the database
            cursor.update_from_db()

        # Get the latest mentions
        mentions = tw_bot.check_mentions(api=api, since_id=cursor.last_id)

        # Process every mention and then store the value of the 'tweet ID' for the latest mention processed
        # First create a variable to hold the latest ID
        last_reply_id = 0

        # Check wheter the list of mentions is empty or not
        if mentions['tweet_ids'] is not None:
            # If the list wasn't empty, process every tweet
            for unreplied_tweet in mentions['tweets']:
                # Reply to the current tweet and store the data returned
                last_reply = tw_bot.reply_tweet(api=api, tweet=unreplied_tweet)

                # Collect the tweet ID from the reply variable above
                last_reply_id = last_reply['tweet_id']

                # Like this mention
                tw_bot.like_tweet(tweet=unreplied_tweet)

                # Follow author back
                tw_bot.follow_user(tweet=unreplied_tweet)

            #  Grab the localised message for a 'job done' message
            site_msg = lang_site_msg['job_done']
        else:
            # Otherwise, if the list of mentions was empty, simply grab the localised message for an 'I have no work
            # to do' message
            site_msg = lang_site_msg['no_mentions']

        # In Google App Engine there could be more than one instance of the bot running concurrently so we should
        # compare if the tweet ID for the last mention that was processed by this bot instance is greater than the
        # last_id recorded in the datastore
        if last_reply_id > cursor.last_id:

            # If it's greater, update the cursor last_id property and send cursor to datastore
            cursor.set(obj_property='last_id', value=mentions['since_id'])
            cursor.send_to_db()
        else:

            # If it's not greater, then another instance may have changed it so let's update the cursor's last_id anyway
            cursor.update_from_db()

        # Return the localised message set above in case this process was activated by a web browser visiting this URL
        return site_msg


    @event_bot.route('/twitter/actions/{0}/hourly-reminder'.format(secrets.twitter_access_token), methods=['GET'])
    def hourly_tweet():
        """
        This route is specific for the Twitter bot and is meant to tweet a reminder every hour about the number of
        hours left to reach the event date. It only accepts HTTP GET requests. Please note that as Twitter doesn't
        provide webhooks for users of their Standard API, this bot is configured to manually execute
        this actions when triggering this route with an HTTP GET request. Therefore, you can automatise this process by
        simply creating a CRON job in your Linux/Unix server (haven't tested this program on any Windows server,
        sorry about that) that visits this URL every 60 minutes.

        :return: An informative statement notifying you that the method finished successfully
        :rtype: str
        """

        tw_bot.reminder_tweet(api=api, command=lang_commands['hours'])

        return lang_site_msg['job_done']


    @event_bot.route('/twitter/actions/{0}/daily-summary-reminder'.format(secrets.twitter_access_token), methods=['GET'])
    def daily_summary():
        """
        This route is specific for the Twitter bot and is meant to tweet a reminder every 24 hours providing a summary
        of years, months and days left to reach the event date. It only accepts HTTP GET requests. Please note that as
        Twitter doesn't provide webhooks for users of their Standard API, this bot is configured to manually execute
        this actions when triggering this route with an HTTP GET request. Therefore, you can automatise this process by
        simply creating a CRON job in your Linux/Unix server (haven't tested this program on any Windows server, sorry
        about that) that visits this URL every 24 hours.

        :return: An informative statement notifying you that the method finished successfully
        :rtype: str
        """

        tw_bot.reminder_tweet(api=api, command=lang_commands['summary'])

        return lang_site_msg['job_done']


    @event_bot.route('/twitter/actions/{0}/daily-days-reminder'.format(secrets.twitter_access_token), methods=['GET'])
    def daily_days():
        """
        This route is specific for the Twitter bot and is meant to tweet a reminder every 24 hours about the number of
        days left to reach the event date. It only accepts HTTP GET requests. Please note that as Twitter doesn't
        provide webhooks for users of their Standard API, this bot is configured to manually execute
        this actions when triggering this route with an HTTP GET request. Therefore, you can automatise this process by
        simply creating a CRON job in your Linux/Unix server (haven't tested this program on any Windows server,
        sorry about that) that visits this URL every 24 hours.

        :return: An informative statement notifying you that the method finished successfully
        :rtype: str
        """
        tw_bot.reminder_tweet(api=api, command=lang_commands['days'])

        return lang_site_msg['job_done']


    @event_bot.route('/twitter/actions/{0}/daily-months-reminder'.format(secrets.twitter_access_token), methods=['GET'])
    def daily_months():
        """
        This route is specific for the Twitter bot and is meant to tweet a reminder every 24 hours about the number of
        months left to reach the event date. It only accepts HTTP GET requests. Please note that as Twitter doesn't
        provide webhooks for users of their Standard API, this bot is configured to manually execute
        this actions when triggering this route with an HTTP GET request. Therefore, you can automatise this process by
        simply creating a CRON job in your Linux/Unix server (haven't tested this program on any Windows server,
        sorry about that) that visits this URL every 24 hours.

        :return: An informative statement notifying you that the finished successfully
        :rtype: str
        """

        tw_bot.reminder_tweet(api=api, command=lang_commands['months'])

        return lang_site_msg['job_done']
