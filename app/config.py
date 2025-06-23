# config.py - Environment and Constants

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_URL = os.getenv("AGENTOPS_SERVER_URL", "http://localhost:8000")
POLL_INTERVAL = int(os.getenv("AGENTOPS_POLL_INTERVAL", 10))
