"""
Copyright 2015 Load Impact

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

import unittest

from click.testing import CliRunner
from unittest.mock import MagicMock
from cli import userscenario_commands


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

    def test_get_scenario(self):
        client = userscenario_commands.client
        client.get_user_scenario = MagicMock(return_value=3)
        result = self.runner.invoke(userscenario_commands.get_scenario, ['1'])

        assert result.exit_code == 0
        assert result.output == "3\n"

    def test_get_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.get_scenario, [])
        assert result.exit_code == 2

    def test_create_scenario(self):
        client = userscenario_commands.client
        client.create_user_scenario = MagicMock(return_value=3)
        result = self.runner.invoke(userscenario_commands.create_scenario, ['script', '--name', 'jennys', '--project_id', '1'])
        assert result.exit_code == 0
        assert result.output == "3\n"

    def test_create_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.create_scenario, [])
        assert result.exit_code == 2

    def test_update_scenario(self):
        userscenario_commands.update_user_scenario_script = MagicMock(return_value="Userscenario1")
        result = self.runner.invoke(userscenario_commands.update_scenario, ['1', 'script'])
        assert result.exit_code == 0
        assert result.output == 'Userscenario1\n'

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

        result = self.runner.invoke(userscenario_commands.validate_scenario, ['1'])

        assert result.exit_code == 0

    def test_validate_scenario_no_params(self):
        result = self.runner.invoke(userscenario_commands.delete_scenario, [])
        assert result.exit_code == 2
