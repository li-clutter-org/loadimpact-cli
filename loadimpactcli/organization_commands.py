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
def organization(ctx):
    pass


@organization.command('list', short_help='List organizations that the user is a member of.')
def list_organizations():
    try:
        orgs = client.list_organizations()
        for org in orgs:
            click.echo('{0}\t{1}'.format(org.id, org.name))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")


@organization.command('projects', short_help='List the projects of an organization the user is a member of.')
@click.argument('organization_id')
def list_organization_projects(organization_id):
    try:
        projects = client.list_organization_projects(organization_id)
        for project in projects:
            click.echo('{0}\t{1}'.format(project.id, project.name))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")
