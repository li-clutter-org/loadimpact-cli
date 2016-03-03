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
import os.path
from sys import platform
from shutil import copyfile
from six import raise_from

from .errors import CLIError


def get_value_from_usersettings(key):
    try:
        return config.get('user_settings', key)
    except configparser.Error:
        raise_from(CLIError("You need to configure default project and token."), None)


config = configparser.ConfigParser()
home = os.path.expanduser("~")
config_file_path = ''

# MacOSX
if platform == "darwin":
    config_file_path = '{0}/Library/Application Support/LoadImpact/config.ini'.format(home)

# Linux
if platform == "linux" or platform == "linux2":
    config_file_path = '{0}/.config/LoadImpact/config.ini'.format(home)


if not os.path.isfile(config_file_path):
    print("Creating config file in {0}".format(config_file_path))
    copyfile('config.ini', config_file_path)

config.read(config_file_path)

DEFAULT_PROJECT = os.getenv("LOADIMPACT_DEFAULT_PROJECT") if os.getenv("LOADIMPACT_DEFAULT_PROJECT") else get_value_from_usersettings('default_project')
LOADIMPACT_API_TOKEN = os.getenv("LOADIMPACT_API_TOKEN") if os.getenv("LOADIMPACT_API_TOKEN") else get_value_from_usersettings('api_token')
