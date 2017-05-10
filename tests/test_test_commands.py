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
from loadimpactcli.util import Metric

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


Test = namedtuple('Test', ['id', 'name', 'last_test_run_id', 'config'])
TestRun = namedtuple('TestRun', ['id', 'queued', 'status', 'status_text'])
Organization = namedtuple('Organization', ['id'])
Project = namedtuple('Project', ['id'])
StreamData = namedtuple('StreamData', ['timestamp', 'value'])


class TestTestsList(unittest.TestCase):

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


class TestTestsRun(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def _assertMetricHeader(self, string, metrics):
        self.assertEqual(test_commands.pprint_header(metrics),
                         u'TIMESTAMP:\t{0}'.format(string))

    def test_ui_header(self):
        """
        Test the header of metric streaming.
        """
        # Default metrics: they are automatically appended the load zone.
        default_metrics = [Metric.from_raw('clients_active'),
                           Metric.from_raw('requests_per_second'),
                           Metric.from_raw('bandwidth'),
                           Metric.from_raw('user_load_time'),
                           Metric.from_raw('failure_rate'),]
        self._assertMetricHeader(
            u'VUs [1]:\treqs/s [1]:\tbandwidth [1]:\tuser load time [1]:\tfailure rate [1]:',
            default_metrics)

        # Same metrics, different parameters.
        repeated_metrics = [Metric.from_raw('clients_active'),
                            Metric.from_raw('__li_clients_active:2')]
        self._assertMetricHeader(u'VUs [1]:\tVUs [2]:', repeated_metrics)

        # Unicode metrics.
        unicode_metrics = [Metric.from_raw(u'foöbår:0:ßåŕ')]
        self._assertMetricHeader(u'foöbår [0 ßåŕ]:', unicode_metrics)

    def test_ui_row(self):
        """
        Test the row generation of metric streaming.
        """
        metrics = [Metric.from_raw('clients_active'),
                   Metric.from_raw(u'foöbår:1')]

        # No results returned.
        data = {}
        self.assertEqual(test_commands.pprint_row(data, metrics), '')

        # Only timestamp (not one of the requested metrics) returned.
        data = {'somerandomkey': StreamData(datetime.now(), 1),}
        self.assertEqual(test_commands.pprint_row(data, metrics).split('\t', 1)[1], u'-\t-')

        # Data returned for one metric.
        data = {metrics[0].str_raw(True): StreamData(datetime.now(), 123)}
        self.assertEqual(test_commands.pprint_row(data, metrics).split('\t', 1)[1], u'123\t-')

        # Data returned for both metrics.
        data = {metrics[0].str_raw(True): StreamData(datetime.now(), 123),
                metrics[1].str_raw(True): StreamData(datetime.now(), 'xyz'),}
        self.assertEqual(test_commands.pprint_row(data, metrics).split('\t', 1)[1], u'123\txyz')

    def test_run_no_streaming(self):
        """
        Test `test run` with no streaming of the results.
        """
        client = test_commands.client

        # Setup mockers.
        MockedTest = namedtuple('Test', ['id', 'name', 'last_test_run_id', 'config', 'start_test_run'])
        test_run = MagicMock(return_value=TestRun(222, datetime.now(), 0, 'status'))
        test = MockedTest(1, 'Test1', 10001, '', test_run)
        client.get_test = MagicMock(return_value=test)

        result = self.runner.invoke(test_commands.run_test, ['--quiet', '1'])

        # Client and test methods have been called.
        self.assertEqual(client.get_test.call_count, 1)
        self.assertEqual(test.start_test_run.call_count, 1)

        # Last line of the output contains new TestRun ID.
        output = result.output.split('\n')
        self.assertEqual(output[-2], u'222')

    def test_run_streaming(self):
        """
        Test `test run` with streaming of the results using default metrics.
        """
        def mocked_stream(*args, **kwargs):
            """
            Mimic stream() generator, yielding one row of results.
            """
            yield {'__li_clients_active:1': StreamData(datetime.now(), '1.23')}

        client = test_commands.client

        # Setup mockers.
        MockedTest = namedtuple('MockedTest',
                                ['id', 'name', 'last_test_run_id', 'config', 'start_test_run'])
        MockedTestRun = namedtuple('MockedTestRun',
                                   ['id', 'queued', 'status', 'status_text', 'result_stream'])
        mocked_stream = MagicMock(return_value=mocked_stream)
        test_run = MagicMock(return_value=MockedTestRun(222, datetime.now(), 0, 'status', mocked_stream))
        test = MockedTest(1, 'Test1', 10001, '', test_run)
        client.get_test = MagicMock(return_value=test)

        result = self.runner.invoke(test_commands.run_test, ['1'])

        # Client and test methods have been called.
        self.assertEqual(client.get_test.call_count, 1)
        self.assertEqual(test.start_test_run.call_count, 1)
        self.assertEqual(mocked_stream.call_count, 1)

        # Assertions on the output.
        output = result.output.split('\n')
        self.assertEqual(len(output), 5)
        # Results table assertions (one row, one metric).
        self.assertEqual(len(output), 5)
        self.assertEqual(len(output[-2].split('\t')), 6)
        self.assertEqual(output[-2].split('\t')[1], '1.23')
