import os
import logging
import openai
from dotenv import load_dotenv

# Load environment variables from .env (if available)
load_dotenv()

# Retrieve API key and base URL
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it.")

# Configure OpenAI globally
openai.api_key = API_KEY
openai.api_base = API_BASE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
