"""
This module provides functions to upload content to an AWS S3 bucket and check if a specified path exists in an AWS S3 bucket.
"""
import os
import logging
import mimetypes
import boto3
import requests
from botocore.exceptions import NoCredentialsError, ClientError
from bs4 import BeautifulSoup
from .hash_util import hash_image_content

def upload_image_to_s3(image_content: bytes, s3_folder: str, mime_type: str) -> str:
    """Upload an image to S3 and return the HTTPS object URL."""
    s3 = boto3.client('s3')
    file_extension = mime_type.split('/')[1]  # Get the file extension from MIME type
    image_hash = hash_image_content(image_content)
    bucket_name = s3_folder.split("/")[2]
    s3_prefix = "/".join(s3_folder.split("/")[3:])
    s3_key = f"{s3_prefix}/{image_hash}.{file_extension}"
    
    # Ensure the S3 path is correctly formatted
    s3_path = f"s3://{bucket_name}/{s3_key}"  # Construct the S3 path

    # Get the bucket region
    region = get_bucket_region(bucket_name)  # New function to get the bucket region
    s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"  # Construct HTTPS URL

    if check_s3_path_exists(s3_path):  # Use the correctly formatted S3 path
        logging.info("Image already exists in S3: %s", s3_url)  # Use lazy formatting
        return s3_url

    try:
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=image_content)
        logging.info("Uploaded image to S3: %s", s3_url)  # Changed to lazy formatting
        return s3_url
    except NoCredentialsError as exc:
        raise RuntimeError("AWS credentials not found.") from exc
    except ClientError as e:
        raise RuntimeError(f"Failed to upload to S3: {e}") from e

def get_bucket_region(bucket_name: str) -> str:
    """Get the region of the specified S3 bucket."""
    logging.debug("Getting region for bucket: %s", bucket_name)  # Added debug info
    s3_client = boto3.client('s3')
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    region = response.get('LocationConstraint')
    return region if region else 'us-east-1'  # Default to us-east-1 if None

def check_s3_path_exists(s3_path: str) -> bool:
    """
    Checks if a specified path exists in an AWS S3 bucket.

    Args:
        s3_path (str): The S3 path to check.

    Returns:
        bool: True if the path exists, False otherwise.

    Raises:
        ValueError: If the S3 path is invalid.
        RuntimeError: If there are issues accessing S3.
    """
    logging.debug("Checking if S3 path exists: %s", s3_path)  # Added debug info
    if not s3_path.startswith("s3://"):
        raise ValueError("Invalid S3 path. It must start with 's3://'.")

    s3_client = boto3.client("s3")
    bucket_name = s3_path.split("/")[2]
    object_key = "/".join(s3_path.split("/")[3:])

    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise RuntimeError(f"Failed to access S3: {e}") from e

def upload_images_to_s3(html_content: str, base_dir: str, s3_folder: str) -> str:
    """Upload images found in the HTML content to S3 and return modified HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    img_tags = soup.find_all("img")
    logging.debug("Found %d image(s) in HTML content.", len(img_tags))  # Moved debug info below img_tags definition

    for img in img_tags:
        img_src = img.get("src")
        logging.debug("Processing image source: %s", img_src)  # Added debug info
        if img_src:
            try:
                if img_src.startswith("http://") or img_src.startswith("https://"):
                    # Handle remote image
                    response = requests.get(img_src, timeout=10)  # Set a timeout of 10 seconds
                    response.raise_for_status()  # Raise an error for bad responses
                    image_content = response.content
                    mime_type = response.headers['Content-Type']
                else:
                    # Handle local image
                    image_path = os.path.join(base_dir, img_src)
                    with open(image_path, "rb") as image_file:
                        image_content = image_file.read()
                    mime_type, _ = mimetypes.guess_type(image_path)  # Automatically detect MIME type

                # Ensure MIME type is valid before uploading
                if mime_type is None or not mime_type.startswith('image/'):
                    logging.warning("Unsupported MIME type for image: %s. Skipping upload.", img_src)
                    continue
                
                # Upload the image to S3
                s3_url = upload_image_to_s3(image_content, s3_folder, mime_type)
                # Replace the src in the img tag with the S3 URL
                img["src"] = s3_url

            except FileNotFoundError:
                logging.error("Image file not found: %s", img_src)
            except requests.RequestException as e:
                logging.error("Error downloading image from URL (%s): %s", img_src, e)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                logging.error("Error uploading image (%s): %s", img_src, e)

    return str(soup)