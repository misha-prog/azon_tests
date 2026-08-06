import os

from dotenv import load_dotenv

load_dotenv()

MANAGER_INVITE_CODE = os.getenv("INVITE_CODE_MANAGER", "")
ADMIN_INVITE_CODE = os.getenv("INVITE_CODE_ADMIN", "")