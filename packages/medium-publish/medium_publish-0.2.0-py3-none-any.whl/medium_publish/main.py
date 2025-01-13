"""Main entry point for the markdown processing CLI tool."""

import os
import click
from medium_publish.process_file import process_markdown_file
# load the .env file
from dotenv import load_dotenv

load_dotenv()


# Extract the bucket name from the S3 folder path

@click.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output",
    type=click.Path(dir_okay=False),
    help="Output file path for the modified HTML.",
)
@click.option(
    "--embed-images", is_flag=True, default=False, help="Embed images in the output."
)
@click.option(
    "--upload-images", is_flag=True, default=False, help="Upload images to AWS S3."
)
def main(file_path: str, output: str, embed_images: bool, upload_images: bool) -> None:
    """Process a markdown file and publish code blocks as Gists."""

    # Convert relative path to absolute path
    absolute_path = os.path.abspath(file_path)

    try:
        modified_html = process_markdown_file(
            absolute_path, embed_images=embed_images, upload_images=upload_images
        )

        click.echo("Modified HTML Content:")
        click.echo(modified_html)

        if output:  # Check if output file path is provided
            with open(output, "w", encoding="utf-8") as f:  # Specify encoding
                f.write(modified_html)
            click.echo(f"Modified HTML written to {output}")

    except FileNotFoundError:
        click.echo(f"Error: The file '{absolute_path}' was not found.", err=True)
    except IOError as e:
        click.echo(f"Error: An I/O error occurred: {e}", err=True)
    except ValueError as e:  # Catch specific exception
        if "S3 folder not found" in str(e):
            click.echo("Error: S3 folder not found. Please set the S3_FOLDER environment variable.", err=True)
        else:
            click.echo(f"Error: {e}", err=True)
    # pylint: disable=broad-exception-caught
    except Exception as e:  # Catch any other exceptions
        click.echo(f"An unexpected error occurred: {e}", err=True)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
