#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.config.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     06 Dec 2018, (7:21 AM)

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved

           Permission is hereby granted, free of charge, to any person obtaining a copy
           of this software and associated documentation files (the "Software"), to deal
           in the Software without restriction, including without limitation the rights
           to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
           copies of the Software, and to permit persons to whom the Software is
           furnished to do so, subject to the following conditions:

           The above copyright notice and this permission notice shall be included in all
           copies or substantial portions of the Software.

           THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
           EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
           MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
           IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
           DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
           OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
           OR OTHER DEALINGS IN THE SOFTWARE.

"""

import os
import json

from unmanic import metadata
from unmanic.libs import unlogger
from unmanic.libs import common
from unmanic.libs.singleton import SingletonType

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class Config(object, metaclass=SingletonType):
    app_version = ''

    test = ''

    def __init__(self, config_path=None, **kwargs):
        # Set the default UI Port
        self.ui_port = 8888

        # Set default directories
        self.config_path = os.path.join(common.get_home_dir(), '.unmanic', 'config')
        self.log_path = os.path.join(common.get_home_dir(), '.unmanic', 'logs')
        self.plugins_path = os.path.join(common.get_home_dir(), '.unmanic', 'plugins')
        self.userdata_path = os.path.join(common.get_home_dir(), '.unmanic', 'userdata')

        # Configure debugging
        self.debugging = False

        # Library Settings:
        self.library_path = os.path.join('/', 'library')
        self.enable_library_scanner = False
        self.schedule_full_scan_minutes = 1440
        self.follow_symlinks = True
        self.run_full_scan_on_start = False
        self.enable_inotify = False

        # Worker settings
        self.number_of_workers = 1
        self.cache_path = os.path.join('/', 'tmp', 'unmanic')

        # Import env variables and override all previous settings.
        self.__import_settings_from_env()

        # Finally, re-read config from file and override all previous settings.
        self.__import_settings_from_file(config_path)

        # Overwrite current settings with given args
        if config_path:
            self.set_config_item('config_path', config_path, save_settings=False)

        if kwargs.get('unmanic_path'):
            self.set_config_item('config_path', os.path.join(kwargs.get('unmanic_path'), 'config'), save_settings=False)
            self.set_config_item('plugins_path', os.path.join(kwargs.get('unmanic_path'), 'plugins'), save_settings=False)
            self.set_config_item('userdata_path', os.path.join(kwargs.get('unmanic_path'), 'userdata'), save_settings=False)

        if kwargs.get('port'):
            self.set_config_item('ui_port', kwargs.get('port'), save_settings=False)

        # Apply settings to the unmanic logger
        self.__setup_unmanic_logger()

    def _log(self, message, message2='', level="info"):
        """
        Generic logging method. Can be implemented on any unmanic class

        :param message:
        :param message2:
        :param level:
        :return:
        """
        unmanic_logging = unlogger.UnmanicLogger.__call__()
        logger = unmanic_logging.get_logger(__class__.__name__)
        if logger:
            message = common.format_message(message, message2)
            getattr(logger, level)(message)
        else:
            print("Unmanic.{} - ERROR!!! Failed to find logger".format(self.__name__))

    def get_config_as_dict(self):
        """
        Return a dictionary of configuration fields and their current values

        :return:
        """
        return self.__dict__

    def get_config_keys(self):
        """
        Return a list of configuration fields

        :return:
        """
        return self.get_config_as_dict().keys()

    def __setup_unmanic_logger(self):
        """
        Pass configuration to the global logger

        :return:
        """
        unmanic_logging = unlogger.UnmanicLogger.__call__()
        unmanic_logging.setup_logger(self)

    def __import_settings_from_env(self):
        """
        Read configuration from environment variables.
        This is useful for running in a docker container or for unit testing.

        :return:
        """
        for setting in self.get_config_keys():
            if setting in os.environ:
                self.set_config_item(setting, os.environ.get(setting), save_settings=False)

    def __import_settings_from_file(self, config_path=None):
        """
        Read configuration from the settings JSON file.

        :return:
        """
        # If config path was not passed as variable, use the default one
        if not config_path:
            config_path = self.get_config_path()
        # Ensure the config path exists
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        settings_file = os.path.join(config_path, 'settings.json')
        if os.path.exists(settings_file):
            data = {}
            try:
                with open(settings_file) as infile:
                    data = json.load(infile)
            except Exception as e:
                self._log("Exception in reading saved settings from file:", message2=str(e), level="exception")
            # Set data to Config class
            self.set_bulk_config_items(data, save_settings=False)

    def __write_settings_to_file(self):
        """
        Dump current settings to the settings JSON file.

        :return:
        """
        if not os.path.exists(self.get_config_path()):
            os.makedirs(self.get_config_path())
        settings_file = os.path.join(self.get_config_path(), 'settings.json')
        data = self.get_config_as_dict()
        result = common.json_dump_to_file(data, settings_file)
        if not result['success']:
            for message in result['errors']:
                self._log("Exception:", message2=str(message), level="exception")
            raise Exception("Exception in writing settings to file")

    def get_config_item(self, key):
        """
        Get setting from either this class or the Settings model

        :param key:
        :return:
        """
        # First attempt to fetch it from this class' get functions
        if hasattr(self, "get_{}".format(key)):
            getter = getattr(self, "get_{}".format(key))
            if callable(getter):
                return getter()

    def set_config_item(self, key, value, save_settings=True):
        """
        Assigns a value to a given configuration field.
        This is applied to both this class.

        If 'save_settings' is set to False, then settings are only
        assigned and not saved to file.

        :param key:
        :param value:
        :param save_settings:
        :return:
        """
        # Get lowercase value of key
        field_id = key.lower()
        # Check if key is a valid setting
        if field_id not in self.get_config_keys():
            self._log("Attempting to save unknown key", message2=str(key), level="warning")
            # Do not proceed if this is any key other than the database
            return

        # Assign value to class attribute
        setattr(self, key, value)

        # Save settings (if requested)
        if save_settings:
            self.__write_settings_to_file()

    def set_bulk_config_items(self, items, save_settings=True):
        """
        Write bulk config items to this class.

        :param items:
        :param save_settings:
        :return:
        """
        # Set values that match the settings model attributes
        config_keys = self.get_config_keys()
        for config_key in config_keys:
            # Only import the item if it exists (Running a get here would default a missing var to None)
            if config_key in items:
                self.set_config_item(config_key, items[config_key], save_settings=save_settings)

    @staticmethod
    def read_version():
        """
        Return the application's version number as a string

        :return:
        """
        return metadata.read_version_string('long')

    def get_ui_port(self):
        """
        Get setting - ui_port

        :return:
        """
        return self.ui_port

    def get_cache_path(self):
        """
        Get setting - cache_path

        :return:
        """
        return self.cache_path

    def get_config_path(self):
        """
        Get setting - config_path

        :return:
        """
        return self.config_path

    def get_debugging(self):
        """
        Get setting - debugging

        :return:
        """
        return self.debugging

    def get_enable_inotify(self):
        """
        Get setting - enable_inotify

        :return:
        """
        return self.enable_inotify

    def get_library_path(self):
        """
        Get setting - library_path

        :return:
        """
        return self.library_path

    def get_log_path(self):
        """
        Get setting - log_path

        :return:
        """
        return self.log_path

    def get_number_of_workers(self):
        """
        Get setting - number_of_workers

        :return:
        """
        return self.number_of_workers

    def get_enable_library_scanner(self):
        """
        Get setting - enable_library_scanner

        :return:
        """
        return self.enable_library_scanner

    def get_run_full_scan_on_start(self):
        """
        Get setting - run_full_scan_on_start

        :return:
        """
        return self.run_full_scan_on_start

    def get_schedule_full_scan_minutes(self):
        """
        Get setting - schedule_full_scan_minutes

        :return:
        """
        return self.schedule_full_scan_minutes

    def get_follow_symlinks(self):
        """
        Get setting - follow_symlinks

        :return:
        """
        return self.follow_symlinks

    def get_plugins_path(self):
        """
        Get setting - config_path

        :return:
        """
        return self.plugins_path
