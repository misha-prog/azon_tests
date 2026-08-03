import os

from dotenv import load_dotenv

load_dotenv()

MANAGER_INVITE_CODE = os.getenv("MANAGER_INVITE_CODE", "")
ADMIN_INVITE_CODE = os.getenv("ADMIN_INVITE_CODE", "")