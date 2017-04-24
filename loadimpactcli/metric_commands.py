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

# TestRunResults type codes.
TEXT_TO_TYPE_CODE_MAP = {
    'common': 1,
    'url': 2,
    'live_feedback': 3,
    'log': 4,
    'custom_metric': 5,
    'page': 6,
    'dtp': 7,
    'system': 8,
    'server metric': 9,
    'integration': 10
}


@click.group()
@click.pass_context
def metric(ctx):
    pass


@metric.command('list', short_help='List metrics for a test run.')
@click.argument('test_run_id')
@click.option('--type', '-t', 'metric_types', multiple=True, type=click.Choice(TEXT_TO_TYPE_CODE_MAP.keys()),
              help='Metric type to include on the list.')
def list_metrics(test_run_id, metric_types):
    try:
        data = ','.join(str(TEXT_TO_TYPE_CODE_MAP[k]) for k in metric_types)
        print data
        test_run = client.get_test_run(test_run_id)
        result_ids = test_run.list_test_run_result_ids(data=data)

        click.echo('NAME:\tTYPE:')
        for result_id in result_ids:
            for key, _ in result_id.ids.iteritems():
                click.echo('{0}\t{1}'.format(key, result_id.results_type_code_to_text(result_id.type)))
    except ConnectionError:
        click.echo("Cannot connect to Load impact API")
