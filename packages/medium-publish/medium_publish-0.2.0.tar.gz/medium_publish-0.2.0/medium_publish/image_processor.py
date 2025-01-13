import os
import base64
import logging
import mimetypes
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Configuration for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("image_processor.log"), logging.StreamHandler()],
)

# Constants
TIMEOUT = 10  # seconds
CACHE_DIR = "image_cache"


def download_image(url: str) -> str:
    """Download an image from a URL and return its base64 representation."""
    cache_file = os.path.join(CACHE_DIR, os.path.basename(url))

    # Check if the image is already cached
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as image_file:
            logging.info("Using cached image for %s", url)
            return (
                base64.b64encode(image_file.read()).decode("utf-8"),
                "image/jpeg",
            )  # Default MIME type

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        logging.info("Successfully downloaded image from %s", url)

        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)

        # Save to cache
        with open(cache_file, "wb") as image_file:
            image_file.write(response.content)

        # Determine MIME type from Content-Type header
        mime_type = response.headers.get("Content-Type", "image/jpeg")

        return base64.b64encode(response.content).decode("utf-8"), mime_type
    except requests.RequestException as e:
        logging.error("Failed to download image from %s: %s", url, e)
        return None, None


def get_mime_type(file_path: str) -> str:
    """Get the MIME type based on the file extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "application/octet-stream"




def embed_images_in_html(html_content: str, base_dir: str, embed_images: bool) -> str:
    """Replace non-local image URLs with inline base64 images if embed_images is True."""
    soup = BeautifulSoup(html_content, "html.parser")

    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src:
            if embed_images:  # Check if embedding is enabled
                if src.startswith("http"):  # Remote image
                    base64_image, mime_type = download_image(src)
                    if base64_image:
                        img_tag["src"] = f"data:{mime_type};base64,{base64_image}"
                else:  # Local image
                    full_image_path = Path(base_dir) / src  # Convert to Path object
                    if not full_image_path.exists():
                        logging.error("Local image file not found: %s", src)
                        continue
                    try:
                        with full_image_path.open("rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                            mime_type = get_mime_type(str(full_image_path))
                            img_tag["src"] = f"data:{mime_type};base64,{base64_image}"
                    except (FileNotFoundError, PermissionError) as e:
                        logging.error("Error accessing local image file %s: %s", src, e)

    return str(soup)



# Example usage (uncomment to test):
# html_content = '<html><body><img src="https://example.com/image.jpg"><img src="local_image.jpg"></body></html>'
# processed_html = embed_images_in_html(html_content, "/path/to/local/images")
# print(processed_html)
