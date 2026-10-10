from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
MAIL = getenv("USER_MAIL")
PEREK_API_KEY = getenv("PEREK_API_KEY")
