import click

from userscenario_commands import userscenario


@click.group()
@click.pass_context
def cli(ctx):
    pass

if __name__ == '__main__':
    cli.add_command(userscenario)
    cli()
