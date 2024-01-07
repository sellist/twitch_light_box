import os

from twitchAPI.type import AuthScope
import dotenv

dotenv.load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
USER_SCOPE = [AuthScope.CHANNEL_READ_REDEMPTIONS]
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")