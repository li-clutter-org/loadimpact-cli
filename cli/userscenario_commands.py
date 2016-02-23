# coding=utf-8
"""
Copyright 2015 Load Impact

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

from time import sleep
import click

from .client import client
from .config import DEFAULT_PROJECT


@click.group()
@click.pass_context
def userscenario(ctx):
    pass


@userscenario.command('get', short_help='Get user-scenario.')
@click.argument('id')
def get_scenario(id):
    userscenario = client.get_user_scenario(id)
    click.echo(userscenario)


@userscenario.command('create', short_help='Create user-scenario.')
@click.argument('script_file', type=click.File('r'))
@click.option('--name', nargs=1, help='Name of the user-scenario.')
@click.option('--project_id', default=DEFAULT_PROJECT, help='Id of the project the scenario should be in.')
def create_scenario(script_file, name, project_id):
    script = read_file(script_file)
    data = {
        u"name": name,
        u"script": script,
        u"project_id": project_id
    }
    click.echo(client.create_user_scenario(data=data))


@userscenario.command('update', short_help='Update user-scenario.')
@click.argument('scenario_id')
@click.argument('script_file', type=click.File('r'))
def update_scenario(scenario_id, script_file):
    script = read_file(script_file)
    user_scenario = update_user_scenario_script(scenario_id, script)
    click.echo(user_scenario)


@userscenario.command('delete', short_help='Delete user-scenario.')
@click.confirmation_option(help='Are you sure you want to delete the user-scenario?')
@click.argument('scenario_id')
def delete_scenario(scenario_id):
    click.echo(delete_user_scenario(scenario_id))


@userscenario.command('validate', short_help='Validate user-scenario.')
@click.argument('scenario_id')
def validate_scenario(scenario_id):
    user_scenario = client.get_user_scenario(scenario_id)
    validation = get_validation(user_scenario)
    validation_results = get_validation_results(validation)

    for result in validation_results:
        click.echo("[{0}] {1}".format(result.timestamp, result.message))

    click.echo("Validation completed with status: {0}".format(validation.status_text))


def delete_user_scenario(scenario_id):
    userscenario = client.get_user_scenario(scenario_id)
    return userscenario.delete()


def update_user_scenario_script(scenario_id, script):
    userscenario = client.get_user_scenario(scenario_id)
    userscenario.update({'script': script})
    return client.get_user_scenario(scenario_id)


def get_validation(user_scenario):
    validation = user_scenario.validate()
    return validation


def get_validation_results(validation):
    poll_rate = 10

    while not validation.is_done():
        validation = client.get_user_scenario_validation(validation.id)
        sleep(poll_rate)

    validation_results = client.get_user_scenario_validation_result(validation.id)
    return validation_results


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def read_file(script_file):
    read_data = ""
    with script_file as f:
        read_data = f.read()
    return read_data
