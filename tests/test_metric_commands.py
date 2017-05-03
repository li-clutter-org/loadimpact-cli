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
from loadimpactcli import metric_commands

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


TestRunResultId = namedtuple('TestRunResultId', ['type', 'ids', 'results_type_code_to_text'])


class TestMetric(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.result_ids = [TestRunResultId(1, {'result_id_1_1': '', 'result_id_1_2': ''},
                                           self._results_type_code_to_text),
                           TestRunResultId(2, {'result_id_2_1': ''}, self._results_type_code_to_text)]

    def _results_type_code_to_text(self, type_):
        return 'text_for_type_{}'.format(type_)

    def test_list_metric_no_type(self):
        """
        Test "test metric" without specifying metric type.
        """
        client = metric_commands.client

        # Setup mockers.
        client.list_test_run_result_ids = MagicMock(return_value=self.result_ids)

        result = self.runner.invoke(metric_commands.list_metrics, ['1'])

        self.assertEqual(client.list_test_run_result_ids.call_count, 1)
        output = result.output.split('\n')
        self.assertEqual(len(output), 2+3)
        self.assertEqual(output[1], 'result_id_1_1\ttext_for_type_1')
        self.assertEqual(output[2], 'result_id_1_2\ttext_for_type_1')
        self.assertEqual(output[3], 'result_id_2_1\ttext_for_type_2')

    def test_list_metric_with_types(self):
        """
        Test "test metric" specifying metric type.
        """
        client = metric_commands.client

        # Setup mockers.
        client.list_test_run_result_ids = MagicMock(return_value=self.result_ids)

        result = self.runner.invoke(metric_commands.list_metrics, ['1', '--type', 'common', '--type', 'url'])

        self.assertEqual(client.list_test_run_result_ids.call_count, 1)
        output = result.output.split('\n')
        self.assertEqual(len(output), 2+3)
        self.assertEqual(output[1], 'result_id_1_1\ttext_for_type_1')
        self.assertEqual(output[2], 'result_id_1_2\ttext_for_type_1')
        self.assertEqual(output[3], 'result_id_2_1\ttext_for_type_2')

    def test_list_metric_invalid_type(self):
        """
        Test "test metric" specifying an invalid metric type.
        """
        client = metric_commands.client

        # Setup mockers.
        client.list_test_run_result_ids = MagicMock(return_value=self.result_ids)

        result = self.runner.invoke(metric_commands.list_metrics, ['1', '--type', 'INVALID'])

        self.assertEqual(client.list_test_run_result_ids.call_count, 0)
        self.assertEqual(result.exit_code, 2)
