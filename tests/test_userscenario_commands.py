# coding=utf-8
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
os.environ['LOADIMPACT_API_V3_TOKEN'] = 'token'

import unittest
from collections import namedtuple

from click.testing import CliRunner
from loadimpactcli import userscenario_commands

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class MockValidation(object):

    def __init__(self, status_text):
        self.status_text = status_text


class MockValidationResult(object):

    def __init__(self, timestamp, message):
        self.message = message
        self.timestamp = timestamp


class TestUserScenarios(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        Scenario = namedtuple('Scenario', ['id', 'name', 'script'])
        self.scenario1 = Scenario(1, u'Scen1', 'debug')
        self.scenario2 = Scenario(2, u'Scen2', 'info')
        self.scenario3 = Scenario(3, u'Scen3 åäö', 'info')

    def test_get_scenario(self):
        client = userscenario_commands.client
        client.get_user_scenario = MagicMock(return_value=self.scenario1)
        result = self.runner.invoke(userscenario_commands.get_scenario, ['1'])

        assert result.exit_code == 0
        assert result.output == "debug\n"

    def test_get_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.get_scenario, [])
        assert result.exit_code == 2

    def test_list_scenario(self):
        client = userscenario_commands.client
        client.DEFAULT_PROJECT = 1
        client.list_user_scenarios = MagicMock(return_value=[self.scenario1, self.scenario2])
        result = self.runner.invoke(userscenario_commands.list_scenarios, ['--project_id', '1'])

        assert result.exit_code == 0
        assert result.output == u"ID:\tNAME:\n1\tScen1\n2\tScen2\n"

    def test_list_scenario_non_ascii_name(self):
        client = userscenario_commands.client
        client.DEFAULT_PROJECT = 1
        client.list_user_scenarios = MagicMock(return_value=[self.scenario1, self.scenario3])
        result = self.runner.invoke(userscenario_commands.list_scenarios, ['--project_id', '1'])

        assert result.exit_code == 0
        assert result.output == u"ID:\tNAME:\n1\tScen1\n3\tScen3 åäö\n"

    def test_create_scenario(self):
        client = userscenario_commands.client
        client.create_user_scenario = MagicMock(return_value=self.scenario1)
        result = self.runner.invoke(userscenario_commands.create_scenario, ['tests/script', 'my script', '--project_id', '1'])
        assert result.exit_code == 0
        assert result.output == "debug\n"

    def test_create_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.create_scenario, [])
        assert result.exit_code == 2

    def test_create_scenario_with_datastore_files(self):
        client = userscenario_commands.client
        client.create_user_scenario = MagicMock(return_value=self.scenario1)
        result = self.runner.invoke(userscenario_commands.create_scenario,
                                    ['tests/script', 'my script',
                                     '--project_id', '1',
                                     '--datastore_file', 'tests/datastore.csv',
                                     '--datastore_file', 'tests/script'])
        assert result.exit_code == 0
        assert result.output == "debug\n"

    def test_create_scenario_with_existing_datastore(self):
        client = userscenario_commands.client
        client.create_user_scenario = MagicMock(return_value=self.scenario1)
        result = self.runner.invoke(userscenario_commands.create_scenario,
                                    ['tests/script', 'my script',
                                     '--project_id', '1',
                                     '--datastore_id', '1'
                                     ])
        assert result.exit_code == 0
        assert result.output == "debug\n"

    def test_update_scenario(self):
        userscenario_commands.update_user_scenario_script = MagicMock(return_value=self.scenario1)
        result = self.runner.invoke(userscenario_commands.update_scenario, ['1', 'tests/script'])
        assert result.exit_code == 0
        assert result.output == 'debug\n'

    def test_update_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.update_scenario, [])
        assert result.exit_code == 2

    def test_delete_scenario(self):
        userscenario_commands.delete_user_scenario = MagicMock(return_value="Userscenario1")
        result = self.runner.invoke(userscenario_commands.delete_scenario, ['1', '--yes'])
        assert result.exit_code == 0
        assert result.output == 'Userscenario1\n'

    def test_delete_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.update_scenario, [])
        assert result.exit_code == 2

    def test_validate_scenario(self):
        userscenario_commands.client.get_user_scenario = MagicMock(return_value=1)
        userscenario_commands.get_validation = MagicMock(return_value=MockValidation('Success'))
        userscenario_commands.get_validation_results = MagicMock(return_value=[MockValidationResult(2, 'msg')])

        userscenario_commands.get_formatted_validation_results = MagicMock(return_value='Validation 1')
        result = self.runner.invoke(userscenario_commands.validate_scenario, ['1'])

        assert result.exit_code == 0

    def test_validate_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.delete_scenario, [])
        assert result.exit_code == 2

    def test_get_formatted_validation_results(self):

        MockValidationResult.level = None
        userscenario_commands.get_timestamp_as_local_time = MagicMock(return_value=2)

        unformatted_validations = [MockValidationResult(2, 'msg 1'), MockValidationResult(2, 'msg 2'), MockValidationResult(2, 'msg 3')]
        formatted_validations = userscenario_commands.get_formatted_validation_results(unformatted_validations)
        assert formatted_validations == "[2] msg 1\n[2] msg 2\n[2] msg 3\n"
