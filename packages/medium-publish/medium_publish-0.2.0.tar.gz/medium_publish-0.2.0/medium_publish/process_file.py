"""
This module contains functions to process markdown files and publish them on Medium.
"""

import os
import logging
import markdown2
from bs4 import BeautifulSoup
from medium_publish.copy_to_clipboard import copy_html_to_clipboard
from medium_publish.image_processor import embed_images_in_html
from medium_publish.gist_operations import publish_code_block  # Import the new function
from medium_publish.s3_file_operations import upload_images_to_s3
from medium_publish.env import S3_FOLDER

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def read_markdown_file(file_path: str) -> str:
    """Read the markdown file into a string."""
    logging.debug("Attempting to read markdown file: %s", file_path)  # Added debug log
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        logging.debug("Successfully read markdown file: %s", file_path)  # Added debug log
        return content
    except FileNotFoundError as exc:
        logging.error("File not found: %s", file_path)
        raise ValueError(
            f"File not found: {file_path}. Please check the path and try again."
        ) from exc
    except Exception as e:
        logging.error("Error reading file: %s", e)
        raise ValueError(f"An error occurred while reading the file: {e}") from e


def clean_html(html_content: str) -> str:
    """Remove all empty <span> and <pre> tags from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove empty <span> tags
    for span in soup.find_all("span"):
        if not span.get_text(strip=True):  # Check if the span is empty
            span.decompose()

    # Remove empty <pre> tags
    for pre in soup.find_all("pre"):
        if not pre.get_text(strip=True):  # Check if the pre is empty
            pre.decompose()

    return str(soup)


def process_markdown_file(
    file_path: str, embed_images: bool, upload_images: bool
) -> str:
    """Orchestrate reading, extracting, publishing, and modifying markdown file."""
    logging.debug("Processing markdown file: %s", file_path)  # Added debug log
    markdown_content = read_markdown_file(file_path)

    logging.debug("Transforming code blocks.")  # Added debug log
    markdown_content = transform_code_blocks(markdown_content=markdown_content)

    logging.debug("Transforming unordered list.")  # Added debug log
    markdown_content = transform_markdown_unordered_list(markdown_content)
    logging.debug("Transforming ordered list.")  # Added debug log
    markdown_content = transform_markdown_ordered_list(markdown_content)

    # Convert entire markdown content to HTML
    logging.debug("Converting markdown to HTML.")  # Added debug log
    html_content = markdown2.markdown(markdown_content, extras=["fenced-code-blocks"])

    # Directory of the file
    base_dir = os.path.dirname(os.path.abspath(file_path))

    if upload_images:
        logging.debug("Uploading images to S3.")  # Added debug log
        html_content = upload_images_to_s3(html_content, base_dir, S3_FOLDER)
    else:
        logging.debug("Embedding images in HTML.")  # Added debug log
        html_content = embed_images_in_html(html_content, base_dir, embed_images)

    # Wrap the modified HTML content in a complete HTML document structure
    complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Processed Output</title>
</head>
<body>
{html_content}
</body>
</html>
"""

    logging.debug("Copying final HTML content to clipboard.")  # Added debug log
    copy_html_to_clipboard(complete_html)

    return complete_html


def transform_markdown_unordered_list(text: str) -> str:
    """Transform markdown unordered list items into a string with emojis.

    Args:
        text (str): The input markdown text containing unordered list items.

    Returns:
        str: The transformed text with emojis replacing the list items.
    """
    # Define the emoji to replace the markdown unordered list item
    emoji = "•"  # You can change this to any other emoji you prefer

    # Split the text into lines
    lines = text.split("\n")

    # Iterate over each line
    for i, line in enumerate(lines):
        # Check if the line starts with a dash followed by a space
        if line.strip().startswith("- "):
            # Replace the markdown dash with the emoji
            lines[i] = line.replace("- ", f"{emoji} ") + "\n"

    # Join the modified lines back into a single string
    transformed_text = "\n".join(lines)

    return transformed_text


def transform_markdown_ordered_list(text: str) -> str:
    """Transform numbered list in markdown text to corresponding emoji representation."""
    # Define a dictionary to map numbers to emojis
    emoji_map = {
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
        "10": "🔟",
    }

    # Define a function to convert numbers greater than 10 to emoji representation
    def number_to_emoji(number: int) -> str:
        if number <= 10:
            return emoji_map[str(number)]
        else:
            return " ".join(emoji_map[digit] for digit in str(number))

    # Split the text into lines
    lines = text.split("\n")

    # Iterate over each line
    for i, line in enumerate(lines):
        # Check if the line starts with a number followed by a period
        if line.strip().startswith(tuple(emoji_map.keys())) and line.strip()[1] == ".":
            # Extract the number from the line
            number = int(line.strip()[0])

            line_return = "\n" if i != 1 else ""

            # Replace the number with the corresponding emoji and add a space after the number
            lines[i] = (
                line_return
                + line.replace(f"{number}.", f"{number_to_emoji(number)} ")
                + "\n"
            )

    # Join the modified lines back into a single string
    transformed_text = "\n".join(lines)

    return transformed_text


def process_code_tags(html_content: str, file_name: str) -> str:
    """Process <code> tags, publish their content, and replace with Gist URLs."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all <code> tags
    code_tags = soup.find_all("code")
    logging.debug("Found %d <code> tags in HTML.", len(code_tags))

    for code_tag in code_tags:
        code_content = code_tag.get_text()
        # Publish the code block and get the Gist URL
        gist_url = publish_code_block(code_content, file_name)
        # Replace the <code> tag with the Gist URL
        code_tag.replace_with(gist_url)

    return str(soup)


def transform_code_blocks(markdown_content: str) -> str:
    """
    Clean the markdown content by removing leading spaces from lines within code blocks
    based on the indentation of the first line of the code block, and ensuring proper newline handling.

    Args:
        markdown_content (str): The markdown content to be cleaned.

    Returns:
        str: The cleaned markdown content.
    """
    logging.debug("Transforming code blocks in markdown content.")  # Added debug log
    if not isinstance(markdown_content, str):
        raise ValueError("Input must be a string.")

    # Split the content into lines while preserving line endings
    lines = markdown_content.splitlines(keepends=True)
    cleaned_lines = []
    in_code_block = False
    code_block_indent = 0

    for line in lines:
        stripped_line = line.strip()

        # Check for the start or end of a code block
        if stripped_line.startswith("```"):
            in_code_block = not in_code_block  # Toggle code block status
            if in_code_block:
                cleaned_lines.append(
                    "\n"
                )  # Add newline at the beginning of the code block
            cleaned_lines.append(line.lstrip())  # Retain the line as is
            if not in_code_block:
                cleaned_lines.append("\n")  # Add newline at the end of the code block
                code_block_indent = 0  # Reset on closing code block
            else:
                # Reset indentation for new code block
                code_block_indent = len(line) - len(line.lstrip())
        elif in_code_block:
            # Remove leading spaces/tabs based on the first line's indentation
            cleaned_lines.append(line[code_block_indent:])  # Remove indent
        else:
            # Retain lines outside code blocks as is
            cleaned_lines.append(line)

    # Ensure there's a newline after each line, if not already present
    cleaned_lines = [
        line if line.endswith("\n") else line + "\n" for line in cleaned_lines
    ]

    # Join the cleaned lines into a single string and strip any trailing newlines
    return "".join(cleaned_lines).rstrip("\n")
