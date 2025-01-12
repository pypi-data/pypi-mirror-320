# morph_extractor/config.py

import os
import logging
from dotenv import load_dotenv
import openai

load_dotenv()  # Load variables from .env if present

API_KEY = os.environ.get("OPENAI_API_KEY")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.sambanova.ai/v1")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it.")


# Configure openai globally
openai.api_key = API_KEY
openai.api_base = API_BASE


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Sambanova-compatible OpenAI client
