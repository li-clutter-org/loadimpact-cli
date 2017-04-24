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

import click

from loadimpact3.exceptions import ConnectionError
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

        click.echo("ID:\tNAME:\tLAST RUN DATE:\tCONFIG:")
        for test_ in tests:
            last_run_date = None
            if test_.last_test_run_id:
                last_run_date = client.get_test_run(test_.last_test_run_id).queued

            click.echo('{0}\t{1}\t{2}\t{3}'.format(test_.id, test_.name, last_run_date, test_.config))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@test.command('run', short_help='Run a test.')
@click.argument('test_id')
def list_tests(test_id):
    try:
        test_ = client.get_test(test_id)
        test_run = test_.start_test_run()
        click.echo('{0}'.format(test_run.id))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")
