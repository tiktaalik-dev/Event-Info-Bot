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
This module defines a database model for a cursor, which is an object that holds data about the ID number of the last
tweet retrieved from Twitter servers, as well as the date and time when it was retrieved. This data is necessary to
ensure your bot does not keep replying to old mentions more than once, which would obviously upset your users. This
cursor will also be equipped with methods that get, set, update and modify its data, as well as to ensure that data is
current.
"""

from bot.app.controllers.logger import *
import bot.app.config as config
from datetime import datetime, timedelta, timezone
from google.cloud import datastore
import json

# Start logger
logger = logging.getLogger(__name__)


# Define a model class to store data in Google Cloud Firestore (using Datastore compatibility)
class TwitterCursor(object):
    """
    This class creates an object that stores ID number of the last tweet retrieved from Twitter servers, as well as the
    date and time it was last modified. Its methods not only allow you to get, set, and update its data in the database,
    but also to import/export as a dictionary, export as JSON, as well as checking if the data is recent enough or you
    should reload it from the database.
    """

    def __init__(self, last_id=1):
        """
        This method initialises an instance by storing a tweet ID number and recording the date and time of its
        creation. The ID number can be either provided at creation time or it will default to 1 (int) as it would be
        the case if your bot has just been activated in a new account. In case that you enable this bot in an already
        existent account you should visit the URL that only checks mentions to make sure of overwrite the default value
        with the actual last tweet ID number!

        :param last_id: The tweet ID number that should be set as a cursor for future request to the Twitter API
        :type last_id: int
        """

        # Log informational message
        logger.info(msg='Started a new TwitterCursor instance')

        # Start the datastore client instance
        self.db_client = datastore.Client()

        # Log informational message
        logger.info(msg='Started a new datastore client instance')

        # Set a single default entity key so that the entity is always assigned the same record (number 1) in datastore
        # because there's no need to store this datum more than once
        self.entity_key = self.db_client.key('tw_cursor_last_id', 1)

        # Check first if there's any cursor data recorded in the datastore, in case that the bot is restarting
        db_data = self.get_from_db()

        # If data is absent from datastore, then set default values because this is the first time the bot has ran
        if db_data is None:
            self.last_id = last_id
            self.creation_time = datetime.now(tz=timezone.utc)
        else:
            # Otherwise, set the cursor using the data from the datastore
            self.last_id = db_data['last_id']
            self.creation_time = db_data['creation_time']

    def get(self, obj_property):
        """
        This method gets the current instance data and returns the requested property.

        :param obj_property: The specific property that should be returned
        :type obj_property: str or int
        :return: The current data for that cursor property
        :rtype: str or int
        """

        # Map the cursor properties to possible parameter names to ensure returning the correct one
        obj_map = {'last_id': self.last_id, 'creation_time': self.creation_time}

        # Return requested datum
        return obj_map[obj_property]

    def set(self, obj_property, value):
        """
        This method sets the provided value for the requested property in the current instance.

        :param obj_property: The cursor property whose value should be overwritten
        :type obj_property: str
        :param value: The new value that should overwrite the current data for a given property
        :type value: int or datetime
        :return: An informational message stating success or False
        :rtype: str or bool
        """

        # Log debugging information
        logger.debug(msg='Cursor set method received this for value: {0}'.format(value))
        logger.debug(msg='Cursor set method received this for type(value): {0}'.format(type(value)))

        # Set new value into property and exit
        if setattr(self, obj_property, value):
            return 'OK'
        else:
            return False

    def to_dict(self):
        """
        Get the current cursor data and return it as a dictionary.

        :return: Cursor data as a dictionary
        :rtype: dict
        """

        # Return data
        return {'creation_time': self.creation_time, 'last_id': self.last_id}

    def from_dict(self, dict_data):
        """
        Import data from a dictionary and overwrite current values for any property.

        :param dict_data: Dictionary containing cursor data
        :type dict_data: dict[str or int]
        :return: True
        :rtype: bool
        """

        # Iterate over the dictionary data and set new values
        for item in dict_data:
            setattr(self, item, dict_data[item])

        # Return success signal
        return True

    def to_json(self, indented=True):
        """
        This method gets the current cursor data and return it in JSON format.

        :param indented: Whether the JSON data returned should be indented for pretty-printing
        :type indented: bool
        :return: Current cursor data in JSON format
        :rtype: str
        """

        # Convert the cursor properties to a dictionary and set values as data types that can be exported in JSON format
        structure = {'creation_time': self.creation_time.isoformat(), 'last_id': self.last_id}

        # Check whether data should be indented or not and return it
        if indented:
            return json.dumps(structure, indent=4, sort_keys=True)
        else:
            return json.dumps(structure, sort_keys=True)

    def from_json(self, json_data):
        """
        This method imports data provided in JSON format and overwrites current values for any cursor property.

        :param json_data: Cursor data provided in JSON format
        :type json_data: str
        :return: An informational message
        :rtype: str
        """

        # Load JSON data ina temporary variable
        cursor_data = json.loads(json_data)

        # Overwrite current property values with new ones, converting them to an appropriate format if necessary
        self.last_id = cursor_data.last_id
        self.creation_time = datetime.fromisoformat(date_string=cursor_data.creation_time)

        # Return informational message
        return 'json data imported'

    def send_to_db(self):
        """
        Store current cursor data into the database and return a copy of it.

        :return: A copy of the current cursor data that was sent to database
        """

        # Create a new datastore entity
        data_item = datastore.Entity(key=self.entity_key)

        # Get current cursor data
        cursor_data = self.to_dict()

        # Log debugging messages
        logger.debug(msg='data_item entity is: {0}'.format(data_item))
        logger.debug(msg='cursor_data is: {0}'.format(cursor_data))
        logger.debug(msg='type(cursor_data) is: {0}'.format(type(cursor_data)))

        # Populate datastore entity with current cursor data
        data_item.update(cursor_data)

        # Store datastore entity in the database
        self.db_client.put(entity=data_item)

        # Return a copy of current cursor data
        return {'item_id': str(data_item.id), 'cursor_data': cursor_data}

    def get_from_db(self):
        """
        Retrieve cursor data directly from the datastore and return it.

        :return: Cursor data as it is stored in the database
        :rtype: dict
        """

        # Get cursor data from the database
        db_data = self.db_client.get(key=self.entity_key)

        # Log debugging information
        logger.debug(msg='Retrieved cursor data from db: {0}'.format(repr(db_data)))

        # Return cursor data
        return db_data

    def update_from_db(self):
        """
        This method retrieves the cursor data stored in the database and update current cursor values with those in
        the database.

        :return: If database is not empty, return cursor data. Otherwise return None
        :rtype: dict or None
        """
        db_data = self.db_client.get(key=self.entity_key)
        logger.info(msg='Retrieved cursor data from db: {0}'.format(repr(db_data)))

        if db_data is not None:
            self.from_dict(dict_data=db_data)

            return {'last_id': self.last_id, 'creation_time': self.creation_time}
        else:
            return None

    def is_it_recent(self):
        """
        This method checks whether the current values of the cursor instance are reasonably recent (i.e. less than
        twice the twitter_interval setting in the config.py module). If it's not, you should get the cursor data from
        the database in case another instance from your app in GAE has been active as well. Otherwise, you may end up
        replying twice to the same tweet mention.

        :return: Confirmation of whether this cursor instance holds recent data or not
        :rtype: bool
        """

        # Get current date and time from the operating system
        now = datetime.now(tz=timezone.utc)

        # Calculate the date and time difference between now and the data stored in the cursor
        delta = now - self.creation_time

        # Calculate if the magnitude of the difference exceeds the threshold
        interval = timedelta(minutes=2 * config.twitter_interval)

        # Make a decision and return it
        if delta > interval:
            return False
        else:
            return True
