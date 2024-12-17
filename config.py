from os import getenv
from dotenv import load_dotenv

load_dotenv()

USER = getenv('SERVER_USER')
PASS = getenv('SERVER_PASS')
# SLACK_CHANNELS = getenv('CHANNELS')

# BOLAJI = getenv('BOLAJI')
# ALEJANDRO = getenv('ALEJANDRO')