import click
from .summarizer import process_text
from .utils import extract_from_url, read_file
import warnings

#warnings.filterwarnings("ignore")
#warnings.filterwarnings("ignore", module="torch")
#warnings.filterwarnings("ignore", module="numpy")

@click.command()
@click.option('--url', help='URL to extract text from')
@click.option('--file', help='Text file path to summarize', type=click.Path(exists=True))
@click.option('--model', default='t5-base', help='Transformer model to use')
@click.option('--max-length', default=180, help='Maximum length of summary')
def main(url, file, model, max_length):
    """Summarize text from a URL or file."""
    try:
        if url:
            click.echo(f"Fetching text from URL: {url}")
            text = extract_from_url(url)
        elif file:
            click.echo(f"Reading file: {file}")
            text = read_file(file)
        else:
            raise click.UsageError("Please provide either --url or --file")

        if not text or len(text.strip()) < 50:
            raise click.UsageError("Not enough text content to summarize")

        click.echo("Starting summarization process...")
        summary = process_text(text, model=model, max_length=max_length)
        click.echo("\nSummary:")
        click.echo("=" * 80)
        click.echo(summary)
        click.echo("=" * 80)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()