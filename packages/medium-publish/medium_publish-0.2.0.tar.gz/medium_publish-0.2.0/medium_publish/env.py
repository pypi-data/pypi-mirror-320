import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError(
        "GitHub token not found. Set the GITHUB_TOKEN environment variable."
    )

S3_FOLDER = os.getenv("S3_FOLDER")
if not S3_FOLDER:
    raise ValueError("S3 folder not found. Set the S3_FOLDER environment variable.")
