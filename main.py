import click
from cli.commands import add,list,summary,plot,report
@click.group()
def cli():
    """MoneyTracker: A command-line personal accounting tool."""
    pass
cli.add_comand(add)
cli.add_command(list)
cli.add_command(summary)
cli.add_command(plot)
cli.add_command(report)

if __name__ == "__main__":
    cli()