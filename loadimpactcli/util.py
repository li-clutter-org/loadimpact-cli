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

