import click
from cli.commands import add, list, summary, plot, report, report_pdf
@click.group()
def cli():
    """MoneyTracker: A command-line personal accounting tool."""
    pass
cli.add_command(add)
cli.add_command(list)
cli.add_command(summary)
cli.add_command(plot)
cli.add_command(report)
cli.add_command(report_pdf)

if __name__ == "__main__":
    cli()