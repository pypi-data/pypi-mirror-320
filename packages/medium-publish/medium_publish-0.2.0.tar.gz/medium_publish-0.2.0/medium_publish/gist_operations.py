"""
This module contains functions to handle Gist operations on GitHub.
"""

from medium_publish.env import GITHUB_TOKEN

import logging
from github import Github, InputFileContent

def publish_code_block(code_block: str, file_name: str) -> str:
    """Publish a single code block as a Gist on GitHub and return its embed script."""
    g = Github(GITHUB_TOKEN)
    gist_filename = f"{file_name}"
    files = {gist_filename: InputFileContent(content=code_block)}
    gist = g.get_user().create_gist(False, files, "Uploaded from Markdown")
    gist_url = f"https://gist.github.com/{gist.owner.login}/{gist.id}"
    logging.info("Published code block to Gist: %s", gist.html_url)
    return gist_url