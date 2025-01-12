import click
from .scanner import scan_directory
import json

@click.command()
@click.argument("directory", required=False, default=".")
def run_scan(directory):
    """Run Sherlock to scan for hardcoded secrets."""
    results = scan_directory(directory)
    if results:
        click.echo("⚠️  Security issues found:")
        click.echo(json.dumps(results, indent=4))
    else:
        click.echo("No security issues found!")

if __name__ == "__main__":
    run_scan()
