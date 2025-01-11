import click
from kapito.main import Analyzer

@click.command()
@click.argument('url')
def main(url):
    """A short description of the project."""
    analyzer = Analyzer()
    results = analyzer.analyze(url)
    click.echo(results)

if __name__ == "__main__":
    main()
