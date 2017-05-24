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

import sys

from click import unstyle
from enum import Enum


class Style(Enum):
    """
    Foreground colors used in the UI.
    """
    NONE = None
    SUCCESS = 'green'
    WARNING = 'yellow'
    ERROR = 'red'


class TestRunStatus(Enum):
    """
    Representation of a TestRun status.
    """
    STATUS_CREATED = -1
    STATUS_QUEUED = 0
    STATUS_INITIALIZING = 1
    STATUS_RUNNING = 2
    STATUS_FINISHED = 3
    STATUS_TIMED_OUT = 4
    STATUS_ABORTING_USER = 5
    STATUS_ABORTED_USER = 6
    STATUS_ABORTING_SYSTEM = 7
    STATUS_ABORTED_SYSTEM = 8
    STATUS_ABORTED_SCRIPT_ERROR = 9
    STATUS_ABORTING_THRESHOLD = 10
    STATUS_ABORTED_THRESHOLD = 11
    STATUS_FAILED_THRESHOLD = 12

    @property
    def style(self):
        if self in (TestRunStatus.STATUS_CREATED, TestRunStatus.STATUS_QUEUED,
                    TestRunStatus.STATUS_INITIALIZING, TestRunStatus.STATUS_RUNNING):
            return Style.WARNING
        elif self in (TestRunStatus.STATUS_TIMED_OUT, TestRunStatus.STATUS_ABORTING_USER,
                      TestRunStatus.STATUS_ABORTED_USER, TestRunStatus.STATUS_ABORTING_SYSTEM,
                      TestRunStatus.STATUS_ABORTED_SYSTEM, TestRunStatus.STATUS_ABORTED_SCRIPT_ERROR,
                      TestRunStatus.STATUS_ABORTING_THRESHOLD, TestRunStatus.STATUS_ABORTED_THRESHOLD,
                      TestRunStatus.STATUS_FAILED_THRESHOLD):
            return Style.ERROR
        elif self == TestRunStatus.STATUS_FINISHED:
            return Style.SUCCESS

        return Style.NONE


class DefaultMetricType(Enum):
    ACCUMULATED_LOAD_TIME = 'acc load time'
    BANDWIDTH = 'bandwidth'
    CLIENTS_ACTIVE = 'VUs'
    CONNECTIONS_ACTIVE = 'connections'
    CONTENT_TYPE = 'content type'
    CONTENT_TYPE_LOAD_TIME = 'content type load time'
    FAILURE_RATE = 'failure rate'
    LIVE_FEEDBACK = 'feedback'
    LOADGEN_CPU_UTILIZATION = 'cpu'
    LOADGEN_MEMORY_UTILIZATION = 'mem'
    LOG = 'log'
    PROGRESS_PERCENT_TOTAL = 'progress'
    REPS_FAILED_PERCENT = 'failed'
    REPS_SUCCEEDED_PERCENT = 'successful'
    REQUESTS_PER_SECOND = 'reqs/s'
    TOTAL_RX_BYTES = 'rx'
    TOTAL_REQUESTS = 'reqs'
    USER_LOAD_TIME = 'user load time'

    @classmethod
    def from_raw(cls, str_raw):
        return cls.__members__[str_raw.replace('__li_', '', 1).upper()]

    def str_param(self):
        return self.name.lower()

    def str_raw(self):
        return u'__li_{0}'.format(self.name.lower())

    def str_ui(self):
        return self.value


class OtherMetricType(object):
    def __init__(self, metric_id):
        self.metric_id = metric_id

    def str_param(self):
        return '-'

    def str_raw(self):
        return self.metric_id

    def str_ui(self):
        if self.metric_id.startswith('__li_url') or self.metric_id.startswith('__li_page'):
            return self.metric_id.replace('__li_', '').split('_')[0]
        elif self.metric_id.startswith('__server_metric'):
            return 'server metric'
        elif self.metric_id.startswith('__custom_'):
            return 'custom'

        return self.metric_id

    def __eq__(self, other):
            return self.metric_id == other.metric_id


class Metric(object):
    """
    Utility class for representing a Metric, allowing to obtain the different
    string representations (`str_raw()`, `str_param()`, `str_ui()`) and access
    the metric type and parameters.
    """
    def __init__(self, metric_type, params):
        self.metric_type = metric_type
        self.params = params

    @classmethod
    def from_raw(cls, str_raw):
        # Split the string into metric id and parameters.
        str_raw = str_raw.split('|')[0]
        str_parts = str_raw.split(':')
        str_raw, params = str_parts[0], str_parts[1:]

        try:
            metric_type = DefaultMetricType.from_raw(str_raw)
            if not params:
                # For standard metrics, append aggregated world load zone
                # parameter if no parameters are passed.
                params = ['1']
        except KeyError:
            metric_type = OtherMetricType(str_raw)
        return cls(metric_type, params)

    def str_param(self):
        """
        Return the user-friendly representation of the metric, as expected by
        the CLI arguments.
        """
        return self.metric_type.str_param()

    def str_raw(self, with_params=False):
        """
        Return the "raw" representation of the metric, as used by the API.
        """
        if with_params:
            return u':'.join([self.metric_type.str_raw()] + self.params)
        else:
            return self.metric_type.str_raw()

    def str_ui(self, with_params=False):
        """
        Return the representation of the metric for display purposes.
        """
        if with_params and self.params:
            return u'{0} [{1}]'.format(self.metric_type.str_ui(), u' '.join(self.params))
        else:
            return self.metric_type.str_ui()

    def __eq__(self, other):
            return self.metric_type == other.metric_type and self.params == other.params


class ColumnFormatter(object):
    """
    Helper class for formatting text into columns with fixed width.
    """
    def __init__(self, widths, separator):
        """
        :param widths: list with the width (in chars) of each column. A value
        of 0 is used for specifying unlimited width (ie. that column will not
        be processed and the value will be printed as-is).
        :param separator: string used as a separator between columns.
        """
        self.widths = widths
        self.separator = separator

    def format(self, *args):
        """
        Return a string that contains `args` formatted by columns, with each
        column having the width specified by `self.widths` and separated by
        `separator`. The values are truncated (replacing the 3 last characters
        by '...') if needed. For example:
            > f = ColumnFormatter(widths=(8,10,4), separator='|')
            > output = f.format('0123456789','0123456789','abc')
            > output == '01234...|0123456789|abc '

        Note that `Click.style()`-d strings (using ANSII character codes) are
        not processed at all.

        :param args: list of strings, one for each column. Note that the
        number of arguments should match the number of items on the self.width
        attribute.
        :return: a string with the resulting row
        """
        def format_cell(val_, width_):
            if len(val_) != len(unstyle(val_)) or width_ == 0:
                # For styled strings, assume they have been already prepared.
                # For width == 0, ignore formatting completely.
                return val_

            if len(val_) > width_:
                val_ = val_[:width_ - 3] + '...'

            return u'{:{width}}'.format(val_, width=width_)

        if sys.version_info >= (3, 0):
            decode = str
        else:
            decode = unicode

        return self.separator.join([format_cell(decode(val), width)
                                    for width, val in zip(self.widths, args)]).rstrip()
