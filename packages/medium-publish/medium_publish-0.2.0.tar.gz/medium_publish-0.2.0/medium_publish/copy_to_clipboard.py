from richxerox import copy
import click

def copy_html_to_clipboard(html_content: str) -> None:
    """
    Copies the provided HTML content to the clipboard in multiple formats.

    Args:
        html_content (str): The HTML content to be copied.
    """
    copy(html=html_content, text=html_content)  # Copy as HTML and plain text
    click.echo("✨Content has been copied to the clipboard in multiple formats.", err=True)

