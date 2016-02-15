import click
import loadimpact


client = loadimpact.ApiTokenClient(api_token='token')


@click.group()
@click.pass_context
def userscenario(ctx):
    pass


@userscenario.command('get', short_help='Get user-scenario.')
@click.argument('scenario_id')
def get_scenario(scenario_id):
    userscenario = client.get_user_scenario(scenario_id)
    click.echo(userscenario)


@userscenario.command('create', short_help='Create user-scenario.')
@click.argument('filename')
@click.option('--name', nargs=1, type=unicode, help='Name of the user-scenario.')
@click.option('--project_id', default=1, help='Id of the project the scenario should be in.')
def create_scenario(filename, name, project_id):
    script = read_file(filename)
    data = {
        u"name": name,
        u"script": script,
        u"project_id": project_id
    }
    click.echo(client.create_user_scenario(data=data))


@userscenario.command('update', short_help='Update user-scenario.')
@click.argument('scenario_id')
@click.argument('filename')
def update_scenario(scenario_id, filename):
    script = read_file(filename)
    userscenario = client.get_user_scenario(scenario_id)
    click.echo(userscenario.update({'script': script}))


@userscenario.command('delete', short_help='Delete user-scenario.')
@click.confirmation_option(help='Are you sure you want to delete the user-scenario?')
@click.argument('scenario_id')
def delete_scenario(scenario_id):
    userscenario = client.get_user_scenario(scenario_id)
    click.echo(userscenario.delete())


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def read_file(filename):
    read_data = ""
    with open(filename, 'r') as f:
        read_data = f.read()
    return read_data
