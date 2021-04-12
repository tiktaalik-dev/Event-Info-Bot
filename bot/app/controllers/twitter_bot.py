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
This module handles the Twitter bot. The request is captured using the Flask framework, and then this bot handles it
using to the Tweepy library. If your want to use the Twitter bot remember to enable that option in the config.py module.
"""

from bot.app.controllers.logger import *
import bot.app.config as config
import bot.app.secrets as secrets
from bot.app.controllers import calculations
from bot.app.models import twitter as tw_model
from bot.app.views.l10n import locales, remove_tildes
import tweepy


# Set version
__version__ = (1, 0, 0)

# Start logger
logger = logging.getLogger(__name__)

# Get key, token and secrets from config file
access_token = secrets.twitter_access_token
access_token_secret = secrets.twitter_access_token_secret
consumer_key = secrets.twitter_consumer_key
consumer_secret = secrets.twitter_consumer_secret

# Set global variables
lang = locales[config.bot_locale]
lang_log_msgs = lang['log_msgs']
lang_site_msgs = lang['site_msgs']
lang_twitter = lang['Twitter']
lang_commands = lang['calculations']['commands']

# Instantiate a Twitter Cursor
tw_cursor = tw_model.TwitterCursor()


# Authenticate with Twitter servers
def twitter_auth():
    """
    This function authenticates your server with Twitter servers using your consumer key and secret as well as the
    access token and token secret. Therefore, make sure you get all of these codes from Twitter before deploying your
    bot.

    :return: The API access object that it's required by every other function to communicate with Twitter servers. You
    should always collect it in a variable after calling this function
    :rtype: tweepy.API
    """

    # Build authentication credentials
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # Negotiate authentication with Twitter servers
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e

    # Log information message
    logger.info("API created")

    # Return API object to caller
    return api


def whoami(api):
    """
    This function is meant to help you test that your Twitter credentials are working properly by asking Twitter
    servers to send you back the identification info of your bot.

    :param api: The API object returned by the authentication function
    :rtype api: tweepy.API
    :return: User name of your bot as it it registered in Twitter servers
    :rtype: str
    """
    # Get bot info from servers using the API
    user = api.me()

    # Return username to caller
    return user.name


def rate_limit_status(api):
    """
    Use this function to check whether your bot hasn't exceeded your quota of Twitter's API calls. It will present you
    with the information in JSON format, though it will be 'pretty-printed'.

    :param api: The API object returned by the authentication function
    :rtype api: tweepy.API
    :return: Remaining-quota details of Twitter API calls for your bot, sourced directly from Twitter servers
    :rtype: str
    """

    # Return quota details to caller
    return api.rate_limit_status()


def check_mentions(api, since_id='1'):
    """
    This function retrieves a list of the most recent tweets that mentioned your bot's username (Twitter handle) since
    the tweet ID number stored in the database. If there's no number stored in the database (i.e. this is a fresh
    installation), then it will default to search from tweet ID number 1 onwards.

    :param api: The API object returned by the authentication function
    :type api: tweepy.API
    :param since_id: The last tweet ID that should be used as a 'bookmark' of the last tweet that was replied to
    :type since_id: str or int
    :return: The list of IDs from the tweets retrieved, the list of tweets, and the ID number of the last tweet
    retrieved
    :rtype: dict[list[str or int] or None, list[list] or None, str]
    """

    # Log informational message
    logger.info("Retrieving mentions")

    # First check if the data in tw_cursor is current. If this bot has just been loaded into memory then its last_id
    # property will be equal to '1' and data must be retrieved from the database
    if tw_cursor.get(obj_property='last_id') == '1':
        tw_cursor.get_from_db()

    # Create collectors and set starting values
    tweet_ids = []
    tweets_list = []
    new_since_id = since_id

    # Retrieve list of tweets from server and iterate over its elements to collect ID numbers
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id, tweet_mode='extended').items():
        # First check that the tweets were not posted by your bot itself. If they are, skip them
        if (tweet.user.screen_name is not config.twitter_bot_name) and (tweet.id > since_id):
            tweet_ids.append(tweet.id)
            tweets_list.append(tweet)

            # Compare the ID number of this tweet with the one in 'new_since_id' and keep the highest number
            new_since_id = max(since_id, tweet.id)

    # If the list of tweets retrieved was empty set variable values to None
    if len(tweets_list) == 0:
        tweet_ids = None
        tweets_list = None

    # Return lists of tweets, IDs, and new_since_id
    return {'tweet_ids': tweet_ids, 'tweets': tweets_list, 'since_id': new_since_id}


def like_tweet(tweet):
    """
    This function takes a single tweet object and 'like' it.

    :param tweet: Tweet object that should be liked
    :type tweet: tweepy.Status
    :return: The tweet ID number
    :rtype: dict[str or int]
    """

    # Try to 'like' tweet
    try:
        tweet.favorite()

        # Log informational message
        logger.info(lang_log_msgs['liked_tweet'].format(tweet.id))

    except tweepy.TweepError as e:
        # If fails, log a warning message
        logger.warning(lang_log_msgs['like_failed'].format(tweet.id, e.reason))

    # Return the ID number of this tweet
    return {'tweet_id': tweet.id}


def reply_tweet(api, tweet, keywords=lang_commands):
    """
    This function takes a given tweet and extracts the keywords for the information requested by your users. Then it
    replies accordingly with the information returned by the calculations module.

    :param api: The API object returned by the authentication function
    :type api: tweepy.API
    :param tweet: Tweet that must be replied
    :type tweet: tweepy.Status
    :param keywords: List of commands keywords against which to compare the text written in the tweet. It defaults to
    the commands detailed in the localisation file so this parameter should normally be omitted
    :type keywords: dict[str]
    :return: The tweet ID number
    :rtype: dict[str or int]
    """

    # Log debugging information
    logger.debug(msg='\n\ntweet.id is: {0}'.format(str(tweet.id)))
    logger.debug(msg='\n\ntweet.text is: {0}'.format(str(tweet.full_text)))

    # Split the tweet message into a list of words
    raw_tweet_words = tweet.full_text.lower().split()

    # Splitted words may contain dots. Remove them to ensure commands are recognised!
    tweet_words = [word.replace('.', '') for word in raw_tweet_words]

    # Extract a list of all values for the elements in the 'keywords' dictionary
    keywords_values = keywords.values()

    # Log debugging information
    logger.debug(msg='\n\nkeywords_values is: {0}'.format(list(keywords_values)))

    # Make a list of lowercase and 'normalised' keywords (that don't include tildes) to later on compare against the
    # words extracted from the text in the tweet
    normalised_keywords = list(map(lambda keyword: remove_tildes(word=keyword.lower()), keywords_values))

    # Log debugging information
    logger.debug(msg='\n\nnormalised_keywords is: {0}'.format(list(normalised_keywords)))

    # Filter the list of words in the tweet comparing each lowercase and normalised word against the list of normalised
    # command keywords. Then use a set to store all requested commands because sets don't allow for duplicates and we
    # don't want to send duplicated replies to our users
    commands = set(filter(lambda word: remove_tildes(word=word) in normalised_keywords, tweet_words))

    # Log debugging information
    logger.debug(msg='\n\ncommands was: {0}'.format(list(commands)))

    # Normalise keywords by removing tildes in case people have poor spelling skills
    # ToDo: Check if this is actually necessary! Maybe it should be moved up?
    commands = set(map(lambda word: remove_tildes(word=word), commands))

    # Log debugging information
    logger.debug(msg='\n\ncommands is now: {0}'.format(commands))

    # Check whether the list of commands is not empty after filtering it
    if len(commands) > 0:

        # Log debugging information
        logger.debug(msg='\n\ntype(commands) is: {0}'.format(type(commands)))
        logger.debug(msg='\n\ncommands[0] is: {0}'.format(list(commands)[0]))
        logger.debug(msg='\n\ntype(commands[0]) is: {0}'.format(type(list(commands)[0])))

        # Iterate over the list of commands and get the information requested
        for item in commands:

            # Log debugging information
            logger.info(lang_log_msgs['replying_tweet'].format(tweet.user.name))
            logger.debug(msg='\n\nitem is: {0}'.format(item))
            logger.debug(msg='\n\ntype(item) is: {0}'.format(type(item)))

            # Get the calculation for the requested information
            reply = calculations.get_date(remove_tildes(word=item.lower()))

            # Log debugging information
            logger.debug(msg=lang_log_msgs['replied_with'].format(reply))

            # Try to send the reply to our user
            try:
                api.update_status(status=reply, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)
            except tweepy.TweepError as error:
                # If the reply failed (e.g. too many characters) log a warning message
                logger.warning(msg=lang_log_msgs['tweet_failed'].format(tweet.id, error.reason))
    else:
        # If the filtered list of commands is empty, assign a generic reply explaining the user that the bot couldn't
        # understand what the user is requesting (i.e. there was no words in the tweet text that was recognised as a
        # valid command)
        reply = lang['Twitter']['default_reply']

        # Log debugging information
        logger.debug(msg=lang_log_msgs['replied_with'].format(reply))

        # Try to send the generic response
        try:
            api.update_status(status=reply, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)
        except tweepy.TweepError as error:
            # If the reply failed (e.g. too many characters) log a warning message
            logger.warning(msg=lang_log_msgs['tweet_failed'].format(tweet.id, error.reason))

    # Log informational message stating that the function was executed
    logger.info(lang_log_msgs['job_done'])

    # Return the ID number of this tweet
    return {'tweet_id': tweet.id}


def reminder_tweet(api, command):
    """
    This function tweets a reminder to your users about either the number of hours, days, months, or the summary
    information to keep them on their toes regarding the date of your event. It will source the text of these reminders
    from the l10n.py (or l10n_production.py) module, so don't forget to customise the text there and to add some
    hashtags in your message to make sure more people finds your tweets! ;-)

    :param api: The API object returned by the authentication function
    :type api: tweepy.API
    :param command: The command (localised for your language according to the l10n.py module!) to trigger the desired
    reminder tweet. Possible commands are 'hours', 'days', 'months', or 'summary'
    :type command: str
    :return: A copy of the tweet object composed, in case you need it
    :rtype: tweepy.Status
    """

    # log debugging information
    logger.debug(msg='\ncommand is: {0}'.format(str(command)))

    # Get the localised base strings for the reminder text for all possible commands and store them
    reminder_strings = {
        lang_commands['hours']: lang_twitter['hourly_reminder'],
        lang_commands['minutes']: lang_twitter['minutes_reminder'],
        lang_commands['seconds']: lang_twitter['seconds_reminder'],
        lang_commands['summary']: lang_twitter['daily_summary_reminder'],
        lang_commands['days']: lang_twitter['daily_days_reminder'],
        lang_commands['months']: lang_twitter['daily_months_reminder']
    }

    # Get the calculation message
    calculation_msg = calculations.get_date(data_request=remove_tildes(word=command))

    # Concatenate the final string
    tweet_text = reminder_strings[command].format(calculation_msg)

    # Send reminder tweet
    tweet = api.update_status(status=tweet_text)

    # Return a copy of the composed tweet object
    return tweet


def follow_user(tweet):
    """
    This function takes the tweet object provided and extracts the username of who wrote it. Then it makes your bot to
    follow that user.

    :param tweet: Tweet that must be replied
    :type tweet: tweepy.Status
    :return: The username of who you just followed
    :rtype: dict[str]
    """

    # First check whether you haven't followed that user before
    if not tweet.user.following:
        # If you haven't, follow that user
        tweet.user.follow()

        # Log informational message
        logger.info(lang_log_msgs['followed_user'].format(tweet.user.screen_name))

    # Return the username of who you just followed
    return {'username': tweet.user.screen_name}


def follow_all_followers(api):
    """
    This function retrieves a list of all your followers from twitter servers and then follow everyone back at once.
    This could come in handy if you just implemented this bot in an exiting Twitter account that you were managing
    manually.

    :param api: The API object returned by the authentication function
    :type api: tweepy.API
    :return: An informational message stating that all your followers were followed
    """
    # Get the account user information of this bot
    user = api.me()

    # Iterate over a list of all the bot followers
    for follower in tweepy.Cursor(api.followers).items():

        # Follow back this follower
        follower.follow()

    # Get the localised success message
    result = lang_log_msgs['followed_everyone'].format(user.name)

    # Log the result message
    logger.info(msg=result)

    # Return a copy of the results message
    return result

