# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ArXiv Search Configuration
MAX_PAPERS_TO_FETCH = 10
ARXIV_SEARCH_MAX_RESULTS = 10   # Ensure arXiv package brings back this many
ARXIV_RETRY_ATTEMPTS = 3        # How many times to retry if ArXiv API times out

# LLM Configuration
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Agent Prompts & Languages
REPORT_LANGUAGE = "English"

# Directories
REPORTS_DIR = "reports"
