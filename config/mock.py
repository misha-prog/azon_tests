import os

from dotenv import load_dotenv

load_dotenv()

MOCK_URL = os.getenv("MOCK_URL", "http://localhost:8090")
