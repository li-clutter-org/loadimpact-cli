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
from operator import attrgetter, methodcaller

import click
import sys

from loadimpact3.resources import TestRun
from loadimpact3.exceptions import ConnectionError
from .client import client
from .util import TestRunStatus, Metric, DefaultMetricType, ColumnFormatter


@click.group()
@click.pass_context
def test(ctx):
    pass


@test.command('list', short_help='List tests.')
@click.option('--project_id', 'project_ids', multiple=True, help='Id of the project to list tests from.')
@click.option('--limit', 'display_limit', default=20, help='Maximum number of tests to display.')
@click.option('--full_width', 'full_width', is_flag=True, help='Display the full contents of each column.')
def list_tests(project_ids, display_limit, full_width):
    try:
        if not project_ids:
            # If no project_id is specified, retrieve all projects the user has access to.
            orgs = client.list_organizations()
            projs = []
            for org in orgs:
                projs.extend(client.list_organization_projects(org_id=org.id))
            project_ids = [proj.id for proj in projs]

        tests = []
        for id_ in set(project_ids):
            tests.extend(client.list_tests(project_id=id_))

        # Output formatting.
        formatter = get_list_tests_formatter(full_width, tests)
        click.echo(formatter.format('ID:', 'NAME:', 'LAST RUN DATE:', 'LAST RUN STATUS:', 'CONFIG:'))

        # Display the tests sorted by descending test_run ID, and limit the
        # list according to the display_limit argument.
        tests = sorted(tests, key=attrgetter('last_test_run_id'), reverse=True)
        for test_ in tests[:display_limit]:
            last_run_date = last_run_status = '-'
            if test_.last_test_run_id:
                last_run = client.get_test_run(test_.last_test_run_id)
                last_run_date = last_run.queued
                last_run_status_text = last_run.status_text if full_width else '{:22}'.format(last_run.status_text)
                last_run_status = click.style(last_run_status_text, fg=TestRunStatus(last_run.status).style.value)

            click.echo(formatter.format(test_.id, test_.name, last_run_date, last_run_status,
                                        summarize_config(test_.config)))

        if len(tests) > display_limit:
            click.echo("Only the first {0} tests (out of {1}) are displayed. This behaviour can be"
                       "changed using the --limit argument.".format(display_limit, len(tests)))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@test.command('run', short_help='Run a test.')
@click.argument('test_id')
@click.option('--no-ignore-errors', is_flag=True, default=False,
              help='Print any errors returned by API while streaming results.')
@click.option('--quiet/--no-quiet', default=False, help='Disable streaming of metrics to stdout.')
@click.option('--metric', 'standard_metrics', multiple=True,
              help='Name of the standard metric to stream (implies aggregated world load zone).',
              type=click.Choice([m.name.lower() for m in list(DefaultMetricType)]))
@click.option('--raw_metric', 'raw_metrics', multiple=True, help='Raw name of the metric to stream.')
@click.option('--full_width', 'full_width', is_flag=True, help='Display the full contents of each column.')
def run_test(test_id, no_ignore_errors, quiet, standard_metrics, raw_metrics, full_width):
    try:
        test_ = client.get_test(test_id)
        test_run = test_.start_test_run()
        click.echo('TEST_RUN_ID:\n{0}'.format(test_run.id))

        try:
            if not quiet:
                # Prepare metrics.
                metrics = sorted([Metric.from_raw(m) for m in standard_metrics + raw_metrics],
                                 key=methodcaller('str_raw', True))
                if not metrics:
                    metrics = [Metric(DefaultMetricType.CLIENTS_ACTIVE, ['1']),
                               Metric(DefaultMetricType.REQUESTS_PER_SECOND, ['1']),
                               Metric(DefaultMetricType.BANDWIDTH, ['1']),
                               Metric(DefaultMetricType.USER_LOAD_TIME, ['1']),
                               Metric(DefaultMetricType.FAILURE_RATE, ['1'])]

                # Output formatting.
                formatter = get_run_test_formatter(full_width, metrics)

                stream = test_run.result_stream([m.str_raw(True) for m in metrics], raise_api_errors=no_ignore_errors)
                click.echo('Initializing test ...')

                for i, data in enumerate(stream(poll_rate=3)):
                    if i % 20 == 0:
                        click.echo(pprint_header(formatter, metrics))
                    click.echo(pprint_row(formatter, data, metrics))

            if test_run.status in [TestRun.STATUS_ABORTED_SYSTEM, TestRun.STATUS_ABORTED_SCRIPT_ERROR,
                                   TestRun.STATUS_FAILED_THRESHOLD, TestRun.STATUS_ABORTED_THRESHOLD]:
                sys.exit(test_run.status)  # We return status as exit code
        except KeyboardInterrupt:
            click.echo("Aborting test run!")
            test_run.abort()

    except ConnectionError:
        click.echo("Cannot connect to Load impact API")
        sys.exit(1)


def get_list_tests_formatter(full_width, tests):
    """
    Returns a `ColumnFormatter` with sensible values for the column widths for
    the `tests list` command.
    """
    if full_width:
        return ColumnFormatter([0] * 5, '\t')
    else:
        # Setup the formatter using sensible column widths for each field.
        column_widths = (max(len('ID:'), max([len(str(t.id)) for t in tests])),
                         32,  # width for test name (arbitrary)
                         25,  # last run date (YYYY-MM-DD HH:mm:ss+ZZ:zz)
                         22,  # len('Aborted (by threshold)')
                         64  # width for configuration (arbitrary)
                         )
        return ColumnFormatter(column_widths, ' ')


def get_run_test_formatter(full_width, metrics):
    """
    Returns a `ColumnFormatter` with sensible values for the column widths for
    the `test list` command.
    """
    if full_width:
        return ColumnFormatter([0] * (len(metrics) + 1), '\t')
    else:
        # Setup the formatter using sensible column widths for each field.
        column_widths = (25,  # timestamp (YYYY-MM-DD HH:mm:ss+ZZ:zz)
                         ) + tuple(max(16, len(m.str_ui(True)) + 1) for m in metrics)

        return ColumnFormatter(column_widths, ' ')


def pprint_header(formatter, returned_metrics):
    """
    Return a pretty printed string with the header of the metric streaming
    output, consisting of the name of the metrics including the parameters.
    """
    return formatter.format(*([u'TIMESTAMP:'] + [u'{0}:'.format(m.str_ui(True)) for m in returned_metrics]))


def pprint_row(formatter, data, returned_metrics):
    """
    Return a pretty printed string with a row of the metric streaming
    output, consisting of the values of the metrics.
    """
    try:
        parts = [u'{0}'.format(next(iter(data.items()))[1].timestamp)]
    except (StopIteration, AttributeError):
        return u''

    for m in returned_metrics:
        try:
            parts.append(u'{0}'.format(data[m.str_raw(True)].value))
        except KeyError:
            parts.append(u'-')

    return formatter.format(*parts)


def summarize_config(config):
    try:
        str_schedules = [u'{0} users {1}s'.format(schedule[u'users'], schedule[u'duration'])
                         for schedule in config[u'load_schedule']]

        return '; '.join(str_schedules)

    except (KeyError, IndexError, ValueError, TypeError):
        # Do not attempt to show the configuration, for UI-conciseness purposes.
        return '-'
