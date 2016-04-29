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

# Without this the config will prompt for a token
import os
os.environ['LOADIMPACT_API_TOKEN'] = 'token'

import unittest
from collections import namedtuple

from click.testing import CliRunner
from loadimpactcli import datastore_commands

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestDataStores(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        DataStore = namedtuple('DataStore', ['id', 'name', 'status', 'public_url'])
        self.datastore1 = DataStore(1, 'First datastore', 'status1', 'www.example.com')
        self.datastore2 = DataStore(2, 'Second datastore', 'status2', 'www.example.com')

    def test_download_csv(self):
        client = datastore_commands.client
        datastore_commands._download_csv = MagicMock()
        client.get_data_store = MagicMock(return_value=self.datastore1)
        result = self.runner.invoke(datastore_commands.download_csv, ['1'])
        assert result.exit_code == 0
        assert result.output == "Downloading CSV file, please wait.\nFinished download.\n"

    def test_download_csv_no_params(self):
        result = self.runner.invoke(datastore_commands.download_csv, [])
        assert result.exit_code == 2

    def test_list_datastore(self):
        client = datastore_commands.client
        client.DEFAULT_PROJECT = 1
        client.list_data_stores = MagicMock(return_value=[self.datastore1, self.datastore2])
        result = self.runner.invoke(datastore_commands.list_datastore, ['--project_id', '1'])

        assert result.exit_code == 0
        assert result.output == "1\tFirst datastore\n2\tSecond datastore\n"

    def test_list_datastore_missing_project_id(self):
        client = datastore_commands.client
        client.list_data_stores = MagicMock(return_value=[self.datastore1, self.datastore2])
        result = self.runner.invoke(datastore_commands.list_datastore, [])
        assert result.exit_code == 0
        assert result.output == "You need to provide a project id.\n"

    def test_create_datastore(self):
        client = datastore_commands.client
        client.DEFAULT_PROJECT = 1

        client.create_data_store = MagicMock(return_value=self.datastore1)
        datastore_commands._wait_for_conversion = MagicMock(return_value=self.datastore1)
        result = self.runner.invoke(datastore_commands.create_datastore, ['tests/script',
                                                                          'NewDatastore',
                                                                          '--project_id',
                                                                          '1'])
        assert result.exit_code == 0
        assert result.output == "{0}\n".format("Data store conversion completed with status 'unknown'")

    def test_create_datastore_missing_params(self):
        client = datastore_commands.client
        client.DEFAULT_PROJECT = 1

        client.create_data_store = MagicMock(return_value=self.datastore1)
        datastore_commands._wait_for_conversion = MagicMock(return_value=self.datastore1)
        result = self.runner.invoke(datastore_commands.create_datastore, ['tests/script'])
        assert result.exit_code == 2

    def test_update_datastore(self):
        client = datastore_commands.client
        client.DEFAULT_PROJECT = 1

        client.get_data_store = MagicMock(return_value=self.datastore2)
        client.update_data_store = MagicMock(return_value=self.datastore2)
        datastore_commands._wait_for_conversion = MagicMock(return_value=self.datastore2)

        result = self.runner.invoke(datastore_commands.update_datastore, ['1',
                                                                          'tests/script',
                                                                          '--name',
                                                                          'New name',
                                                                          '--project_id',
                                                                          '1'])
        assert result.exit_code == 0
        assert result.output == "{0}\n".format("Data store conversion completed with status 'unknown'")

    def test_update_datastore_missing_params(self):
        client = datastore_commands.client
        client.DEFAULT_PROJECT = 1

        client.get_data_store = MagicMock(return_value=self.datastore2)
        client.update_data_store = MagicMock(return_value=self.datastore2)
        datastore_commands._wait_for_conversion = MagicMock(return_value=self.datastore2)

        result = self.runner.invoke(datastore_commands.update_datastore, ['1'])
        assert result.exit_code == 2
