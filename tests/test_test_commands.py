# coding=utf-8
"""
Copyright 2017 Load Impact

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
from datetime import datetime

from click.testing import CliRunner
from loadimpactcli import test_commands

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


Test = namedtuple('Test', ['id', 'name', 'last_test_run_id', 'config'])
TestRun = namedtuple('TestRun', ['id', 'queued', 'status', 'status_text'])
Organization = namedtuple('Organization', ['id'])
Project = namedtuple('Project', ['id'])


class TestTest(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.tests = [Test(1, 'Test1', 10001, ''),
                      Test(2, 'Test2', 10002, ''),
                      Test(3, 'Test3', 10003, '')]

    def test_list_tests_one_project_id(self):
        """
        Test "test list" with 1 project id and 3 tests.
        """
        client = test_commands.client

        # Setup mockers.
        client.list_tests = MagicMock(return_value=self.tests)
        client.get_test_run = MagicMock(return_value=TestRun(1, datetime.now(), 0, 'status'))
        result = self.runner.invoke(test_commands.list_tests, ['--project_id', '1'])

        self.assertEqual(client.list_tests.call_count, 1)
        self.assertEqual(client.get_test_run.call_count, 3)
        output = result.output.split('\n')
        self.assertEqual(len(output), 2+3)
        self.assertTrue(output[1].startswith('1\tTest1\t'))
        self.assertTrue(output[2].startswith('2\tTest2\t'))
        self.assertTrue(output[3].startswith('3\tTest3\t'))

    def test_list_tests_several_project_id(self):
        """
        Test "test list" with 2 project id and 6 tests.
        """
        client = test_commands.client

        # Setup mockers.
        client.list_tests = MagicMock(return_value=self.tests)
        client.get_test_run = MagicMock(return_value=TestRun(1, datetime.now(), 0, 'status'))
        result = self.runner.invoke(test_commands.list_tests, ['--project_id', '1',
                                                               '--project_id', '2'])

        self.assertEqual(client.list_tests.call_count, 2)
        self.assertEqual(client.get_test_run.call_count, 6)
        output = result.output.split('\n')
        self.assertEqual(len(output), 2+2*3)

    def test_list_tests_no_project_id(self):
        """
        Test "test list" with no project id. The test simulates 2
        organizations, with 2 projects per organization, with 3 tests per
        project.
        """
        client = test_commands.client

        # Setup mockers.
        client.list_tests = MagicMock(return_value=self.tests)
        client.get_test_run = MagicMock(return_value=TestRun(1, datetime.now(), 0, 'status'))
        client.list_organizations = MagicMock(return_value=[Organization(1), Organization(2)])
        client.list_organization_projects = MagicMock(side_effect=[[Project(1), Project(2)],
                                                                   [Project(3), Project(4)]])
        result = self.runner.invoke(test_commands.list_tests)

        self.assertEqual(client.list_organizations.call_count, 1)
        self.assertEqual(client.list_organization_projects.call_count, 2)
        self.assertEqual(client.list_tests.call_count, 2*2)
        self.assertEqual(client.get_test_run.call_count, 2*2*3)
        output = result.output.split('\n')
        self.assertEqual(len(output), 2+2*2*3)

    def test_summarize_valid_config(self):
        config = {u'new_relic_applications': [],
                  u'network_emulation': {u'client': u'li', u'network': u'unlimited'},
                  u'user_type': u'sbu',
                  u'server_metric_agents': [],
                  u'tracks': [
                      {u'clips': [{u'user_scenario_id': 225, u'percent': 100}],
                       u'loadzone': u'amazon:ie:dublin'}
                  ],
                  u'url_groups': [],
                  u'load_schedule': [
                      {u'duration': 1, u'users': 50},
                      {u'duration': 2, u'users': 100}
                  ],
                  u'source_ips': 0}
        summary = test_commands.summarize_config(config)
        self.assertEqual(summary, '50 users 1s; 100 users 2s')

    def test_summarize_invalid_config(self):
        config = 'INVALID'
        summary = test_commands.summarize_config(config)
        self.assertEqual(summary, '-')
