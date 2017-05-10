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

from click.testing import CliRunner
from loadimpactcli import metric_commands
from loadimpactcli.util import Metric

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


TestRunResultId = namedtuple('TestRunResultId', ['type', 'ids', 'results_type_code_to_text'])
MetricRepresentation = namedtuple('MetricRepresentation', ['full', 'raw', 'as_param', 'args'])


class TestMetric(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.result_ids = [TestRunResultId(1, {'result_id_1_1': '', 'result_id_1_2': ''},
                                           self._results_type_code_to_text),
                           TestRunResultId(2, {'result_id_2_1': ''}, self._results_type_code_to_text)]

    def _assertExpectedMetric(self, metric_representation, metric, include_full=True):
        if include_full:
            self.assertEqual(metric_representation.full, metric.str_raw(True))
        self.assertEqual(metric_representation.raw, metric.str_raw(False))
        self.assertEqual(metric_representation.as_param, metric.str_param())
        self.assertEqual(metric_representation.args, metric.params)

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
        self.assertEqual(output[1], 'result_id_1_1\t-\ttext_for_type_1')
        self.assertEqual(output[2], 'result_id_1_2\t-\ttext_for_type_1')
        self.assertEqual(output[3], 'result_id_2_1\t-\ttext_for_type_2')

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
        self.assertEqual(output[1], 'result_id_1_1\t-\ttext_for_type_1')
        self.assertEqual(output[2], 'result_id_1_2\t-\ttext_for_type_1')
        self.assertEqual(output[3], 'result_id_2_1\t-\ttext_for_type_2')

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

    def test_standard_metric(self):
        """
        Test representation of standard metrics.
        """
        # Metric with parameters from full raw string.
        expected_metric_1 = MetricRepresentation('__li_bandwidth:1', '__li_bandwidth', 'bandwidth', ['1'])
        metric_1 = Metric.from_raw(expected_metric_1.full)
        self._assertExpectedMetric(expected_metric_1, metric_1)

        # Metric with parameters from full raw string and slicing: slicing is dropped.
        expected_metric_2 = MetricRepresentation('__li_bandwidth:1|1:2', '__li_bandwidth', 'bandwidth', ['1'])
        metric_2 = Metric.from_raw(expected_metric_2.full)
        self._assertExpectedMetric(expected_metric_2, metric_2, False)
        self.assertEqual(expected_metric_2.full.split('|')[0], metric_2.str_raw(True))

        # Metric with no parameters: load zone 1 is appended.
        expected_metric_3 = MetricRepresentation('__li_bandwidth', '__li_bandwidth', 'bandwidth', ['1'])
        metric_3 = Metric.from_raw(expected_metric_3.full)
        self._assertExpectedMetric(expected_metric_3, metric_3, False)
        self.assertEqual('{0}:1'.format(expected_metric_3.full), metric_3.str_raw(True))

        # Construct the metrics from the parameter representation.
        metric_1_param = Metric.from_raw(expected_metric_1.as_param)
        metric_2_param = Metric.from_raw(expected_metric_1.as_param)
        metric_3_param = Metric.from_raw(expected_metric_1.as_param)
        self.assertEqual(metric_1, metric_1_param)
        self.assertEqual(metric_2, metric_2_param)
        self.assertEqual(metric_3, metric_3_param)

        # Check equivalence of the metrics.
        self.assertEqual(metric_1, metric_2)
        self.assertEqual(metric_2, metric_3)

        # Metric with different parameters from full raw string.
        expected_metric_4 = MetricRepresentation('__li_bandwidth:1:2:x', '__li_bandwidth', 'bandwidth',
                                                 ['1', '2', 'x'])
        metric_4 = Metric.from_raw(expected_metric_4.full)
        self._assertExpectedMetric(expected_metric_4, metric_4)
        self.assertNotEqual(metric_1, metric_4)

    def test_non_standard_metric(self):
        """
        Test representation of non standard metrics.
        """
        # Metric with parameters from full raw string.
        expected_metric_1 = MetricRepresentation('__li_foo:1', '__li_foo', '-', ['1'])
        metric_1 = Metric.from_raw(expected_metric_1.full)
        self._assertExpectedMetric(expected_metric_1, metric_1)

        # Metric with parameters from full raw string and slicing: slicing is dropped.
        expected_metric_2 = MetricRepresentation('__li_foo:1|1:2', '__li_foo', '-', ['1'])
        metric_2 = Metric.from_raw(expected_metric_2.full)
        self._assertExpectedMetric(expected_metric_2, metric_2, False)
        self.assertEqual(expected_metric_2.full.split('|')[0], metric_2.str_raw(True))

        # Metric with no parameters: load zone 1 is appended.
        expected_metric_3 = MetricRepresentation('__li_foo', '__li_foo', '-', [])
        metric_3 = Metric.from_raw(expected_metric_3.full)
        self._assertExpectedMetric(expected_metric_3, metric_3)

        # Check equivalence of the metrics.
        self.assertEqual(metric_1, metric_2)
        # Metrics 2 and 3 are not equal due to having different parameters.
        self.assertNotEqual(metric_2, metric_3)

        # Metric without __li_ prefix and unicode characters.
        expected_metric_4 = MetricRepresentation(u'foöbår:0:ßåŕ', u'foöbår', '-', ['0', u'ßåŕ'])
        metric_4 = Metric.from_raw(expected_metric_4.full)
        self._assertExpectedMetric(expected_metric_4, metric_4)
