"""
Copyright 2016 Load Impact

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from six.moves import configparser
from six import raise_from
import errno
import os
from sys import platform
import click

from .errors import CLIError

config = configparser.ConfigParser()
home = os.path.expanduser("~")
config_file_path = ''

# MacOSX
if platform == "darwin":
    config_file_path = '{0}/Library/Application Support/LoadImpact/config.ini'.format(home)

# Linux
if platform == "linux" or platform == "linux2":
    config_file_path = '{0}/.config/LoadImpact/config.ini'.format(home)

# Windows
if platform == "win32":
    config_file_path = '{0}\AppData\LoadImpact\config.ini'.format(home)


def build_config():
    new_config = configparser.RawConfigParser()
    new_config.add_section('user_settings')
    return new_config


def get_or_create_config_file_path(config_file_path):
    """Check if a config file exists globally, otherwise create it."""
    if not os.path.isfile(config_file_path):
        print("Creating config file in {0}".format(config_file_path))

        new_config = build_config()

        path = os.path.dirname(config_file_path)
        try:
            os.makedirs(path)
        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise_from(CLIError("Unable to create directory {0}".format(path)), ex)
        with open(config_file_path, 'w') as configfile:
            new_config.write(configfile)


def get_required_value_from_usersettings(key, env_name):
    """Get value from config or env, if the value is not in the config, prompt the user for it."""
    if os.getenv(env_name):
        return os.getenv(env_name)
    try:
        return config.get('user_settings', key)
    except configparser.Error:
        value = click.prompt('{0}'.format(env_name))
        print("Adding key and value to config at {0}".format(config_file_path))
        with open(config_file_path, 'a') as file:
            file.write('\n{0}={1}'.format(key, value))
        return value


def get_optional_value_from_usersettings(key, env_name):
    """Get value from config or env if it exists."""
    if os.getenv(env_name):
        return os.getenv(env_name)
    try:
        return config.get('user_settings', key)
    except configparser.Error:
        pass


get_or_create_config_file_path(config_file_path)
config.read(config_file_path)

DEFAULT_PROJECT = get_optional_value_from_usersettings('default_project', 'LOADIMPACT_DEFAULT_PROJECT')
LOADIMPACT_API_TOKEN = get_required_value_from_usersettings('api_token', 'LOADIMPACT_API_V3_TOKEN')
