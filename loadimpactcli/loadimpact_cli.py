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

from .userscenario_commands import userscenario
from .organization_commands import organization
from .datastore_commands import data_store
from .version import __version__


@click.group()
@click.pass_context
@click.version_option(version=__version__)
def cli(ctx):
    pass


def run_cli():
    cli.add_command(userscenario)
    cli.add_command(organization)
    cli.add_command(data_store)
    cli()

if __name__ == '__main__':
    run_cli()
