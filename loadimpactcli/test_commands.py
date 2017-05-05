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
from operator import attrgetter

import click

from loadimpact3.exceptions import ConnectionError
from loadimpactcli.util import TestRunStatus
from .client import client


@click.group()
@click.pass_context
def test(ctx):
    pass


@test.command('list', short_help='List tests.')
@click.option('--project_id', 'project_ids', multiple=True, help='Id of the project to list tests from.')
def list_tests(project_ids):
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

        click.echo("ID:\tNAME:\tLAST RUN DATE:\tLAST RUN STATUS:\tCONFIG:")
        for test_ in sorted(tests, key=attrgetter('id')):
            last_run_date = last_run_status = '-'
            if test_.last_test_run_id:
                last_run = client.get_test_run(test_.last_test_run_id)
                last_run_date = last_run.queued
                last_run_status = click.style(last_run.status_text,
                                              fg=TestRunStatus(last_run.status).style.value)

            click.echo(u'{0}\t{1}\t{2}\t{3}\t{4}'.format(
                test_.id, test_.name, last_run_date, last_run_status,
                summarize_config(test_.config)))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@test.command('run', short_help='Run a test.')
@click.argument('test_id')
@click.option('--quiet/--no-quiet', default=False, help='Disable streaming of metrics to stdout.')
@click.option('--metric', 'result_ids', multiple=True, help='Name of the metric to stream.')
def run_tests(test_id, quiet, result_ids):
    try:
        test_ = client.get_test(test_id)
        test_run = test_.start_test_run()
        click.echo('TEST_RUN_ID:\n{0}'.format(test_run.id))

        if not quiet:
            click.echo('TIMESTAMP:\tMETRIC:\tAGGREGATE:\tVALUE:')
            stream = test_run.result_stream(result_ids)
            for data in stream(poll_rate=3):
                for metric_id in (result_ids or sorted(data.keys())):
                    click.echo(u'{0}\t{1}\t{2}\t{3}'.format(
                        data[metric_id].timestamp,
                        metric_id,
                        data[metric_id].aggregate_function,
                        data[metric_id].value))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


def summarize_config(config):
    try:
        str_schedules = [u'{0} users {1}s'.format(schedule[u'users'], schedule[u'duration'])
                         for schedule in config[u'load_schedule']]

        return '; '.join(str_schedules)

    except (KeyError, IndexError, ValueError, TypeError):
        # Do not attempt to show the configuration, for UI-conciseness purposes.
        return '-'
