import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# NOTE : These variables are hardcoded on the CCDOCS server, there is no .env file

USER = getenv('CCDOCS_SERVER_USER')
PASS = getenv('CCDOCS_SERVER_PASS')

ROOFCON_USER = getenv('CORNERSTONE_USER')
ROOFCON_PASS = getenv('CORNERSTONE_PASS')

SLACK_CHANNELS = json.loads(getenv('CCDOCS_SLACK_CHANNELS', '{}'))
CORNERSTONE_SLACK_CHANNEL = getenv('CORNERSTONE_SLACK_CHANNEL')

BOLAJI = getenv('BOLAJI')
ALEJANDRO = getenv('ALEJANDRO')
SLACK_BOT = getenv('SLACKBOT')